import React from 'react';
import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import {
  lightColors,
  spacing,
  borderRadius,
  typography,
  hitSlop,
} from '@/design-system';
import { createShadows } from '@/design-system';

const shadows = createShadows(lightColors.shadow, lightColors.shadowStrong);

interface EmptyStateProps {
  icon: React.ComponentProps<typeof FontAwesome6>['name'];
  title: string;
  subtitle?: string;
  actionLabel?: string;
  onActionPress?: () => void;
}

export default function EmptyState({
  icon,
  title,
  subtitle,
  actionLabel,
  onActionPress,
}: EmptyStateProps) {
  return (
    <View style={styles.container}>
      <FontAwesome6 name={icon} size={56} color={lightColors.textMuted} style={styles.icon} />
      <ThemedText variant="bodyMedium" color={lightColors.textPrimary} style={styles.title}>
        {title}
      </ThemedText>
      {!!subtitle && (
        <ThemedText variant="small" color={lightColors.textSecondary} style={styles.subtitle}>
          {subtitle}
        </ThemedText>
      )}
      {!!actionLabel && !!onActionPress && (
        <TouchableOpacity
          style={styles.actionButton}
          onPress={onActionPress}
          activeOpacity={0.86}
          hitSlop={hitSlop.medium}
          accessibilityRole="button"
          accessibilityLabel={actionLabel}
        >
          <ThemedText variant="bodyMedium" color={lightColors.backgroundDefault}>
            {actionLabel}
          </ThemedText>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing['2xl'],
  },
  icon: {
    marginBottom: spacing.lg,
  },
  title: {
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  actionButton: {
    minHeight: 44,
    paddingHorizontal: spacing.xl,
    borderRadius: borderRadius.xl,
    backgroundColor: lightColors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.medium,
  },
});
