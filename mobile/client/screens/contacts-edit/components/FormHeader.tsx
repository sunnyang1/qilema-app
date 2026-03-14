/**
 * 表单头部组件
 */
import React from 'react';
import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  HitSlop,
} from '@/constants/theme-warm';

interface FormHeaderProps {
  isEditing: boolean;
  onCancel: () => void;
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.lg,
  },

  headerTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
    flex: 1,
    textAlign: 'center',
  },

  cancelButton: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.lg,
  },

  cancelButtonText: {
    ...Typography.bodyMedium,
    color: Colors.textSecondary,
  },

  placeholder: {
    width: 60,
  },
});

export function FormHeader({ isEditing, onCancel }: FormHeaderProps) {
  return (
    <View style={styles.header} accessible accessibilityLabel="编辑联系人页面">
      <TouchableOpacity
        style={styles.cancelButton}
        onPress={onCancel}
        hitSlop={HitSlop.medium}
        accessible
        accessibilityLabel="取消"
        accessibilityHint="点击取消编辑并返回"
        accessibilityRole="button"
      >
        <ThemedText variant="bodyMedium" color={Colors.textSecondary} style={styles.cancelButtonText}>
          取消
        </ThemedText>
      </TouchableOpacity>
      <ThemedText variant="h1" color={Colors.textPrimary} style={styles.headerTitle}>
        {isEditing ? '编辑联系人' : '添加联系人'}
      </ThemedText>
      <View style={styles.placeholder} />
    </View>
  );
}
