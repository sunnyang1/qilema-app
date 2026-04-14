import { apiClient } from '@/utils/api';
import { authService } from '@/services/auth';

/** 与 FastAPI ApiResponseBuilder.success 一致的外层结构 */
type ApiEnvelope<T> = { code: number; message: string; data: T; timestamp?: number };

function unwrap<T>(body: unknown): T {
  if (body !== null && typeof body === 'object' && 'data' in body) {
    return (body as ApiEnvelope<T>).data;
  }
  throw new Error('无效的 API 响应格式');
}

function normalizeChannels(raw: Record<string, unknown>): string[] {
  const n = raw.notify_channels ?? raw.notification_channels;
  if (Array.isArray(n)) {
    return n.map(String);
  }
  if (typeof n === 'string' && n.trim()) {
    return n.split(',').map((c) => c.trim()).filter(Boolean);
  }
  return [];
}

function mapContact(raw: Record<string, unknown>): EmergencyContact {
  const idNum = Number(raw.id);
  return {
    id: Number.isFinite(idNum) ? idNum : 0,
    contactId: String(raw.contact_id ?? raw.contactId ?? ''),
    userId: String(raw.user_id ?? raw.userId ?? ''),
    name: String(raw.name ?? raw.contact_name ?? ''),
    phone: String(raw.phone ?? ''),
    relationship: String(raw.relationship ?? raw.relation ?? ''),
    priority: Number(raw.priority ?? 1),
    notificationChannels: normalizeChannels(raw),
    isDefault: raw.is_primary === 1 || raw.is_primary === true,
    createdAt: String(raw.created_at ?? raw.createdAt ?? ''),
    updatedAt: String(raw.updated_at ?? raw.updatedAt ?? ''),
  };
}

export interface EmergencyContact {
  /** 数据库主键，对应 GET/PUT/DELETE `/api/v1/contacts/{id}` */
  id: number;
  contactId: string;
  userId: string;
  name: string;
  phone: string;
  relationship: string;
  priority: number;
  notificationChannels: string[];
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateContactDto {
  name: string;
  phone: string;
  relationship: string;
  priority: number;
  notificationChannels: string[];
  isDefault?: boolean;
}

export interface UpdateContactDto {
  name?: string;
  phone?: string;
  relationship?: string;
  priority?: number;
  notificationChannels?: string[];
  isDefault?: boolean;
}

const CONTACTS_BASE = '/api/v1/contacts';

export const contactsService = {
  async getContacts(): Promise<EmergencyContact[]> {
    try {
      const raw = await apiClient.get<
        ApiEnvelope<{ total: number; contacts: Record<string, unknown>[] }>
      >(`${CONTACTS_BASE}/`);
      const data = unwrap<{ total: number; contacts: Record<string, unknown>[] }>(raw);
      return (data.contacts ?? []).map((c) => mapContact(c));
    } catch (error) {
      console.error('获取紧急联系人列表失败:', error);
      throw error;
    }
  },

  /**
   * @param contactId 数据库主键 id 的字符串形式（与列表项 `contact.id` 一致）
   */
  async getContact(contactId: string): Promise<EmergencyContact> {
    try {
      const raw = await apiClient.get<ApiEnvelope<Record<string, unknown>>>(
        `${CONTACTS_BASE}/${encodeURIComponent(contactId)}`
      );
      return mapContact(unwrap(raw) as Record<string, unknown>);
    } catch (error) {
      console.error('获取紧急联系人失败:', error);
      throw error;
    }
  },

  async createContact(data: CreateContactDto): Promise<EmergencyContact> {
    try {
      const user = authService.getCurrentUser();
      const uid = user?.user_id ?? user?.id;
      if (!uid) {
        throw new Error('未登录，无法创建联系人');
      }
      const raw = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(`${CONTACTS_BASE}/`, {
        user_id: uid,
        contact_name: data.name,
        phone: data.phone,
        relationship: data.relationship,
        is_primary: data.isDefault ?? false,
        priority: data.priority,
      });
      return mapContact(unwrap(raw) as Record<string, unknown>);
    } catch (error) {
      console.error('创建紧急联系人失败:', error);
      throw error;
    }
  },

  async updateContact(contactId: string, data: UpdateContactDto): Promise<EmergencyContact> {
    try {
      const payload: Record<string, unknown> = {};
      if (data.name !== undefined) {
        payload.contact_name = data.name;
      }
      if (data.phone !== undefined) {
        payload.phone = data.phone;
      }
      if (data.relationship !== undefined) {
        payload.relationship = data.relationship;
      }
      if (data.priority !== undefined) {
        payload.priority = data.priority;
      }
      if (data.isDefault !== undefined) {
        payload.is_primary = data.isDefault;
      }
      const raw = await apiClient.put<ApiEnvelope<Record<string, unknown>>>(
        `${CONTACTS_BASE}/${encodeURIComponent(contactId)}`,
        payload
      );
      return mapContact(unwrap(raw) as Record<string, unknown>);
    } catch (error) {
      console.error('更新紧急联系人失败:', error);
      throw error;
    }
  },

  async deleteContact(contactId: string): Promise<void> {
    try {
      await apiClient.delete<ApiEnvelope<unknown>>(
        `${CONTACTS_BASE}/${encodeURIComponent(contactId)}`
      );
    } catch (error) {
      console.error('删除紧急联系人失败:', error);
      throw error;
    }
  },

  async setDefaultContact(contactId: string): Promise<EmergencyContact> {
    try {
      const raw = await apiClient.put<ApiEnvelope<Record<string, unknown>>>(
        `${CONTACTS_BASE}/${encodeURIComponent(contactId)}/set-primary`
      );
      return mapContact(unwrap(raw) as Record<string, unknown>);
    } catch (error) {
      console.error('设置默认联系人失败:', error);
      throw error;
    }
  },
};
