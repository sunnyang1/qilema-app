/**
 * Theme 类型定义
 * 为主题系统提供完整的 TypeScript 类型支持
 */

import { TextStyle, ViewStyle } from 'react-native';

// ============ 颜色类型 ============

/** 主题颜色 */
export interface ThemeColors {
  // 主色调
  primary: string;
  primaryLight: string;
  primaryDark: string;

  // 辅助色
  accent: string;
  accentLight: string;
  accentDark: string;

  // 功能色
  success: string;
  warning: string;
  error: string;
  info: string;

  // 文本色
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  disabled: string;

  // 背景色
  backgroundRoot: string;
  backgroundDefault: string;
  backgroundTertiary: string;
  backgroundCard: string;

  // 边框色
  border: string;
  borderLight: string;
  borderDark: string;

  // 阴影色
  shadow: string;
  shadowLight: string;
  shadowStrong: string;

  // 触摸反馈色
  touchRipple: string;
  touchRippleDark: string;
  touchOverlay: string;
  touchOverlayDark: string;

  // 按钮文本色（扩展）
  buttonPrimaryText?: string;
  tabIconSelected?: string;
}

/** 深色模式颜色（可选扩展） */
export interface DarkThemeColors extends ThemeColors {
  // 深色模式可能有不同的颜色值
}

// ============ 间距类型 ============

/** 间距系统 */
export interface Spacing {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
  '3xl': number;
  '4xl': number;
  '5xl': number;
  '6xl': number;
}

// ============ 圆角类型 ============

/** 圆角系统 */
export interface BorderRadius {
  xs?: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
  '3xl': number;
  '4xl'?: number;
  full: number;
}

// ============ 字体类型 ============

/** 字体样式 */
export interface TypographyStyle {
  fontSize: number;
  lineHeight: number;
  fontWeight: TextStyle['fontWeight'];
  letterSpacing?: number;
  textTransform?: TextStyle['textTransform'];
}

/** 字体系统 */
export interface Typography {
  display: TypographyStyle;
  displayLarge?: TypographyStyle;
  displayMedium?: TypographyStyle;
  h1: TypographyStyle;
  h2: TypographyStyle;
  h3: TypographyStyle;
  h4?: TypographyStyle;
  title: TypographyStyle;
  body: TypographyStyle;
  bodyMedium: TypographyStyle;
  small: TypographyStyle;
  smallMedium: TypographyStyle;
  caption: TypographyStyle;
  captionMedium: TypographyStyle;
  label?: TypographyStyle;
  labelSmall?: TypographyStyle;
  labelTitle?: TypographyStyle;
  link?: TypographyStyle;
  stat?: TypographyStyle;
  tiny?: TypographyStyle;
  navLabel?: TypographyStyle;
}

// ============ 阴影类型 ============

/** 阴影样式 */
export interface ShadowStyle {
  shadowColor: string;
  shadowOffset: { width: number; height: number };
  shadowOpacity: number;
  shadowRadius: number;
  elevation: number;
}

/** 阴影系统 */
export interface Shadows {
  soft: ShadowStyle;
  medium: ShadowStyle;
  strong: ShadowStyle;
  glow: ShadowStyle;
  card?: ShadowStyle;
}

// ============ 动画类型 ============

/** 动画时长 */
export interface Animation {
  instant: number;
  fast: number;
  normal: number;
  slow: number;
  verySlow: number;
}

// ============ 触摸目标类型 ============

/** 触摸目标尺寸 */
export interface TouchTarget {
  minimum: number;
  comfortable: number;
  large: number;
}

/** HitSlop 扩展区域 */
export interface HitSlop {
  none: number;
  small: number;
  medium: number;
  large: number;
  extraLarge: number;
}

// ============ 完整主题类型 ============

/** 完整主题接口 */
export interface Theme {
  // 颜色
  primary: string;
  primaryLight: string;
  primaryDark: string;
  accent: string;
  accentLight: string;
  accentDark: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  disabled: string;
  backgroundRoot: string;
  backgroundDefault: string;
  backgroundTertiary: string;
  backgroundCard: string;
  border: string;
  borderLight: string;
  borderDark: string;
  shadow: string;
  shadowLight: string;
  shadowStrong: string;
  touchRipple: string;
  touchRippleDark: string;
  touchOverlay: string;
  touchOverlayDark: string;
  buttonPrimaryText?: string;
  tabIconSelected?: string;
}

/** 主题Hook返回值 */
export interface UseThemeReturn {
  theme: Theme;
  isDark: boolean;
}

/** 颜色方案 */
export type ColorScheme = 'light' | 'dark' | null;

/** 颜色方案选择 */
export type ColorSchemeChoice = 'follow-system' | 'dark' | 'light';

// ============ 辅助类型 ============

/** 主题变体 */
export type ThemeVariant = 'warm' | 'default';

/** 带主题的样式创建函数 */
export type CreateStylesFn<T> = (theme: Theme) => T;
