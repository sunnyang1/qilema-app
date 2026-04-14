import { apiClient } from '@/utils/api';
import { contactsService } from '@/services/contacts';
import * as Location from 'expo-location';

// SOS 请求状态
export type SOSStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface SOSRequest {
  id: string;
  userId: string;
  status: SOSStatus;
  location?: {
    latitude: number;
    longitude: number;
  };
  locationAddress?: string;
  createdAt: string;
  updatedAt: string;
  contactsNotified: number[];
  emergencyServicesNotified: boolean;
}

export interface EmergencyContact {
  id: string;
  name: string;
  relation: string;
  phone: string;
  email?: string;
  priority: number;
  isDefault: boolean;
}

const STORAGE_KEY = 'sos_current_request';

// SOS 服务
export const sosService = {
  /**
   * 请求当前位置权限
   */
  async requestLocationPermission(): Promise<boolean> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('请求位置权限失败:', error);
      return false;
    }
  },

  /**
   * 获取当前位置
   */
  async getCurrentLocation(): Promise<{ latitude: number; longitude: number; address?: string } | null> {
    try {
      const hasPermission = await this.requestLocationPermission();
      if (!hasPermission) {
        throw new Error('位置权限未授权');
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      const { latitude, longitude } = location.coords;

      // 尝试获取地址
      let address: string | undefined;
      try {
        const addressResults = await Location.reverseGeocodeAsync({ latitude, longitude });
        if (addressResults.length > 0) {
          const addr = addressResults[0];
          address = `${addr.street || ''} ${addr.city || ''} ${addr.region || ''}`.trim();
        }
      } catch (error) {
        console.error('获取地址失败:', error);
      }

      return { latitude, longitude, address };
    } catch (error) {
      console.error('获取位置失败:', error);
      return null;
    }
  },

  /**
   * 发起 SOS 求助
   */
  async createSOSRequest(): Promise<SOSRequest> {
    try {
      // 获取位置
      const location = await this.getCurrentLocation();

      // 发送请求到后端
      const data = await apiClient.post<SOSRequest>('/api/v1/sos-requests', {
        location: location ? { latitude: location.latitude, longitude: location.longitude } : undefined,
        locationAddress: location?.address,
      });

      // 缓存当前 SOS 请求
      await this.cacheCurrentRequest(data);

      return data;
    } catch (error) {
      console.error('发起 SOS 求助失败:', error);
      throw error;
    }
  },

  /**
   * 获取紧急联系人列表
   */
  async getEmergencyContacts(): Promise<EmergencyContact[]> {
    try {
      const list = await contactsService.getContacts();
      return list.map((c) => ({
        id: c.contactId,
        name: c.name,
        relation: c.relationship,
        phone: c.phone,
        priority: c.priority,
        isDefault: c.isDefault,
      }));
    } catch (error) {
      console.error('获取紧急联系人列表失败:', error);
      throw error;
    }
  },

  /**
   * 拨打联系人电话
   */
  async callContact(contactId: string): Promise<void> {
    try {
      const result = await apiClient.post<{ phone?: string }>(
        `/api/v1/emergency-contacts/${contactId}/call`
      );
      if (result?.phone) {
        console.log(`拨打联系人电话: ${result.phone}`);
      }
    } catch (error) {
      console.error('拨打联系人电话失败:', error);
      throw error;
    }
  },

  /**
   * 拨打 120 急救电话
   */
  async callEmergencyServices(): Promise<void> {
    try {
      await apiClient.post('/api/v1/emergency-services/call');
      // 模拟拨打 120
      console.log('拨打 120 急救电话');
      // Linking.openURL('tel:120');
    } catch (error) {
      console.error('拨打急救电话失败:', error);
      throw error;
    }
  },

  /**
   * 获取当前 SOS 请求状态
   */
  async getCurrentSOSStatus(): Promise<SOSRequest | null> {
    try {
      // 先从缓存读取
      const cached = await this.getCachedRequest();
      if (cached) {
        return cached;
      }

      const data = await apiClient.get<SOSRequest | null>('/api/v1/sos-requests/current');
      if (data) {
        await this.cacheCurrentRequest(data);
      }
      return data;
    } catch (error) {
      console.error('获取 SOS 状态失败:', error);
      return null;
    }
  },

  /**
   * 取消 SOS 请求
   */
  async cancelSOSRequest(): Promise<void> {
    try {
      const currentRequest = await this.getCurrentSOSStatus();
      if (currentRequest) {
        await apiClient.post(`/api/v1/sos-requests/${currentRequest.id}/cancel`);
        await this.clearCache();
      }
    } catch (error) {
      console.error('取消 SOS 请求失败:', error);
      throw error;
    }
  },

  /**
   * 缓存当前 SOS 请求
   */
  async cacheCurrentRequest(request: SOSRequest): Promise<void> {
    try {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(request));
    } catch (error) {
      console.error('缓存 SOS 请求失败:', error);
    }
  },

  /**
   * 获取缓存的 SOS 请求
   */
  async getCachedRequest(): Promise<SOSRequest | null> {
    try {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      const cached = await AsyncStorage.getItem(STORAGE_KEY);
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      console.error('获取缓存失败:', error);
      return null;
    }
  },

  /**
   * 清除缓存
   */
  async clearCache(): Promise<void> {
    try {
      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
      await AsyncStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('清除缓存失败:', error);
    }
  },
};
