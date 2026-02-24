/**
 * 认证拦截器
 * 自动为请求添加 Authorization 头
 */
import { apiClient, APIError } from '@/utils/api';
import { authService } from '@/services/auth';

// 认证拦截器
apiClient.addRequestInterceptor({
  onRequest: async (config) => {
    // 如果请求标记为跳过认证，直接返回
    if ((config as any).skipAuth) {
      return config;
    }

    // 获取访问令牌
    const token = authService.getAccessToken();

    // 如果存在令牌，添加到请求头
    if (token) {
      return {
        ...config,
        headers: {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        },
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
    // 如果是 401 错误，尝试刷新令牌
    if (error.status === 401) {
      try {
        console.log('Access token expired, refreshing...');
        await authService.refreshToken();

        // 重试原请求
        const originalRequest = (error as any).config;
        if (originalRequest && originalRequest.url && originalRequest.method) {
          // 重新发起请求
          const retryResponse = await fetch(originalRequest.url, {
            ...originalRequest,
            headers: {
              ...originalRequest.headers,
              Authorization: `Bearer ${authService.getAccessToken()}`,
            },
          });

          if (retryResponse.ok) {
            const contentType = retryResponse.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
              return retryResponse.json();
            }
            return retryResponse.text();
          }
        }
      } catch (refreshError) {
        console.error('Failed to refresh token:', refreshError);

        // 刷新失败，清除认证数据并跳转到登录页
        await authService.logout();

        // 注意：这里需要在导航时处理
        // 可以通过事件或全局状态通知需要跳转到登录页
        console.warn('Token refresh failed, user logged out');
      }
    }

    throw error;
  },
});
