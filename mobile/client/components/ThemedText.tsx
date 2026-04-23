import React from 'react';
import { Text, TextProps, TextStyle } from 'react-native';
import { useTheme, useTypography } from '@/design-system';
import { TypographyVariant } from '@/design-system/types';

interface ThemedTextProps extends TextProps {
  variant?: TypographyVariant;
  color?: string;
}

/**
 * 主题文本组件
 * 自动应用排版样式和主题颜色
 *
 * @example
 * <ThemedText variant="h1">标题</ThemedText>
 * <ThemedText variant="body" color={theme.colors.textSecondary}>次要文本</ThemedText>
 */
export function ThemedText({
  variant = 'body',
  color,
  style,
  children,
  ...props
}: ThemedTextProps) {
  const theme = useTheme();
  const typographyStyle = useTypography(variant, color);

  return (
    <Text
      style={[typographyStyle, style]}
      maxFontSizeMultiplier={1.5} // 限制字体放大倍数，避免布局崩坏
      {...props}
    >
      {children}
    </Text>
  );
}
