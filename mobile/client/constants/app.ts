/**
 * 应用常量配置
 * 对应 Flutter 的 app_constants.dart
 */

// 应用信息
export const APP_NAME = '起了吗';
export const APP_VERSION = '1.0.0';

// API 配置
export const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

// 存储键名
export const StorageKeys = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  IS_LOGGED_IN: 'is_logged_in',
} as const;
