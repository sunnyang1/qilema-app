import React from 'react';
import { View, ViewProps, ViewStyle } from 'react-native';
import { useTheme } from '@/design-system';

type BackgroundLevel = 'root' | 'default' | 'tertiary' | 'card';

interface ThemedViewProps extends ViewProps {
  level?: BackgroundLevel;
  backgroundColor?: string;
}

const backgroundMap: Record<BackgroundLevel, keyof ReturnType<typeof useTheme>['colors']> = {
  root: 'backgroundRoot',
  default: 'backgroundDefault',
  tertiary: 'backgroundTertiary',
  card: 'backgroundCard',
};

/**
 * 主题视图组件
 * 自动应用主题背景色
 *
 * @example
 * <ThemedView level="root">...</ThemedView>
 * <ThemedView level="card" style={{ padding: 20 }}>...</ThemedView>
 */
export function ThemedView({
  level = 'root',
  backgroundColor,
  style,
  children,
  ...props
}: ThemedViewProps) {
  const theme = useTheme();
  const bgColor = backgroundColor ?? theme.colors[backgroundMap[level]];

  const viewStyle: ViewStyle = {
    backgroundColor: bgColor,
  };

  return (
    <View style={[viewStyle, style]} {...props}>
      {children}
    </View>
  );
}
