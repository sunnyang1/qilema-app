/**
 * 骨架屏组件
 * 用于显示加载占位符
 * 温暖守护风格
 */
import React from 'react';
import { View, StyleSheet } from 'react-native';
import {
  Colors,
  Spacing,
  BorderRadius,
} from '@/constants/theme-warm';

interface SkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: any;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 20,
  borderRadius = BorderRadius.sm,
  style,
}) => {
  return (
    <View
      style={[
        styles.skeleton,
        {
          width,
          height,
          borderRadius,
        },
        style,
      ]}
    />
  );
};

interface SkeletonCardProps {
  style?: any;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({ style }) => {
  return (
    <View style={[styles.card, style]}>
      <View style={styles.cardHeader}>
        <Skeleton width={48} height={48} borderRadius={BorderRadius.full} />
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
  style?: any;
}

export const SkeletonGrid: React.FC<SkeletonGridProps> = ({ count = 4, style }) => {
  return (
    <View style={[styles.gridContainer, style]}>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={styles.gridItem}>
          <Skeleton width={48} height={48} borderRadius={BorderRadius.xl} />
          <Skeleton width={80} height={14} />
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: Colors.backgroundTertiary,
    opacity: 0.6,
  },

  card: {
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    gap: Spacing.sm,
  },

  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    marginBottom: Spacing.md,
  },

  cardHeaderContent: {
    flex: 1,
    gap: Spacing.xs,
  },

  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },

  gridItem: {
    width: '48%',
    aspectRatio: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
  },
});

export default Skeleton;
