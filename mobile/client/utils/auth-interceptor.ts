/**
 * 认证拦截器
 * 自动为请求添加 Authorization 头
 */
import { apiClient, APIError, apiErrorFromResponse, type RequestConfig } from '@/utils/api';
import { authService } from '@/services/auth';

function mergeAuthorizationHeader(headers: HeadersInit | undefined, token: string | null): Headers {
  const h = new Headers(headers as HeadersInit | undefined);
  if (token) {
    h.set('Authorization', `Bearer ${token}`);
  } else {
    h.delete('Authorization');
  }
  return h;
}

// 认证拦截器
apiClient.addRequestInterceptor({
  onRequest: async (config) => {
    // 如果请求标记为跳过认证，直接返回
    if ((config as RequestConfig).skipAuth) {
      return config;
    }

    // 获取访问令牌
    const token = authService.getAccessToken();

    // 如果存在令牌，添加到请求头
    if (token) {
      return {
        ...config,
        headers: mergeAuthorizationHeader(config.headers as HeadersInit | undefined, token),
      };
    }

    return config;
  },
  onRequestError: (error) => {
    console.error('Request interceptor error:', error);
  },
});

// 响应拦截器：处理 401 错误和令牌刷新
apiClient.addResponseInterceptor({
  onResponse: async (response) => {
    return response;
  },
  onResponseError: async (error: APIError) => {
    if (error.status !== 401) {
      throw error;
    }

    // 未持有 access token 时的 401（如登录密码错误）：不得走刷新，避免递归与误清 session
    if (!authService.getAccessToken()) {
      throw error;
    }

    const ctx = error.requestContext;
    if (!ctx) {
      throw error;
    }

    const { url, init } = ctx;
    if ((init as RequestConfig).retriedAfter401) {
      await authService.logout();
      throw error;
    }

    try {
      console.log('Access token expired, refreshing...');
      await authService.refreshToken();
      const token = authService.getAccessToken();
      if (!token) {
        await authService.logout();
        throw error;
      }

      const retryInit: RequestConfig = {
        ...init,
        headers: mergeAuthorizationHeader(init.headers as HeadersInit | undefined, token),
        retriedAfter401: true,
      };

      const retryResponse = await fetch(url, retryInit);

      if (retryResponse.ok) {
        return retryResponse;
      }

      if (retryResponse.status === 401) {
        await authService.logout();
        throw error;
      }

      throw await apiErrorFromResponse(retryResponse, { url, init: retryInit });
    } catch (e) {
      if (e instanceof APIError) {
        throw e;
      }
      console.error('Failed to refresh token:', e);
      await authService.logout();
      console.warn('Token refresh failed, user logged out');
      throw error;
    }
  },
});
