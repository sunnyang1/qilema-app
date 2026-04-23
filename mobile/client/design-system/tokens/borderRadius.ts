/**
 * 圆角令牌 - Border Radius Tokens
 */
import { BorderRadiusScale } from '../types';

export const borderRadius: BorderRadiusScale = {
  xs: 4,     // 小标签、徽章
  sm: 8,     // 小按钮、输入框
  md: 12,    // 默认按钮、卡片
  lg: 16,    // 大卡片、模态框
  xl: 20,    // 特大卡片、底部面板
  '2xl': 24, // 全屏模态
  '3xl': 32, // 特殊展示卡片
  '4xl': 40, // 大型展示组件
  full: 9999,// 胶囊、圆形
};
