/**
 * 布局令牌 - Layout Tokens
 * 触摸目标、断点、层级等布局相关常量
 */
import { TouchTargetTokens, HitSlopTokens, BreakpointTokens, ZIndexTokens } from '../types';

/**
 * 触摸目标尺寸
 * WCAG 2.1 要求最小 44x44dp，推荐 48x48dp
 */
export const touchTarget: TouchTargetTokens = {
  minimum: 44,     // WCAG 2.1 最低标准
  comfortable: 48, // 推荐舒适尺寸（Material Design 标准）
  large: 56,       // 大按钮、导航项（适合老年人）
};

/**
 * HitSlop 扩展区域
 * 用于扩大触摸响应区域而不改变视觉尺寸
 */
export const hitSlop: HitSlopTokens = {
  none: 0,
  small: 8,
  medium: 12,
  large: 16,
  extraLarge: 20,
};

/**
 * 响应式断点（基于逻辑像素宽度）
 */
export const breakpoints: BreakpointTokens = {
  xs: 375,  // 小屏手机（iPhone SE/mini）
  sm: 414,  // 标准手机（iPhone 14/15）
  md: 768,  // 平板竖屏（iPad mini）
  lg: 1024, // 平板横屏（iPad）
  xl: 1280, // 大平板/桌面
};

/**
 * Z-Index 层级系统
 */
export const zIndex: ZIndexTokens = {
  modal: 1000,    // 模态框、全屏覆盖
  dropdown: 900,  // 下拉菜单、选择器
  sticky: 800,    // 吸顶元素
  header: 700,    // 导航栏
  toast: 600,     // Toast 提示
  popover: 300,   // 气泡弹窗
  tooltip: 200,   // 工具提示
  overlay: 100,   // 遮罩层
  default: 1,     // 默认层级
};
