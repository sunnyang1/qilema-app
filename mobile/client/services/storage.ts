/**
 * 本地存储服务
 * 封装 AsyncStorage，提供类型安全的存储接口
 */
import AsyncStorage from '@react-native-async-storage/async-storage';

export const storage = {
  /**
   * 获取存储项
   */
  async getItem<T>(key: string): Promise<T | null> {
    try {
      const value = await AsyncStorage.getItem(key);
      return value ? (JSON.parse(value) as T) : null;
    } catch (error) {
      console.error(`[Storage] Failed to get item ${key}:`, error);
      return null;
    }
  },

  /**
   * 设置存储项
   */
  async setItem<T>(key: string, value: T): Promise<void> {
    try {
      await AsyncStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`[Storage] Failed to set item ${key}:`, error);
    }
  },

  /**
   * 移除存储项
   */
  async removeItem(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error(`[Storage] Failed to remove item ${key}:`, error);
    }
  },
};
