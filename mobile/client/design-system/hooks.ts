/**
 * 设计系统 Hooks
 */
import { useMemo, useCallback } from 'react';
import {
  StyleSheet,
  ViewStyle,
  TextStyle,
  ImageStyle,
  AccessibilityInfo,
} from 'react-native';
import { useThemeContext } from './ThemeProvider';
import { Theme, ThemedStyles, TypographyVariant } from './types';

// ============================================================================
// useTheme - 获取当前主题
// ============================================================================

export function useTheme(): Theme {
  const { theme } = useThemeContext();
  return theme;
}

// ============================================================================
// useColorScheme - 获取当前颜色模式
// ============================================================================

export function useColorScheme() {
  const { colorScheme, isDark } = useThemeContext();
  return { colorScheme, isDark };
}

// ============================================================================
// useThemedStyles - 创建主题相关的样式表
// ============================================================================

/**
 * 创建基于主题的 StyleSheet 样式
 * 样式会在主题变化时自动重新计算
 *
 * 用法示例：
 * ```tsx
 * const createStyles = (theme: Theme) => StyleSheet.create({
 *   container: {
 *     padding: theme.spacing.lg,
 *     backgroundColor: theme.colors.backgroundRoot,
 *   },
 *   title: {
 *     ...theme.typography.h1,
 *     color: theme.colors.textPrimary,
 *   },
 * });
 *
 * function MyComponent() {
 *   const styles = useThemedStyles(createStyles);
 *   return (
 *     <View style={styles.container}>
 *       <Text style={styles.title}>Hello</Text>
 *     </View>
 *   );
 * }
 * ```
 */
export function useThemedStyles<T extends Record<string, ViewStyle | TextStyle | ImageStyle>>(
  createStylesFn: (theme: Theme) => T
): T {
  const { theme } = useThemeContext();
  return useMemo(() => createStylesFn(theme), [theme, createStylesFn]);
}

// ============================================================================
// useTypography - 获取排版样式
// ============================================================================

/**
 * 获取指定变体的排版样式
 * @param variant 排版变体名称
 * @param color 可选的文本颜色（默认使用 textPrimary）
 */
export function useTypography(
  variant: TypographyVariant,
  color?: string
): TextStyle {
  const { theme } = useThemeContext();
  return useMemo(
    () => ({
      ...theme.typography[variant],
      color: color ?? theme.colors.textPrimary,
    }),
    [theme, variant, color]
  );
}

// ============================================================================
// useAccessibility - 无障碍状态
// ============================================================================

/**
 * 获取无障碍相关状态
 */
export function useAccessibility() {
  const { reduceMotion } = useThemeContext();

  const announceForAccessibility = useCallback((message: string) => {
    AccessibilityInfo.announceForAccessibility(message);
  }, []);

  return {
    reduceMotion,
    announceForAccessibility,
  };
}

// ============================================================================
// useThemePreference - 主题偏好管理
// ============================================================================

/**
 * 管理用户主题偏好（跟随系统 / 浅色 / 深色）
 */
export function useThemePreference() {
  const { preference, setPreference, toggleColorScheme } = useThemeContext();

  return {
    preference,
    setPreference,
    toggleColorScheme,
    isSystem: preference === 'system',
    isLight: preference === 'light',
    isDark: preference === 'dark',
  };
}
