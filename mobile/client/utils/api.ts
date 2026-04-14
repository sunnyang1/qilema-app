/**
 * API 客户端配置
 * 对应 Flutter 的 api_client.dart
 */
import { API_BASE_URL } from '@/constants/app';

// 请求拦截器类型
export interface RequestInterceptor {
  onRequest?: (config: RequestInit) => RequestInit | Promise<RequestInit>;
  onRequestError?: (error: Error) => void;
}

// 响应拦截器类型
export interface ResponseInterceptor {
  onResponse?: (response: Response) => Response | Promise<Response>;
  /** 返回 `Response` 表示错误已恢复（如刷新 token 后重试成功），将按成功响应解析 */
  onResponseError?: (error: APIError) => Promise<Response | void | undefined>;
}

/** 401 重试等场景下用于复现 fetch 的上下文（body 为 string / FormData 时可安全重试） */
export type APIErrorRequestContext = { url: string; init: RequestInit };

// API 错误类型
export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public detail?: any,
    public readonly requestContext?: APIErrorRequestContext
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * 将 FastAPI `detail` 转为单行可读文案。
 * - `str`：原样返回
 * - `list`（422 校验）：拼接各元素的 `msg`
 * - 其他：尽力字符串化
 */
function formatFastApiDetail(detail: unknown): string {
  if (detail == null || detail === '') {
    return '';
  }
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (item != null && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg?: unknown }).msg ?? '').trim();
        }
        if (typeof item === 'string') {
          return item.trim();
        }
        return '';
      })
      .filter(Boolean);
    return parts.length ? parts.join('；') : '';
  }
  if (typeof detail === 'object') {
    try {
      return JSON.stringify(detail);
    } catch {
      return '';
    }
  }
  return String(detail);
}

/** 错误响应体：优先使用后端已填的 `message`，否则从 `detail` 推导（兼容裸 FastAPI 与自定义封装） */
function messageFromErrorBody(errorData: Record<string, unknown>): string {
  const msg = errorData.message;
  if (typeof msg === 'string' && msg.trim()) {
    return msg.trim();
  }
  const fromDetail = formatFastApiDetail(errorData.detail);
  if (fromDetail) {
    return fromDetail;
  }
  return '请求失败';
}

function errorCodeFromBody(errorData: Record<string, unknown>): string {
  const c = errorData.code ?? errorData.error_code;
  return typeof c === 'string' && c ? c : 'UNKNOWN_ERROR';
}

/** 从失败响应构造 APIError（供客户端内部与 401 重试失败路径复用） */
export async function apiErrorFromResponse(
  response: Response,
  requestContext?: APIErrorRequestContext
): Promise<APIError> {
  let errorData: Record<string, unknown>;
  try {
    errorData = (await response.json()) as Record<string, unknown>;
  } catch {
    errorData = { message: response.statusText };
  }

  return new APIError(
    response.status,
    errorCodeFromBody(errorData),
    messageFromErrorBody(errorData),
    errorData.detail !== undefined ? errorData.detail : errorData,
    requestContext
  );
}

// 请求配置接口
export interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>;
  skipAuth?: boolean;
  /** 由 401 刷新后自动重试设置，防止无限刷新 */
  retriedAfter401?: boolean;
}

// API 客户端类
class APIClient {
  private baseURL: string;
  private interceptors: {
    request: RequestInterceptor[];
    response: ResponseInterceptor[];
  } = {
    request: [],
    response: [],
  };

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // 添加请求拦截器
  addRequestInterceptor(interceptor: RequestInterceptor) {
    this.interceptors.request.push(interceptor);
  }

  // 添加响应拦截器
  addResponseInterceptor(interceptor: ResponseInterceptor) {
    this.interceptors.response.push(interceptor);
  }

  // 构建 URL
  private buildURL(path: string, params?: Record<string, string | number | boolean>): string {
    let url = `${this.baseURL}${path}`;

    if (params) {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        query.append(key, String(value));
      });
      const queryString = query.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    return url;
  }

  // 处理请求
  private async handleRequest(config: RequestConfig): Promise<RequestInit> {
    let finalConfig = { ...config };

    // 执行请求拦截器
    for (const interceptor of this.interceptors.request) {
      if (interceptor.onRequest) {
        try {
          finalConfig = await interceptor.onRequest(finalConfig);
        } catch (error) {
          if (interceptor.onRequestError) {
            interceptor.onRequestError(error as Error);
          }
          throw error;
        }
      }
    }

    return finalConfig;
  }

  private async parseSuccessBody<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json() as Promise<T>;
    }

    return response.text() as unknown as Promise<T>;
  }

  // 处理响应
  private async handleResponse<T>(
    response: Response,
    requestContext?: APIErrorRequestContext
  ): Promise<T> {
    // 执行响应拦截器
    for (const interceptor of this.interceptors.response) {
      if (interceptor.onResponse) {
        response = await interceptor.onResponse(response);
      }
    }

    if (!response.ok) {
      const error = await apiErrorFromResponse(response, requestContext);

      // 执行响应错误拦截器
      for (const interceptor of this.interceptors.response) {
        if (interceptor.onResponseError) {
          const result = await interceptor.onResponseError(error);
          if (result instanceof Response) {
            let recovered = result;
            for (const intr of this.interceptors.response) {
              if (intr.onResponse) {
                recovered = await intr.onResponse(recovered);
              }
            }
            if (!recovered.ok) {
              throw await apiErrorFromResponse(recovered, requestContext);
            }
            return this.parseSuccessBody<T>(recovered);
          }
        }
      }

      throw error;
    }

    return this.parseSuccessBody<T>(response);
  }

  // GET 请求
  async get<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'GET',
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }

  // POST 请求
  async post<T>(path: string, data?: any, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...config?.headers,
      },
      body: JSON.stringify(data),
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }

  /**
   * POST application/x-www-form-urlencoded（如 OAuth2 密码流 `/auth/login`）
   */
  async postUrlEncoded<T>(path: string, body: Record<string, string>, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const params = new URLSearchParams();
    Object.entries(body).forEach(([k, v]) => params.append(k, v));
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...config?.headers,
      },
      body: params.toString(),
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }

  // PUT 请求
  async put<T>(path: string, data?: any, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...config?.headers,
      },
      body: JSON.stringify(data),
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }

  // DELETE 请求
  async delete<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'DELETE',
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }

  // 上传文件
  async upload<T>(path: string, formData: FormData, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'POST',
      body: formData,
      // 不设置 Content-Type，让浏览器自动设置 multipart/form-data
      headers: {
        ...config?.headers,
      },
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response, { url, init: finalConfig });
  }
}

// 导出单例
export const apiClient = new APIClient();
