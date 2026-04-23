/**
 * 起了吗 App - 设计系统
 * Qilema Design System
 *
 * 导出所有设计系统相关的类型、令牌、主题、工具和组件
 */

// ============================================================================
// 类型
// ============================================================================
export type {
  ColorTokens,
  TypographyStyle,
  TypographyVariant,
  TypographyScale,
  SpacingToken,
  SpacingScale,
  BorderRadiusToken,
  BorderRadiusScale,
  ShadowStyle,
  ShadowToken,
  ShadowScale,
  AnimationTokens,
  TouchTargetTokens,
  HitSlopTokens,
  BreakpointTokens,
  ZIndexTokens,
  InteractionTokens,
  ComponentDefaults,
  ColorScheme,
  Theme,
  ThemeConfig,
  ThemePreference,
  ThemedStyle,
  ThemedStyles,
  CreateStylesTheme,
} from './types';

// ============================================================================
// 令牌（原始值，可直接使用）
// ============================================================================
export { lightColors, darkColors, semanticColors, contrastRatios } from './tokens/colors';
export { typography } from './tokens/typography';
export { spacing } from './tokens/spacing';
export { borderRadius } from './tokens/borderRadius';
export { createShadows } from './tokens/shadows';
export { animation } from './tokens/animation';
export { touchTarget, hitSlop, breakpoints, zIndex } from './tokens/layout';
export { interaction } from './tokens/interaction';
export { componentDefaults } from './tokens/componentDefaults';

// ============================================================================
// 主题（完整的 Theme 对象）
// ============================================================================
export { warmLight, warmDark, warmThemeConfig } from './themes';

// ============================================================================
// 工具函数
// ============================================================================
export {
  hexToRgba,
  alpha,
  getLuminance,
  autoTextColor,
  spacer,
  spacerHorizontal,
  responsive,
  calculateContrastRatio,
  meetsWCAGAA,
  meetsWCAGAAA,
} from './utils';

// ============================================================================
// Provider & Hooks
// ============================================================================
export { ThemeProvider, useThemeContext } from './ThemeProvider';
export {
  useTheme,
  useColorScheme,
  useThemedStyles,
  useTypography,
  useAccessibility,
  useThemePreference,
} from './hooks';
