/**
 * 健康档案页面（增强版）
 * 改进：
 * - 骨架屏占位加载动画
 * - 模块卡片渐变背景
 * - 顶部健康摘要区
 * - 响应式 2 / 3 列网格
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Animated,
  useWindowDimensions,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { useTheme } from '@/hooks/useTheme';
import { spacing, borderRadius } from '@/design-system';
import { usePressScale } from '@/hooks/usePressScale';
import { useSafeRouter } from '@/hooks/useSafeRouter';

interface HealthModule {
  id: string;
  title: string;
  description: string;
  icon: string;
  gradient: [string, string];
  route: string;
  emoji: string;
  badge?: string;
}

const HEALTH_MODULES: HealthModule[] = [
  {
    id: 'medical-history',
    title: '病史记录',
    description: '慢性病、手术史',
    icon: 'notes-medical',
    gradient: ['#FF6B6B', '#FF8E53'],
    route: '/health/medical-history',
    emoji: '📋',
  },
  {
    id: 'medication',
    title: '用药管理',
    description: '药物与剂量',
    icon: 'pills',
    gradient: ['#4FACFE', '#00F2FE'],
    route: '/health/medication',
    emoji: '💊',
    badge: '提醒',
  },
  {
    id: 'allergies',
    title: '过敏史',
    description: '食物与药物过敏',
    icon: 'allergies',
    gradient: ['#F093FB', '#F5576C'],
    route: '/health/allergies',
    emoji: '⚠️',
  },
  {
    id: 'vaccination',
    title: '疫苗接种',
    description: '接种记录',
    icon: 'syringe',
    gradient: ['#4776E6', '#8E54E9'],
    route: '/health/vaccination',
    emoji: '💉',
  },
  {
    id: 'vitals',
    title: '生命体征',
    description: '血压/血糖/心率',
    icon: 'heart-pulse',
    gradient: ['#11998E', '#38EF7D'],
    route: '/health/vitals',
    emoji: '📊',
  },
  {
    id: 'emergency-info',
    title: '急救卡',
    description: 'SOS 时展示',
    icon: 'id-card',
    gradient: ['#FC5C7D', '#6A3093'],
    route: '/health/emergency-card',
    emoji: '🆔',
    badge: '重要',
  },
];

// 骨架屏卡片
function SkeletonCard({ width: cardW }: { width: number }) {
  const shimmer = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmer, { toValue: 1, duration: 900, useNativeDriver: true }),
        Animated.timing(shimmer, { toValue: 0, duration: 900, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, []);

  const opacity = shimmer.interpolate({ inputRange: [0, 1], outputRange: [0.3, 0.65] });

  return (
    <Animated.View
      style={[
        { width: cardW, borderRadius: borderRadius.xl, overflow: 'hidden', opacity },
      ]}
    >
      <View style={{ height: cardW * 0.85, backgroundColor: '#E0E0E0', borderRadius: borderRadius.xl }} />
    </Animated.View>
  );
}

export default function HealthScreen() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { width } = useWindowDimensions();
  const [isLoading, setIsLoading] = useState(true);

  const fadeAnim = useRef(new Animated.Value(0)).current;

  const isTablet = width >= 768;
  const cols = isTablet ? 3 : 2;
  const cardWidth = (width - spacing.lg * 2 - spacing.md * (cols - 1)) / cols;

  useEffect(() => {
    // 模拟加载
    const t = setTimeout(() => {
      setIsLoading(false);
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    }, 800);
    return () => clearTimeout(t);
  }, []);

  const handleModulePress = (route: string) => {
    router.push(route);
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <ScrollView contentContainerStyle={s.content}>

        {/* 顶部渐变 Banner */}
        <LinearGradient
          colors={['#11998E', '#38EF7D']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={s.banner}
        >
          <View style={s.bannerContent}>
            <View>
              <ThemedText variant="h2" color="#fff" style={s.bannerTitle}>健康档案</ThemedText>
              <ThemedText variant="body" color="rgba(255,255,255,0.85)" style={s.bannerSubtitle}>
                守护您的健康信息
              </ThemedText>
            </View>
            <View style={s.bannerIcon}>
              <ThemedText style={{ fontSize: 48 }}>🏥</ThemedText>
            </View>
          </View>

          {/* 健康摘要统计 */}
          <View style={s.statsRow}>
            <HealthStat label="病史" value="0 条" icon="notes-medical" />
            <HealthStat label="药物" value="0 种" icon="pills" />
            <HealthStat label="过敏源" value="0 项" icon="allergies" />
          </View>
        </LinearGradient>

        {/* 功能网格 */}
        <View style={[s.grid, { paddingHorizontal: spacing.lg }]}>
          <ThemedText variant="h3" color={theme.textPrimary} style={s.sectionTitle}>功能模块</ThemedText>

          <View style={[s.gridRow, { gap: spacing.md }]}>
            {isLoading
              ? Array(6).fill(0).map((_, i) => <SkeletonCard key={i} width={cardWidth} />)
              : HEALTH_MODULES.map((module) => (
                <Animated.View key={module.id} style={{ opacity: fadeAnim, width: cardWidth }}>
                  <ModuleCard
                    module={module}
                    cardWidth={cardWidth}
                    onPress={() => handleModulePress(module.route)}
                  />
                </Animated.View>
              ))}
          </View>
        </View>

        {/* 导出按钮 */}
        {!isLoading && (
          <Animated.View style={[s.exportSection, { opacity: fadeAnim }]}>
            <TouchableOpacity
              style={s.exportBtn}
              onPress={() => router.push('/health/export')}
              activeOpacity={0.88}
              accessibilityRole="button"
              accessibilityLabel="导出健康档案"
            >
              <LinearGradient
                colors={[theme.primary, theme.primaryDark]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={s.exportBtnGradient}
              >
                <FontAwesome6 name="file-export" size={18} color="#fff" />
                <ThemedText variant="bodyMedium" color="#fff" style={s.exportBtnText}>
                  导出健康档案
                </ThemedText>
                <FontAwesome6 name="chevron-right" size={14} color="rgba(255,255,255,0.7)" />
              </LinearGradient>
            </TouchableOpacity>
            <ThemedText variant="caption" color={theme.textMuted} style={s.exportHint}>
              生成 PDF 档案，方便就医时分享给医生
            </ThemedText>
          </Animated.View>
        )}
      </ScrollView>
    </Screen>
  );
}

