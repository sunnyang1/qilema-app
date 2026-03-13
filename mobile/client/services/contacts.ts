import { apiClient } from '@/utils/api';

export interface EmergencyContact {
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

// 紧急联系人服务
export const contactsService = {
  /**
   * 获取紧急联系人列表
   */
  async getContacts(): Promise<EmergencyContact[]> {
    try {
      const response = await apiClient.get('/api/v1/emergency-contacts');
      return response.data;
    } catch (error) {
      console.error('获取紧急联系人列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取单个紧急联系人
   */
  async getContact(contactId: string): Promise<EmergencyContact> {
    try {
      const response = await apiClient.get(`/api/v1/emergency-contacts/${contactId}`);
      return response.data;
    } catch (error) {
      console.error('获取紧急联系人失败:', error);
      throw error;
    }
  },

  /**
   * 创建紧急联系人
   */
  async createContact(data: CreateContactDto): Promise<EmergencyContact> {
    try {
      const response = await apiClient.post('/api/v1/emergency-contacts', data);
      return response.data;
    } catch (error) {
      console.error('创建紧急联系人失败:', error);
      throw error;
    }
  },

  /**
   * 更新紧急联系人
   */
  async updateContact(contactId: string, data: UpdateContactDto): Promise<EmergencyContact> {
    try {
      const response = await apiClient.put(`/api/v1/emergency-contacts/${contactId}`, data);
      return response.data;
    } catch (error) {
      console.error('更新紧急联系人失败:', error);
      throw error;
    }
  },

  /**
   * 删除紧急联系人
   */
  async deleteContact(contactId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/emergency-contacts/${contactId}`);
    } catch (error) {
      console.error('删除紧急联系人失败:', error);
      throw error;
    }
  },

  /**
   * 设置默认联系人
   */
  async setDefaultContact(contactId: string): Promise<EmergencyContact> {
    try {
      const response = await apiClient.post(`/api/v1/emergency-contacts/${contactId}/set-default`);
      return response.data;
    } catch (error) {
      console.error('设置默认联系人失败:', error);
      throw error;
    }
  },
};
