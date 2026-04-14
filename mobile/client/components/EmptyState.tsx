import React from 'react';
import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  Shadows,
  HitSlop,
} from '@/constants/theme-warm';

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
      <FontAwesome6 name={icon} size={56} color={Colors.textMuted} style={styles.icon} />
      <ThemedText variant="bodyMedium" color={Colors.textPrimary} style={styles.title}>
        {title}
      </ThemedText>
      {!!subtitle && (
        <ThemedText variant="small" color={Colors.textSecondary} style={styles.subtitle}>
          {subtitle}
        </ThemedText>
      )}
      {!!actionLabel && !!onActionPress && (
        <TouchableOpacity
          style={styles.actionButton}
          onPress={onActionPress}
          activeOpacity={0.86}
          hitSlop={HitSlop.medium}
          accessibilityRole="button"
          accessibilityLabel={actionLabel}
        >
          <ThemedText variant="bodyMedium" color={Colors.backgroundDefault}>
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
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing['2xl'],
  },
  icon: {
    marginBottom: Spacing.lg,
  },
  title: {
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: Spacing.lg,
  },
  actionButton: {
    minHeight: 44,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.xl,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...Shadows.medium,
  },
});
