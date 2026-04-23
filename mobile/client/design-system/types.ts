/**
 * 设计系统类型定义
 * Design System Type Definitions
 */
import { TextStyle, ViewStyle } from 'react-native';

// ============================================================================
// 颜色令牌类型
// ============================================================================

export interface ColorTokens {
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
  buttonPrimaryText: string;

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

  // 触摸反馈
  touchRipple: string;
  touchRippleDark: string;
  touchOverlay: string;
  touchOverlayDark: string;

  // 其他
  tabIconSelected: string;
}

// ============================================================================
// 排版令牌类型
// ============================================================================

export interface TypographyStyle {
  fontSize: number;
  lineHeight: number;
  fontWeight: TextStyle['fontWeight'];
  letterSpacing?: number;
  textTransform?: TextStyle['textTransform'];
}

export type TypographyVariant =
  | 'display'
  | 'displayLarge'
  | 'displayMedium'
  | 'h1'
  | 'h2'
  | 'h3'
  | 'h4'
  | 'title'
  | 'body'
  | 'bodyMedium'
  | 'small'
  | 'smallMedium'
  | 'caption'
  | 'captionMedium'
  | 'label'
  | 'labelSmall'
  | 'labelTitle'
  | 'link'
  | 'stat'
  | 'tiny'
  | 'navLabel';

export type TypographyScale = Record<TypographyVariant, TypographyStyle>;

// ============================================================================
// 间距令牌类型
// ============================================================================

export type SpacingToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl';
export type SpacingScale = Record<SpacingToken, number>;

// ============================================================================
// 圆角令牌类型
// ============================================================================

export type BorderRadiusToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | 'full';
export type BorderRadiusScale = Record<BorderRadiusToken, number>;

// ============================================================================
// 阴影令牌类型
// ============================================================================

export interface ShadowStyle {
  shadowColor: string;
  shadowOffset: { width: number; height: number };
  shadowOpacity: number;
  shadowRadius: number;
  elevation: number;
}

export type ShadowToken = 'soft' | 'medium' | 'strong' | 'glow' | 'card';
export type ShadowScale = Record<ShadowToken, ShadowStyle>;

// ============================================================================
// 动画令牌类型
// ============================================================================

export interface AnimationTokens {
  instant: number;
  fast: number;
  normal: number;
  slow: number;
  verySlow: number;
}

// ============================================================================
// 布局令牌类型
// ============================================================================

export interface TouchTargetTokens {
  minimum: number;
  comfortable: number;
  large: number;
}

export interface HitSlopTokens {
  none: number;
  small: number;
  medium: number;
  large: number;
  extraLarge: number;
}

export interface BreakpointTokens {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
}

export interface ZIndexTokens {
  modal: number;
  dropdown: number;
  sticky: number;
  header: number;
  toast: number;
  overlay: number;
  tooltip: number;
  popover: number;
  default: number;
}

// ============================================================================
// 交互令牌类型
// ============================================================================

export interface InteractionTokens {
  buttonScale: number;
  cardScale: number;
  rippleRadius: {
    small: number;
    medium: number;
    large: number;
    extraLarge: number;
  };
  useNativeDriver: boolean;
  respectReducedMotion: boolean;
}

// ============================================================================
// 组件默认样式类型
// ============================================================================

export interface ComponentDefaults {
  button: {
    height: number;
    paddingHorizontal: number;
    borderRadius: number;
    gap: number;
  };
  input: {
    height: number;
    paddingHorizontal: number;
    borderRadius: number;
    fontSize: number;
    lineHeight: number;
  };
  card: {
    borderRadius: number;
    padding: number;
  };
  listItem: {
    height: number;
    paddingHorizontal: number;
    gap: number;
  };
}

// ============================================================================
// 主题类型
// ============================================================================

export type ColorScheme = 'light' | 'dark';

export interface Theme {
  colors: ColorTokens;
  typography: TypographyScale;
  spacing: SpacingScale;
  borderRadius: BorderRadiusScale;
  shadows: ShadowScale;
  animation: AnimationTokens;
  touchTarget: TouchTargetTokens;
  hitSlop: HitSlopTokens;
  breakpoints: BreakpointTokens;
  zIndex: ZIndexTokens;
  interaction: InteractionTokens;
  componentDefaults: ComponentDefaults;
}

// ============================================================================
// 主题配置类型
// ============================================================================

export interface ThemeConfig {
  light: Theme;
  dark: Theme;
}

export type ThemePreference = 'system' | 'light' | 'dark';

// ============================================================================
// 样式工具类型
// ============================================================================

export type ThemedStyle<T = ViewStyle> = (theme: Theme) => T;
export type ThemedStyles<T extends Record<string, ViewStyle | TextStyle>> = (theme: Theme) => T;

/**
 * 用于 createStyles 函数的扁平化主题类型。
 * 将 colors 中的属性提升到顶层，方便在 StyleSheet 中直接访问 theme.primary 等。
 */
export type CreateStylesTheme = Omit<Theme, 'colors'> & ColorTokens;
