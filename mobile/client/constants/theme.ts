/**
 * 主题常量（向后兼容导出）
 * 新代码推荐直接使用：
 * import { useTheme, spacing, typography } from '@/design-system';
 */

import { lightColors, spacing, borderRadius, typography } from '@/design-system';

// 兼容旧代码的 Colors 结构
export const Colors = {
  light: {
    textPrimary: lightColors.textPrimary,
    textSecondary: lightColors.textSecondary,
    textMuted: lightColors.textMuted,
    primary: lightColors.primary,
    primaryDark: lightColors.primaryDark,
    primaryLight: lightColors.primaryLight,
    accent: lightColors.accent,
    success: lightColors.success,
    error: lightColors.error,
    info: lightColors.info,
    warning: lightColors.warning,
    backgroundRoot: lightColors.backgroundRoot,
    backgroundDefault: lightColors.backgroundDefault,
    backgroundTertiary: lightColors.backgroundTertiary,
    buttonPrimaryText: lightColors.buttonPrimaryText,
    tabIconSelected: lightColors.tabIconSelected,
    border: lightColors.border,
    borderLight: lightColors.borderLight,
  },
  dark: {
    textPrimary: '#ECEFF1',
    textSecondary: '#B0BEC5',
    textMuted: '#78909C',
    primary: '#FFAB91',
    primaryDark: '#FF8A65',
    primaryLight: '#FFCCBC',
    accent: '#81C784',
    success: '#66BB6A',
    error: '#EF5350',
    info: '#64B5F6',
    warning: '#FFB74D',
    backgroundRoot: '#121212',
    backgroundDefault: '#1E1E1E',
    backgroundTertiary: '#2C2C2C',
    buttonPrimaryText: '#FFFFFF',
    tabIconSelected: '#FFAB91',
    border: '#424242',
    borderLight: '#303030',
  },
};

export { spacing as Spacing };
export { borderRadius as BorderRadius };
export { typography as Typography };

export type { Theme } from '@/design-system';
