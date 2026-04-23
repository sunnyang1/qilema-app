/**
 * 认证服务
 * 对应 Flutter 的 auth_service.dart
 *
 * 后端统一使用 ApiResponseBuilder：`{ code, message, data, timestamp }`；
 * 登录接口为 OAuth2 密码流（form-urlencoded），见 `apiClient.postUrlEncoded`。
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient, APIError } from '@/utils/api';
import { StorageKeys } from '@/constants/app';
import { ApiEnvelope, unwrapData } from '@/services/types';

// 用户信息接口（与后端 `/auth/login` 返回的 user 对象对齐）
export interface UserInfo {
  /** 后端 users.user_id */
  user_id: string;
  /** 与 user_id 相同，兼容旧代码中的 `id` */
  id: string;
  username: string;
  phone?: string;
  nickname?: string;
  email?: string;
  avatar?: string;
}

function normalizeUser(raw: Record<string, unknown> | null | undefined): UserInfo {
  if (!raw) {
    return { user_id: '', id: '', username: '' };
  }
  const uid = String(raw.user_id ?? raw.id ?? '');
  const phone = raw.phone != null ? String(raw.phone) : undefined;
  return {
    user_id: uid,
    id: uid,
    username: phone ?? uid,
    phone,
    nickname: raw.nickname != null ? String(raw.nickname) : undefined,
    email: raw.email as string | undefined,
    avatar: raw.avatar as string | undefined,
  };
}

// 登录响应（客户端内部统一形状；后端登录无 refresh_token 时填空串）
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
      const [token, userInfo] = await Promise.all([
        AsyncStorage.getItem(ACCESS_TOKEN_KEY),
        AsyncStorage.getItem(USER_INFO_KEY),
      ]);

      this.accessToken = token;
      if (userInfo) {
        const parsed = JSON.parse(userInfo) as UserInfo;
        this.userInfo = this.migrateLegacyUser(parsed);
      }
    } catch (error) {
      console.error('Failed to load auth data:', error);
    }
  }

  /** 兼容早期仅存 `id`、无 `user_id` 的缓存 */
  private migrateLegacyUser(u: UserInfo): UserInfo {
    const uid = u.user_id || u.id || '';
    return {
      ...u,
      user_id: uid,
      id: uid,
      username: u.username || u.phone || uid,
    };
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
    const raw = await apiClient.postUrlEncoded<
      ApiEnvelope<{
        access_token: string;
        token_type: string;
        user: Record<string, unknown>;
      }>
    >(
      '/api/v1/auth/login',
      { username: data.username, password: data.password },
      { skipAuth: true }
    );

    const d = unwrapData<{
      access_token: string;
      token_type: string;
      user: Record<string, unknown>;
    }>(raw);

    const result: LoginResponse = {
      access_token: d.access_token,
      refresh_token: '',
      user: normalizeUser(d.user),
    };

    await this.saveAuthData(result);
    return result;
  }

  // 注册（成功后自动登录）
  async register(data: RegisterRequest): Promise<LoginResponse> {
    const raw = await apiClient.post<ApiEnvelope<{ user_id: string }>>(
      '/api/v1/auth/register',
      {
        phone: data.username,
        password: data.password,
        name: data.username,
      },
      { skipAuth: true }
    );

    unwrapData(raw);
    return this.login({ username: data.username, password: data.password });
  }

  // 刷新令牌（需已有 access token；后端按 CurrentUser 签发新 token）
  async refreshToken(): Promise<LoginResponse> {
    const raw = await apiClient.post<ApiEnvelope<{ access_token: string; token_type: string }>>(
      '/api/v1/auth/refresh',
      {}
    );
    const d = unwrapData<{ access_token: string; token_type: string }>(raw);

    this.accessToken = d.access_token;
    await AsyncStorage.setItem(ACCESS_TOKEN_KEY, d.access_token);

    const user = this.userInfo;
    if (!user) {
      throw new APIError(401, 'NO_USER', '缺少用户信息，请重新登录');
    }

    const refreshTok = (await AsyncStorage.getItem(REFRESH_TOKEN_KEY)) || '';
    const result: LoginResponse = {
      access_token: d.access_token,
      refresh_token: refreshTok,
      user,
    };
    await AsyncStorage.setItem(USER_INFO_KEY, JSON.stringify(user));
    return result;
  }

  // 登出
  async logout(): Promise<void> {
    try {
      await apiClient.post<ApiEnvelope<unknown>>('/api/v1/auth/logout', {});
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
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
