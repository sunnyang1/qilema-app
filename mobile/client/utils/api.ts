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
  onResponseError?: (error: APIError) => Promise<APIError> | void;
}

// API 错误类型
export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public detail?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// 请求配置接口
export interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>;
  skipAuth?: boolean;
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

  // 处理响应
  private async handleResponse<T>(response: Response): Promise<T> {
    // 执行响应拦截器
    for (const interceptor of this.interceptors.response) {
      if (interceptor.onResponse) {
        response = await interceptor.onResponse(response);
      }
    }

    if (!response.ok) {
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }

      const error = new APIError(
        response.status,
        errorData.code || 'UNKNOWN_ERROR',
        errorData.message || errorData.detail || '请求失败',
        errorData.detail
      );

      // 执行响应错误拦截器
      for (const interceptor of this.interceptors.response) {
        if (interceptor.onResponseError) {
          const result = await interceptor.onResponseError(error);
          if (result) {
            throw result;
          }
        }
      }

      throw error;
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json() as Promise<T>;
    }

    return response.text() as unknown as Promise<T>;
  }

  // GET 请求
  async get<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'GET',
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response);
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
    return this.handleResponse<T>(response);
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
    return this.handleResponse<T>(response);
  }

  // DELETE 请求
  async delete<T>(path: string, config?: RequestConfig): Promise<T> {
    const url = this.buildURL(path, config?.params);
    const finalConfig = await this.handleRequest({
      ...config,
      method: 'DELETE',
    });

    const response = await fetch(url, finalConfig);
    return this.handleResponse<T>(response);
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
    return this.handleResponse<T>(response);
  }
}

// 导出单例
export const apiClient = new APIClient();
