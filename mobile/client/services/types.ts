/**
 * 服务层共享类型
 *
 * 所有 service 文件通用的类型定义集中在此处，
 * 避免在 auth.ts / contacts.ts / sos.ts 等文件中重复声明。
 */

/** FastAPI ApiResponseBuilder 外层结构 */
export interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
  timestamp?: number;
}

/** 从 ApiEnvelope 中提取 data 字段，若格式不符则抛错 */
export function unwrapData<T>(body: unknown): T {
  if (body !== null && typeof body === 'object' && 'data' in body) {
    return (body as ApiEnvelope<T>).data;
  }
  throw new Error('无效的 API 响应格式');
}

/**
 * 紧急联系人（统一接口）
 *
 * 合并自 contacts.ts（11 字段完整版）和 sos.ts（7 字段精简版）。
 * - contacts.ts 作为主数据源提供全部字段
 * - sos.ts 通过此接口直接使用，不再需要手动映射
 */
export interface EmergencyContact {
  /** 数据库主键，对应 GET/PUT/DELETE `/api/v1/contacts/{id}` */
  id: number;
  /** 业务 ID（UUID） */
  contactId: string;
  /** 所属用户 ID */
  userId: string;
  /** 姓名 */
  name: string;
  /** 电话 */
  phone: string;
  /** 关系（如"父母"、"配偶"等） */
  relationship: string;
  /** 优先级（数字越小优先级越高） */
  priority: number;
  /** 通知渠道列表 */
  notificationChannels: string[];
  /** 是否为默认联系人 */
  isDefault: boolean;
  /** 创建时间（ISO 字符串） */
  createdAt: string;
  /** 更新时间（ISO 字符串） */
  updatedAt: string;
}
