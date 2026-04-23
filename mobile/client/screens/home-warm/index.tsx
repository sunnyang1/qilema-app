/**
 * 首页 - 签到页面（增强响应式版）
 * 改进：
 * - 响应式布局（useWindowDimensions）
 * - 签到按钮触觉反馈
 * - 签到成功庆祝动画
 * - 连续签到里程碑激励
 * - 快捷功能卡片视觉增强
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Animated,
  TouchableOpacity,
  useWindowDimensions,
  Platform,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import {
  spacing,
  borderRadius,
  typography,
  animation,
} from '@/design-system';
import { createShadows } from '@/design-system';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import { useAuth } from '@/contexts/AuthContext';
import { checkInService } from '@/services/checkin';
import Toast from 'react-native-toast-message';

// 辅助：获取问候语
const getGreeting = () => {
  const h = new Date().getHours();
  if (h < 6) return '凌晨好';
  if (h < 9) return '早安';
  if (h < 12) return '上午好';
  if (h < 14) return '中午好';
  if (h < 18) return '下午好';
  if (h < 22) return '晚上好';
  return '夜深了';
};

const getCurrentTime = () => {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
};

// 快捷功能配置
const QUICK_ACTIONS = [
  { id: 'sos', label: 'SOS求助', icon: 'phone-volume', color: '#EF5350', route: '/sos', emoji: '🆘' },
  { id: 'contacts', label: '紧急联系人', icon: 'address-book', color: '#5C6BC0', route: '/contacts', emoji: '📱' },
  { id: 'health', label: '健康档案', icon: 'notes-medical', color: '#26A69A', route: '/health', emoji: '💊' },
  { id: 'knowledge', label: '急救知识', icon: 'book-medical', color: '#FFA726', route: '/knowledge', emoji: '📚' },
];

export default function WarmHomePage() {
  const router = useSafeRouter();
  const { user } = useAuth();
  const { theme, isDark } = useTheme();
  const { width } = useWindowDimensions();

  // 响应式：卡片宽度
  const isTablet = width >= 768;
  const cardWidth = isTablet ? (width - 80) / 3 : (width - 60) / 2;

  const shadows = createShadows(theme.shadow, theme.shadowStrong);
  const s = createStyles(theme);

  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [checkInLoading, setCheckInLoading] = useState(false);
  const [stats, setStats] = useState({ consecutiveDays: 0, totalCheckIns: 0 });
  const [currentTime, setCurrentTime] = useState(getCurrentTime());

  // 动画
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;
  const checkInScale = useRef(new Animated.Value(1)).current;
  const celebrateAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // 快捷按钮按压动画
  const actionScales = useRef(QUICK_ACTIONS.map(() => new Animated.Value(1))).current;

  useEffect(() => {
    loadCheckInStatus();
    // 入场动画
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: animation.normal, useNativeDriver: true }),
      Animated.spring(slideAnim, { toValue: 0, tension: 50, friction: 7, useNativeDriver: true }),
    ]).start();
  }, []);

  // 未签到时 checkIn 按钮轻微脉动
  useEffect(() => {
    if (!isCheckedIn) {
      const loop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.04, duration: 800, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
        ])
      );
      loop.start();
      return () => loop.stop();
    }
  }, [isCheckedIn]);

  // 时钟更新
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(getCurrentTime()), 1000);
    return () => clearInterval(timer);
  }, []);

  const loadCheckInStatus = async () => {
    try {
      const [checkedToday, statsData] = await Promise.all([
        checkInService.isCheckedInToday(),
        checkInService.getCheckInStats(),
      ]);
      setIsCheckedIn(checkedToday);
      setStats({ consecutiveDays: statsData.consecutiveDays, totalCheckIns: statsData.totalCheckIns });
    } catch (e) {
      console.error('加载签到状态失败:', e);
    }
  };

  const handleCheckIn = async () => {
    if (isCheckedIn || checkInLoading) return;

    // 触觉反馈
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    // 按钮按压动画
    Animated.sequence([
      Animated.timing(checkInScale, { toValue: 0.92, duration: 80, useNativeDriver: true }),
      Animated.spring(checkInScale, { toValue: 1, tension: 200, friction: 6, useNativeDriver: true }),
    ]).start();

    setCheckInLoading(true);
    try {
      await checkInService.checkIn();
      setIsCheckedIn(true);
      await loadCheckInStatus();

      // 庆祝动画
      Animated.sequence([
        Animated.timing(celebrateAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.delay(1000),
        Animated.timing(celebrateAnim, { toValue: 0, duration: 300, useNativeDriver: true }),
      ]).start();

      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      Toast.show({ type: 'success', text1: '✅ 签到成功', text2: '今天也要保持好心情 💫', visibilityTime: 2200 });
    } catch (e) {
      console.error('签到失败:', e);
      Toast.show({ type: 'error', text1: '签到失败', text2: '请稍后重试', visibilityTime: 2600 });
    } finally {
      setCheckInLoading(false);
    }
  };

  // 快捷按钮交互
  const handleActionPress = (route: string, idx: number) => {
    if (Platform.OS !== 'web') Haptics.selectionAsync();
    router.push(route);
  };

  const onActionPressIn = (idx: number) => {
    Animated.spring(actionScales[idx], { toValue: 0.93, useNativeDriver: true, speed: 50 }).start();
  };
  const onActionPressOut = (idx: number) => {
    Animated.spring(actionScales[idx], { toValue: 1, useNativeDriver: true, speed: 30 }).start();
  };

  // 连续签到里程碑
  const getMilestoneInfo = () => {
    const d = stats.consecutiveDays;
    if (d >= 30) return { label: '🏆 月度守护者', color: '#FF8F00' };
    if (d >= 14) return { label: '🔥 双周坚持者', color: '#E91E63' };
    if (d >= 7) return { label: '⭐ 周度达人', color: '#7B1FA2' };
    if (d >= 3) return { label: '✨ 连续签到中', color: theme.primary };
    return null;
  };
  const milestone = getMilestoneInfo();

  const handlePressNotifications = () => {
    Toast.show({ type: 'info', text1: '通知中心开发中', text2: '后续版本将支持消息提醒', visibilityTime: 2200 });
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot} safeAreaEdges={['left', 'right', 'bottom']}>
      <ScrollView
        contentContainerStyle={[s.scrollContainer, { paddingBottom: spacing['5xl'] }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <LinearGradient
          colors={['#FF8A65', '#FFB74D']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={s.headerGradient}
        >
          <View style={s.header}>
            <View style={s.headerLeft}>
              <Text style={s.logo}>🏥</Text>
              <ThemedText variant="title" color="#fff" style={s.headerTitle}>起了吗</ThemedText>
            </View>
            <View style={s.headerRight}>
              <TouchableOpacity
                style={s.iconButton}
                onPress={handlePressNotifications}
                accessibilityRole="button"
                accessibilityLabel="消息通知"
              >
                <FontAwesome6 name="bell" size={22} color="rgba(255,255,255,0.9)" />
              </TouchableOpacity>
              <TouchableOpacity
                style={s.iconButton}
                onPress={() => router.push('/settings')}
                accessibilityRole="button"
                accessibilityLabel="设置"
              >
                <FontAwesome6 name="gear" size={22} color="rgba(255,255,255,0.9)" />
              </TouchableOpacity>
              <View style={s.avatar}>
                <ThemedText style={s.avatarText}>
                  {user?.username?.charAt(0)?.toUpperCase() || '我'}
                </ThemedText>
              </View>
            </View>
          </View>

          {/* 问候和时间 */}
          <Animated.View
            style={[
              s.greetingSection,
              { opacity: fadeAnim, transform: [{ translateY: slideAnim }] },
            ]}
          >
            <View>
              <ThemedText variant="h2" color="#fff" style={s.greetingText}>
                {getGreeting()}，{user?.username || '朋友'} 👋
              </ThemedText>
              <ThemedText variant="body" color="rgba(255,255,255,0.85)" style={s.greetingSubtext}>
                {new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })}
              </ThemedText>
            </View>
            <View style={s.clockBox}>
              <Text style={s.clockText}>{currentTime}</Text>
            </View>
          </Animated.View>
        </LinearGradient>

        {/* 签到卡片 */}
        <View style={s.checkInSection}>
          <View style={[s.checkInCard, shadows.glow]}>
            <View style={s.checkInLeft}>
              <ThemedText variant="title" color={theme.textPrimary} style={s.checkInTitle}>
                {isCheckedIn ? '今日已签到 ✅' : '每日签到'}
              </ThemedText>
              <ThemedText variant="small" color={theme.textSecondary} style={s.checkInDesc}>
                {isCheckedIn
                  ? `已连续打卡 ${stats.consecutiveDays} 天，继续加油！`
                  : '点击签到，让家人知道你安全'}
              </ThemedText>
              {milestone && (
                <View style={[s.milestoneBadge, { backgroundColor: milestone.color + '18' }]}>
                  <ThemedText variant="caption" color={milestone.color} style={s.milestoneText}>
                    {milestone.label}
                  </ThemedText>
                </View>
              )}
            </View>

            {/* 签到按钮 */}
            <Animated.View style={{ transform: [{ scale: isCheckedIn ? checkInScale : pulseAnim }] }}>
              <TouchableOpacity
                style={[
                  s.checkInButton,
                  isCheckedIn ? s.checkInButtonDone : s.checkInButtonPending,
                  checkInLoading && s.checkInButtonLoading,
                ]}
                onPress={handleCheckIn}
                disabled={isCheckedIn || checkInLoading}
                activeOpacity={0.88}
                accessibilityRole="button"
                accessibilityLabel={isCheckedIn ? '今日已签到' : '点击完成签到'}
              >
                {checkInLoading ? (
                  <FontAwesome6 name="spinner" size={28} color="#fff" />
                ) : isCheckedIn ? (
                  <FontAwesome6 name="circle-check" size={28} color="#fff" />
                ) : (
                  <FontAwesome6 name="hand-point-up" size={28} color="#fff" />
                )}
                <ThemedText variant="caption" color="#fff" style={s.checkInBtnLabel}>
                  {checkInLoading ? '签到中' : isCheckedIn ? '已打卡' : '签 到'}
                </ThemedText>
              </TouchableOpacity>
            </Animated.View>
          </View>
        </View>

        {/* 快捷功能 */}
        <View style={s.actionsSection}>
          <ThemedText variant="h3" color={theme.textPrimary} style={s.sectionTitle}>
            快捷功能
          </ThemedText>
          <View style={[s.actionsGrid, isTablet && s.actionsGridTablet]}>
            {QUICK_ACTIONS.map((action, idx) => (
              <Animated.View
                key={action.id}
                style={[
                  s.actionCardWrap,
                  { width: cardWidth, transform: [{ scale: actionScales[idx] }] },
                ]}
              >
                <TouchableOpacity
                  style={[s.actionCard, shadows.medium]}
                  onPress={() => handleActionPress(action.route, idx)}
                  onPressIn={() => onActionPressIn(idx)}
                  onPressOut={() => onActionPressOut(idx)}
                  activeOpacity={1}
                  accessibilityRole="button"
                  accessibilityLabel={action.label}
                >
                  <LinearGradient
                    colors={[action.color + 'EE', action.color + 'CC']}
                    style={s.actionCardGradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                  >
                    <Text style={s.actionEmoji}>{action.emoji}</Text>
                    <FontAwesome6 name={action.icon as any} size={28} color="rgba(255,255,255,0.95)" />
                    <ThemedText variant="smallMedium" color="#fff" style={s.actionLabel}>
                      {action.label}
                    </ThemedText>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            ))}
          </View>
        </View>

        {/* 统计卡片 */}
        <View style={s.statsSection}>
          <ThemedText variant="h3" color={theme.textPrimary} style={s.sectionTitle}>
            签到记录
          </ThemedText>
          <View style={[s.statsCard, shadows.medium]}>
            <StatItem
              value={stats.consecutiveDays}
              label="连续天数"
              icon="fire"
              color={theme.error}
            />
            <View style={s.statsDivider} />
            <StatItem
              value={stats.totalCheckIns}
              label="累计签到"
              icon="calendar-check"
              color={theme.accent}
            />
            <View style={s.statsDivider} />
            <StatItem
              value={isCheckedIn ? 1 : 0}
              label="今日状态"
              icon={isCheckedIn ? 'circle-check' : 'circle-xmark'}
              color={isCheckedIn ? theme.success : theme.textMuted}
              isStatus
              statusLabel={isCheckedIn ? '已签到' : '未签到'}
            />
          </View>
        </View>
      </ScrollView>
    </Screen>
  );
}

