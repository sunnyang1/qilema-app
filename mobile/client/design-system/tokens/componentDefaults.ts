/**
 * 组件默认样式 - Component Default Styles
 * 统一组件基础尺寸，确保视觉一致性
 */
import { ComponentDefaults } from '../types';

export const componentDefaults: ComponentDefaults = {
  button: {
    height: 48,           // 舒适触摸目标
    paddingHorizontal: 24,
    borderRadius: 12,
    gap: 8,
  },
  input: {
    height: 48,           // 舒适触摸目标
    paddingHorizontal: 16,
    borderRadius: 12,
    fontSize: 16,         // 不小于 16px 避免 iOS 缩放
    lineHeight: 24,
  },
  card: {
    borderRadius: 20,
    padding: 20,
  },
  listItem: {
    height: 64,           // 足够大的点击区域
    paddingHorizontal: 16,
    gap: 12,
  },
};
