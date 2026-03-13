/**
 * 认证服务
 * 对应 Flutter 的 auth_service.dart
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient, APIError } from '@/utils/api';
import { StorageKeys } from '@/constants/app';

// 用户信息接口
export interface UserInfo {
  id: string;
  username: string;
  email?: string;
  phone?: string;
  avatar?: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: UserInfo;
}

// 注册请求
export interface RegisterRequest {
  username: string;
  password: string;
  phone?: string;
  email?: string;
}

// 登录请求
export interface LoginRequest {
  username: string;
  password: string;
}

// Token 存储键
const ACCESS_TOKEN_KEY = StorageKeys.ACCESS_TOKEN;
const REFRESH_TOKEN_KEY = StorageKeys.REFRESH_TOKEN;
const USER_INFO_KEY = StorageKeys.USER_INFO;
const IS_LOGGED_IN_KEY = StorageKeys.IS_LOGGED_IN;

class AuthService {
  private accessToken: string | null = null;
  private userInfo: UserInfo | null = null;

  constructor() {
    this.init();
  }

  // 初始化：从本地存储加载 token
  private async init() {
    try {
      const [token, userInfo, isLoggedIn] = await Promise.all([
        AsyncStorage.getItem(ACCESS_TOKEN_KEY),
        AsyncStorage.getItem(USER_INFO_KEY),
        AsyncStorage.getItem(IS_LOGGED_IN_KEY),
      ]);

      this.accessToken = token;
      if (userInfo) {
        this.userInfo = JSON.parse(userInfo);
      }
    } catch (error) {
      console.error('Failed to load auth data:', error);
    }
  }

  // 检查是否已登录
  async isLoggedIn(): Promise<boolean> {
    try {
      const isLoggedIn = await AsyncStorage.getItem(IS_LOGGED_IN_KEY);
      return isLoggedIn === 'true' && !!this.accessToken;
    } catch {
      return false;
    }
  }

  // 获取当前用户
  getCurrentUser(): UserInfo | null {
    return this.userInfo;
  }

  // 获取访问令牌
  getAccessToken(): string | null {
    return this.accessToken;
  }

  // 登录
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      '/api/v1/auth/login',
      data,
      { skipAuth: true }
    );

    await this.saveAuthData(response);
    return response;
  }

  // 注册
  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      '/api/v1/auth/register',
      data,
      { skipAuth: true }
    );

    await this.saveAuthData(response);
    return response;
  }

  // 刷新令牌
  async refreshToken(): Promise<LoginResponse> {
    const refreshToken = await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      throw new APIError(401, 'NO_REFRESH_TOKEN', '未找到刷新令牌');
    }

    const response = await apiClient.post<LoginResponse>(
      '/api/v1/auth/refresh',
      { refresh_token: refreshToken },
      { skipAuth: true }
    );

    await this.saveAuthData(response);
    return response;
  }

  // 登出
  async logout(): Promise<void> {
    try {
      // 调用登出 API
      await apiClient.post('/api/v1/auth/logout', {});
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      // 清除本地存储
      await this.clearAuthData();
    }
  }

  // 保存认证数据
  private async saveAuthData(data: LoginResponse): Promise<void> {
    try {
      this.accessToken = data.access_token;
      this.userInfo = data.user;

      await Promise.all([
        AsyncStorage.setItem(ACCESS_TOKEN_KEY, data.access_token),
        AsyncStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token),
        AsyncStorage.setItem(USER_INFO_KEY, JSON.stringify(data.user)),
        AsyncStorage.setItem(IS_LOGGED_IN_KEY, 'true'),
      ]);
    } catch (error) {
      console.error('Failed to save auth data:', error);
      throw error;
    }
  }

  // 清除认证数据
  private async clearAuthData(): Promise<void> {
    try {
      this.accessToken = null;
      this.userInfo = null;

      await Promise.all([
        AsyncStorage.removeItem(ACCESS_TOKEN_KEY),
        AsyncStorage.removeItem(REFRESH_TOKEN_KEY),
        AsyncStorage.removeItem(USER_INFO_KEY),
        AsyncStorage.removeItem(IS_LOGGED_IN_KEY),
      ]);
    } catch (error) {
      console.error('Failed to clear auth data:', error);
    }
  }
}

// 导出单例
export const authService = new AuthService();
