/**
 * 骨架屏组件
 * 用于显示加载占位符
 * 温暖守护风格
 */
import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { lightColors, spacing, borderRadius as borderRadiusTokens } from '@/design-system';

interface SkeletonProps {
  width?: number | string;
  height?: number;
  radius?: number;
  style?: ViewStyle;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 20,
  radius = borderRadiusTokens.sm,
  style,
}) => {
  return (
    <View
      style={[
        styles.skeleton,
        {
          width: width as any,
          height,
          borderRadius: radius,
        },
        style,
      ]}
    />
  );
};

interface SkeletonCardProps {
  style?: ViewStyle;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({ style }) => {
  return (
    <View style={[styles.card, style]}>
      <View style={styles.cardHeader}>
        <Skeleton width={48} height={48} radius={borderRadiusTokens.full} />
        <View style={styles.cardHeaderContent}>
          <Skeleton width={100} height={18} />
          <Skeleton width={60} height={14} />
        </View>
      </View>
      <Skeleton width="100%" height={12} />
      <Skeleton width="80%" height={12} />
    </View>
  );
};

interface SkeletonGridProps {
  count?: number;
  style?: ViewStyle;
}

export const SkeletonGrid: React.FC<SkeletonGridProps> = ({ count = 4, style }) => {
  return (
    <View style={[styles.gridContainer, style]}>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={styles.gridItem}>
          <Skeleton width={48} height={48} radius={borderRadiusTokens.xl} />
          <Skeleton width={80} height={14} />
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: lightColors.backgroundTertiary,
    opacity: 0.6,
  },

  card: {
    backgroundColor: lightColors.backgroundDefault,
    borderRadius: borderRadiusTokens.xl,
    padding: spacing.lg,
    gap: spacing.sm,
  },

  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    marginBottom: spacing.md,
  },

  cardHeaderContent: {
    flex: 1,
    gap: spacing.xs,
  },

  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },

  gridItem: {
    width: '48%',
    aspectRatio: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: lightColors.backgroundDefault,
    borderRadius: borderRadiusTokens.xl,
    padding: spacing.lg,
  },
});

export default Skeleton;
