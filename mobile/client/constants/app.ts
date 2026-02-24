/**
 * 应用常量配置
 * 对应 Flutter 的 app_constants.dart
 */

// 应用信息
export const APP_NAME = '起了吗';
export const APP_VERSION = '1.0.0';

// API 配置
export const API_BASE_URL = process.env.EXPO_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

// 路由名称
export const Routes = {
  // 认证
  LOGIN: 'login',
  REGISTER: 'register',

  // 主要功能
  HOME: 'home',
  HISTORY: 'history',
  SOS: 'sos',
  SOS_STATUS: 'sos-status',

  // 联系人
  CONTACTS: 'contacts',
  CONTACT_EDIT: 'contact-edit',

  // 健康
  HEALTH: 'health',
  MEDICAL_HISTORIES: 'medical-histories',
  MEDICATIONS: 'medications',
  ALLERGIES: 'allergies',

  // 设备
  DEVICES: 'devices',
  DEVICE_DATA: 'device-data',

  // 紧急
  AED_MAP: 'aed-map',
  HOSPITALS: 'hospitals',

  // 知识库
  KNOWLEDGE: 'knowledge',
  KNOWLEDGE_ARTICLES: 'knowledge-articles',
  ARTICLE_DETAIL: 'article-detail',

  // 用药提醒
  MEDICATION_REMINDERS: 'medication',
  MEDICATION_ADD: 'medication-add',
} as const;

// API 端点
export const API = {
  // 认证
  LOGIN: '/api/v1/auth/login',
  REGISTER: '/api/v1/auth/register',
  REFRESH_TOKEN: '/api/v1/auth/refresh',
  LOGOUT: '/api/v1/auth/logout',

  // 签到
  CHECKINS: '/api/v1/checkins',
  CHECKINS_HISTORY: '/api/v1/checkins/history',
  CHECKINS_STATS: '/api/v1/checkins/stats',
  CHECKINS_STATUS: '/api/v1/checkins/status',
  CHECKINS_TODAY: '/api/v1/checkins/today',

  // SOS
  SOS: '/api/v1/sos',
  SOS_BY_ID: (id: string) => `/api/v1/sos/${id}`,
  SOS_CANCEL: (id: string) => `/api/v1/sos/${id}/cancel`,
  SOS_RESOLVE: (id: string) => `/api/v1/sos/${id}/resolve`,

  // 联系人
  CONTACTS: '/api/v1/contacts',
  CONTACT_BY_ID: (id: string) => `/api/v1/contacts/${id}`,
  CONTACT_SET_PRIMARY: (id: string) => `/api/v1/contacts/${id}/set-primary`,

  // 健康
  HEALTH_RECORDS: '/api/v1/health-records',
  HEALTH_RECORD_BY_ID: (userId: string) => `/api/v1/health-records/${userId}`,
  MEDICAL_HISTORIES: '/api/v1/health-records/medical-histories',
  MEDICATIONS: '/api/v1/health-records/medications',
  ALLERGIES: '/api/v1/health-records/allergies',

  // 设备
  DEVICES: '/api/v1/devices',
  DEVICE_BIND: '/api/v1/devices/bind',
  DEVICE_DATA: (id: string) => `/api/v1/devices/${id}/data`,

  // 紧急
  AED_LOCATIONS: '/api/v1/emergency/aed',
  HOSPITALS: '/api/v1/emergency/hospitals',

  // 知识库
  KNOWLEDGE_CATEGORIES: '/api/v1/knowledge/categories',
  KNOWLEDGE_ARTICLES: '/api/v1/knowledge/articles',
  ARTICLE_BY_CATEGORY: (categoryId: string) => `/api/v1/knowledge/categories/${categoryId}/articles`,
  ARTICLE_BY_ID: (id: string) => `/api/v1/knowledge/articles/${id}`,

  // 用药提醒
  MEDICATION_REMINDERS: '/api/v1/medications',
  MEDICATION_REMINDER_BY_ID: (id: string) => `/api/v1/medications/${id}`,
} as const;

// 存储键名
export const StorageKeys = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  IS_LOGGED_IN: 'is_logged_in',
} as const;

// 加载状态
export enum LoadingState {
  IDLE = 'idle',
  LOADING = 'loading',
  SUCCESS = 'success',
  ERROR = 'error',
}

// Toast 持续时间（毫秒）
export const TOAST_DURATION = {
  SHORT: 2000,
  MEDIUM: 3000,
  LONG: 4000,
} as const;

// 分页配置
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  DEFAULT_PAGE: 1,
} as const;

// 权限类型
export enum Permission {
  LOCATION = 'location',
  CAMERA = 'camera',
  PHOTO_LIBRARY = 'photoLibrary',
  NOTIFICATIONS = 'notifications',
  CONTACTS = 'contacts',
}

// 地图配置
export const MAP_CONFIG = {
  DEFAULT_ZOOM: 15,
  MIN_ZOOM: 3,
  MAX_ZOOM: 19,
  DEFAULT_CENTER: {
    latitude: 39.9042, // 北京
    longitude: 116.4074,
  },
} as const;
