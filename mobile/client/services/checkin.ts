import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient } from '@/utils/api';

// 签到记录类型
export interface CheckIn {
  id: string;
  userId: string;
  checkInTime: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  status: 'completed' | 'missed' | 'pending';
}

export interface CheckInStats {
  consecutiveDays: number;
  totalCheckIns: number;
  lastCheckInTime?: string;
  todayChecked: boolean;
}

const STORAGE_KEY = 'checkin_data';

// 签到服务
export const checkInService = {
  /**
   * 完成签到
   */
  async checkIn(location?: { latitude: number; longitude: number }): Promise<CheckIn> {
    try {
      const data = await apiClient.post<CheckIn>('/api/v1/checkins', {
        location,
        timestamp: new Date().toISOString(),
      });

      // 缓存签到数据
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(data));

      return data;
    } catch (error) {
      console.error('签到失败:', error);
      throw error;
    }
  },

  /**
   * 获取签到历史
   */
  async getCheckInHistory(page = 1, pageSize = 20): Promise<CheckIn[]> {
    try {
      return apiClient.get<CheckIn[]>(
        `/api/v1/checkins/history?page=${page}&pageSize=${pageSize}`
      );
    } catch (error) {
      console.error('获取签到历史失败:', error);
      throw error;
    }
  },

  /**
   * 获取签到统计
   */
  async getCheckInStats(): Promise<CheckInStats> {
    try {
      const stats = await apiClient.get<CheckInStats>('/api/v1/checkins/stats');

      // 尝试从缓存读取
      const cachedData = await AsyncStorage.getItem(STORAGE_KEY);
      if (cachedData) {
        const parsed = JSON.parse(cachedData) as CheckIn;
        return {
          ...stats,
          lastCheckInTime: parsed.checkInTime,
          todayChecked: stats.todayChecked || false,
        };
      }

      return stats;
    } catch (error) {
      console.error('获取签到统计失败:', error);
      throw error;
    }
  },

  /**
   * 检查今天是否已签到
   */
  async isCheckedInToday(): Promise<boolean> {
    try {
      const stats = await this.getCheckInStats();
      return stats.todayChecked;
    } catch (error) {
      console.error('检查签到状态失败:', error);
      return false;
    }
  },

  /**
   * 清除缓存
   */
  async clearCache(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('清除缓存失败:', error);
    }
  },
};
