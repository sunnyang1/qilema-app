/**
 * 页面占位符
 * 温暖守护风格 + UI/UX Pro Max 优化
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { Colors, Spacing, Typography } from '@/constants/theme-warm';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.xl,
  },
  title: {
    ...Typography.h1,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
});

export default function PlaceholderPage() {
  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      <View style={styles.container}>
        <ThemedText variant="h1" color={Colors.textPrimary} style={styles.title}>
          页面待实现
        </ThemedText>
        <ThemedText variant="body" color={Colors.textSecondary} style={styles.subtitle}>
          此页面正在开发中...
        </ThemedText>
      </View>
    </Screen>
  );
}