function StatItem({
  value,
  label,
  icon,
  color,
  isStatus,
  statusLabel,
}: {
  value: number;
  label: string;
  icon: string;
  color: string;
  isStatus?: boolean;
  statusLabel?: string;
}) {
  return (
    <View style={{
      alignItems: 'center',
      gap: spacing['xs'],
    }}>
      <View style={{
        width: 36,
        height: 36,
        borderRadius: borderRadius.lg,
        backgroundColor: color + '18',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <FontAwesome6 name={icon as any} size={18} color={color} />
      </View>
      {isStatus ? (
        <ThemedText variant="bodyMedium" color={color}>{statusLabel}</ThemedText>
      ) : (
        <Text style={{ fontSize: 16, fontWeight: '600', color }}>{value}</Text>
      )}
      <ThemedText variant="caption" color="textSecondary">{label}</ThemedText>
    </View>
  );
}

const createStyles = (theme: CreateStylesTheme) => StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
  },
  headerGradient: {
    paddingBottom: spacing['2xl'],
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing['4xl'],
    paddingBottom: spacing.lg,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  logo: { fontSize: 28 },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#fff',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  iconButton: {
    padding: spacing.sm,
    borderRadius: borderRadius.full,
    backgroundColor: 'rgba(255,255,255,0.2)',
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: borderRadius.full,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
  },
  greetingSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
  },
  greetingText: {
    fontSize: 22,
    fontWeight: '700',
    color: '#fff',
    marginBottom: spacing.xs,
  },
  greetingSubtext: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.85)',
  },
  clockBox: {
    alignItems: 'flex-end',
  },
  clockText: {
    fontSize: 26,
    fontWeight: '700',
    color: '#fff',
    fontVariant: ['tabular-nums'],
  },

  // 签到卡片
  checkInSection: {
    paddingHorizontal: spacing.lg,
    marginTop:  spacing.xl,
    marginBottom: spacing.lg,
  },
  checkInCard: {
    backgroundColor: theme.backgroundDefault,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.lg,
  },
  checkInLeft: {
    flex: 1,
  },
  checkInTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: spacing.xs,
    color: theme.textPrimary,
  },
  checkInDesc: {
    fontSize: 13,
    color: theme.textSecondary,
    lineHeight: 18,
  },
  milestoneBadge: {
    marginTop: spacing.sm,
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: 3,
    borderRadius: borderRadius.full,
  },
  milestoneText: {
    fontSize: 11,
    fontWeight: '600',
  },
  checkInButton: {
    width: 76,
    height: 76,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 4,
  },
  checkInButtonPending: {
    backgroundColor: theme.primary,
  },
  checkInButtonDone: {
    backgroundColor: theme.success,
  },
  checkInButtonLoading: {
    opacity: 0.7,
  },
  checkInBtnLabel: {
    fontSize: 11,
    color: '#fff',
    fontWeight: '600',
  },

  // 快捷功能
  actionsSection: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: theme.textPrimary,
    marginBottom: spacing.md,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  actionsGridTablet: {
    justifyContent: 'flex-start',
  },
  actionCardWrap: {
    // width 由计算决定
  },
  actionCard: {
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
    aspectRatio: 1,
  },
  actionCardGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
    gap: spacing.sm,
  },
  actionEmoji: {
    fontSize: 24,
    position: 'absolute',
    top: 10,
    right: 12,
    opacity: 0.3,
  },
  actionLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#fff',
    textAlign: 'center',
  },

  // 统计
  statsSection: {
    paddingHorizontal: spacing.lg,
  },
  statsCard: {
    backgroundColor: theme.backgroundDefault,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statsDivider: {
    width: 1,
    backgroundColor: theme.borderLight,
    marginVertical: spacing.sm,
  },
  statItem: {
    alignItems: 'center',
    gap: spacing.xs,
    flex: 1,
  },
  statIconWrap: {
    width: 44,
    height: 44,
    borderRadius: borderRadius.lg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: theme.textPrimary,
  },
  statLabel: {
    fontSize: 12,
    color: theme.textSecondary,
  },
});
