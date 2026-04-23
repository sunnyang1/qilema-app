/**
 * useTheme Hook（兼容层）
 *
 * 新代码请直接使用：
 *   import { useTheme, useColorScheme } from '@/design-system';
 *
 * 本文件仅做兼容转发，避免批量修改所有引用。
 * 返回扁平化的 theme 对象，支持 theme.primary、theme.spacing 等直接访问。
 */

import { useTheme as useDesignTheme, useColorScheme } from '@/design-system';
import type { CreateStylesTheme } from '@/design-system';

/**
 * 获取当前主题（兼容旧 API）
 * @returns {{ theme: CreateStylesTheme, isDark: boolean }}
 */
function useTheme() {
  const theme = useDesignTheme();
  const { isDark } = useColorScheme();

  // 扁平化：将 theme.colors 中的属性提升到顶层
  const flatTheme: CreateStylesTheme = {
    ...theme,
    ...theme.colors,
  };

  return {
    theme: flatTheme,
    isDark,
  };
}

export { useTheme };