function HealthStat({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <View style={s.statItem}>
      <FontAwesome6 name={icon as any} size={16} color="rgba(255,255,255,0.9)" />
      <ThemedText variant="bodyMedium" color="#fff" style={s.statValue}>{value}</ThemedText>
      <ThemedText variant="caption" color="rgba(255,255,255,0.75)" style={s.statLabel}>{label}</ThemedText>
    </View>
  );
}

function ModuleCard({
  module,
  cardWidth,
  onPress,
}: {
  module: HealthModule;
  cardWidth: number;
  onPress: () => void;
}) {
  const { scale: pressScale, pressHandlers } = usePressScale(0.93);

  return (
    <Animated.View style={{ transform: [{ scale: pressScale }] }}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={pressHandlers.onPressIn}
        onPressOut={pressHandlers.onPressOut}
        activeOpacity={1}
        accessibilityRole="button"
        accessibilityLabel={module.title}
      >
        <LinearGradient
          colors={module.gradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[s.moduleCard, { height: cardWidth * 0.85 }]}
        >
          {/* 装饰 emoji */}
          <ThemedText style={s.moduleEmoji}>{module.emoji}</ThemedText>

          {/* 徽章 */}
          {module.badge && (
            <View style={s.badge}>
              <ThemedText variant="caption" color="#fff" style={s.badgeText}>{module.badge}</ThemedText>
            </View>
          )}

          <View style={s.moduleContent}>
            <View style={s.moduleIconWrap}>
              <FontAwesome6 name={module.icon as any} size={24} color="#fff" />
            </View>
            <ThemedText variant="bodyMedium" color="#fff" style={s.moduleTitle}>{module.title}</ThemedText>
            <ThemedText variant="caption" color="rgba(255,255,255,0.8)" style={s.moduleDesc}>
              {module.description}
            </ThemedText>
          </View>
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
}

const s = StyleSheet.create({
  content: {
    paddingBottom: spacing['4xl'],
  },
  banner: {
    paddingHorizontal: spacing.lg,
    paddingTop: Platform.OS === 'ios' ? 56 : spacing['2xl'],
    paddingBottom: spacing['2xl'],
    marginBottom: spacing.xl,
  },
  bannerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
  },
  bannerTitle: { fontSize: 26, fontWeight: '800', color: '#fff' },
  bannerSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.85)', marginTop: 4 },
  bannerIcon: { opacity: 0.3 },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.lg,
  },
  statItem: { alignItems: 'center', gap: 4 },
  statValue: { fontSize: 16, fontWeight: '700', color: '#fff' },
  statLabel: { fontSize: 11, color: 'rgba(255,255,255,0.75)' },
  grid: { marginBottom: spacing.xl },
  sectionTitle: { fontSize: 17, fontWeight: '700', marginBottom: spacing.lg },
  gridRow: { flexDirection: 'row', flexWrap: 'wrap' },
  moduleCard: {
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
    padding: spacing.md,
    justifyContent: 'flex-end',
  },
  moduleEmoji: {
    position: 'absolute',
    top: 10,
    right: 12,
    fontSize: 28,
    opacity: 0.25,
  },
  badge: {
    position: 'absolute',
    top: 10,
    left: 10,
    backgroundColor: 'rgba(0,0,0,0.25)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 100,
  },
  badgeText: { fontSize: 10, fontWeight: '700', color: '#fff' },
  moduleContent: { gap: 3 },
  moduleIconWrap: {
    width: 40,
    height: 40,
    borderRadius: borderRadius.md,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  moduleTitle: { fontSize: 14, fontWeight: '700', color: '#fff' },
  moduleDesc: { fontSize: 11, color: 'rgba(255,255,255,0.8)', lineHeight: 15 },
  exportSection: {
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
  },
  exportBtn: {
    width: '100%',
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
  },
  exportBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 54,
    gap: spacing.md,
  },
  exportBtnText: { fontSize: 15, fontWeight: '600', color: '#fff', flex: 1, textAlign: 'center' },
  exportHint: { marginTop: spacing.sm, fontSize: 12, color: '#9E9E9E', textAlign: 'center' },
});
