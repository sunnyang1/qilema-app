/**
 * 设计系统工具函数
 * Design System Utilities
 */
import { ColorValue } from 'react-native';
import { Theme, ColorTokens, TypographyVariant, ThemedStyle, ThemedStyles } from './types';

// ============================================================================
// 颜色工具
// ============================================================================

/**
 * 将 hex 颜色转换为 rgba
 * @param hex 十六进制颜色值 (#RGB, #RRGGBB, #RGBA, #RRGGBBAA)
 * @param alpha 透明度 (0-1)
 */
export function hexToRgba(hex: string, alpha: number): string {
  const sanitized = hex.replace('#', '');
  let r: number, g: number, b: number;

  if (sanitized.length === 3) {
    r = parseInt(sanitized[0] + sanitized[0], 16);
    g = parseInt(sanitized[1] + sanitized[1], 16);
    b = parseInt(sanitized[2] + sanitized[2], 16);
  } else if (sanitized.length === 4) {
    r = parseInt(sanitized[0] + sanitized[0], 16);
    g = parseInt(sanitized[1] + sanitized[1], 16);
    b = parseInt(sanitized[2] + sanitized[2], 16);
    alpha = parseInt(sanitized[3] + sanitized[3], 16) / 255;
  } else if (sanitized.length === 6) {
    r = parseInt(sanitized.substring(0, 2), 16);
    g = parseInt(sanitized.substring(2, 4), 16);
    b = parseInt(sanitized.substring(4, 6), 16);
  } else if (sanitized.length === 8) {
    r = parseInt(sanitized.substring(0, 2), 16);
    g = parseInt(sanitized.substring(2, 4), 16);
    b = parseInt(sanitized.substring(4, 6), 16);
    alpha = parseInt(sanitized.substring(6, 8), 16) / 255;
  } else {
    return hex;
  }

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * 调整颜色透明度
 * @param color 基础颜色（hex 或 rgba）
 * @param alpha 目标透明度 (0-1)
 */
export function alpha(color: string, alpha: number): string {
  if (color.startsWith('rgba')) {
    return color.replace(/[\d.]+\)$/, `${alpha})`);
  }
  if (color.startsWith('rgb')) {
    return color.replace('rgb', 'rgba').replace(')', `, ${alpha})`);
  }
  return hexToRgba(color, alpha);
}

/**
 * 获取颜色明度（0-255）
 * 用于判断应使用深色还是浅色文本
 */
export function getLuminance(hex: string): number {
  const sanitized = hex.replace('#', '');
  const r = parseInt(sanitized.substring(0, 2), 16);
  const g = parseInt(sanitized.substring(2, 4), 16);
  const b = parseInt(sanitized.substring(4, 6), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b);
}

/**
 * 根据背景色自动选择文本色（黑或白）
 * @param backgroundColor 背景色
 * @param threshold 明度阈值（默认 128）
 */
export function autoTextColor(backgroundColor: string, threshold = 128): string {
  return getLuminance(backgroundColor) > threshold ? '#000000' : '#FFFFFF';
}

// ============================================================================
// 间距工具
// ============================================================================

/**
 * 生成垂直或水平间距数组
 * 用于 FlatList 的 ItemSeparatorComponent
 */
export function spacer(size: number) {
  return { height: size };
}

export function spacerHorizontal(size: number) {
  return { width: size };
}

// ============================================================================
// 响应式工具
// ============================================================================

/**
 * 根据屏幕宽度选择值
 * @param width 当前屏幕宽度
 * @param values 断点对应的值
 */
export function responsive<T>(
  width: number,
  values: { xs?: T; sm?: T; md?: T; lg?: T; xl?: T; default: T }
): T {
  if (width >= 1280 && values.xl !== undefined) return values.xl;
  if (width >= 1024 && values.lg !== undefined) return values.lg;
  if (width >= 768 && values.md !== undefined) return values.md;
  if (width >= 414 && values.sm !== undefined) return values.sm;
  if (width >= 375 && values.xs !== undefined) return values.xs;
  return values.default;
}

// ============================================================================
// 样式工具
// ============================================================================

/**
 * 创建主题相关的 StyleSheet 样式
 * 配合 useThemedStyles 使用
 *
 * 示例：
 * const createStyles = (theme: Theme) => ({
 *   container: { padding: theme.spacing.lg },
 *   title: { ...theme.typography.h1, color: theme.colors.textPrimary },
 * });
 *
 * const styles = useThemedStyles(createStyles);
 */
export { ThemedStyle, ThemedStyles };

// ============================================================================
// 无障碍工具
// ============================================================================

/**
 * 计算两个颜色的对比度（WCAG 公式）
 * @returns 对比度比值（1-21）
 */
export function calculateContrastRatio(color1: string, color2: string): number {
  function getLuminanceValue(hex: string): number {
    const sanitized = hex.replace('#', '');
    const rsRGB = parseInt(sanitized.substring(0, 2), 16) / 255;
    const gsRGB = parseInt(sanitized.substring(2, 4), 16) / 255;
    const bsRGB = parseInt(sanitized.substring(4, 6), 16) / 255;

    const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
    const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
    const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  const l1 = getLuminanceValue(color1);
  const l2 = getLuminanceValue(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);

  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * 检查对比度是否满足 WCAG AA 标准
 */
export function meetsWCAGAA(
  textColor: string,
  backgroundColor: string,
  isLargeText = false
): boolean {
  const ratio = calculateContrastRatio(textColor, backgroundColor);
  return isLargeText ? ratio >= 3.0 : ratio >= 4.5;
}

/**
 * 检查对比度是否满足 WCAG AAA 标准
 */
export function meetsWCAGAAA(
  textColor: string,
  backgroundColor: string,
  isLargeText = false
): boolean {
  const ratio = calculateContrastRatio(textColor, backgroundColor);
  return isLargeText ? ratio >= 4.5 : ratio >= 7.0;
}
