/**
 * 首页 - 签到页面（温暖守护风格）
 * 温暖守护风格：晨光橙 + 生命绿
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Animated,
  Platform,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { FontAwesome6 } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  Shadows,
  Animation,
} from '@/constants/theme-warm';
import { useAuth } from '@/contexts/AuthContext';
import { checkInService } from '@/services/checkin';

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  scrollContainer: {
    flexGrow: 1,
    paddingBottom: Spacing['5xl'],
  },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.lg,
  },

  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },

  logo: {
    fontSize: 32,
  },

  headerTitle: {
    ...Typography.title,
    color: Colors.textPrimary,
  },

  headerRight: {
    flexDirection: 'row',
    gap: Spacing.md,
  },

  iconButton: {
    padding: Spacing.sm,
  },

  avatar: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
  },

  heroSection: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing['2xl'],
  },

  greetingCard: {
    borderRadius: BorderRadius.xl,
    overflow: 'hidden',
    ...Shadows.glow,
  },

  greetingGradient: {
    padding: Spacing.xl,
  },

  greetingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },

  greetingText: {
    ...Typography.h2,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
  },

  greetingSubtext: {
    ...Typography.body,
    color: Colors.textPrimary,
  },

  weatherIcon: {
    opacity: 0.3,
  },

  timeDisplay: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },

  currentTime: {
    ...Typography.h1,
    color: Colors.textPrimary,
    fontWeight: '700',
  },

  currentDate: {
    ...Typography.body,
    color: Colors.textPrimary,
  },

  functionSection: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing['2xl'],
  },

  sectionTitle: {
    marginBottom: Spacing.lg,
  },

  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },

  gridItem: {
    flex: 1,
    minWidth: '45%',
    aspectRatio: 1,
    borderRadius: BorderRadius.xl,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.lg,
  },

  gridIcon: {
    marginBottom: Spacing.md,
  },

  gridLabel: {
    ...Typography.smallMedium,
  },

  signInCard: {
    backgroundColor: Colors.primary,
    minWidth: '100%',
  },

  signInCardChecked: {
    backgroundColor: Colors.success,
    minWidth: '100%',
  },

  signInCardDisabled: {
    opacity: 0.6,
  },

  signInIcon: {
    marginBottom: Spacing.sm,
  },

  signInLabel: {
    ...Typography.bodyMedium,
  },

  statsSection: {
    paddingHorizontal: Spacing.lg,
  },

  statsCard: {
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    padding: Spacing.xl,
    ...Shadows.medium,
  },

  statsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },

  statsTitle: {
    ...Typography.title,
    color: Colors.textPrimary,
  },

  statsBadge: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },

  statsBadgeText: {
    ...Typography.captionMedium,
  },

  statsContent: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },

  statItem: {
    alignItems: 'center',
  },

  statValue: {
    ...Typography.h2,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
  },

  statLabel: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
});

// 辅助函数：获取问候语
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好，';
  if (hour < 9) return '早上好，';
  if (hour < 12) return '上午好，';
  if (hour < 14) return '中午好，';
  if (hour < 18) return '下午好，';
  if (hour < 22) return '晚上好，';
  return '夜深了，';
};

// 辅助函数：获取当前时间
const getCurrentTime = () => {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

export default function WarmHomePage() {
  const router = useSafeRouter();
  const { user } = useAuth();

  // 签到状态
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [checkInLoading, setCheckInLoading] = useState(false);
  const [stats, setStats] = useState({ consecutiveDays: 0, totalCheckIns: 0 });

  // 动画状态
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(30));

  // 当前时间
  const [currentTime, setCurrentTime] = useState(getCurrentTime());

  // 加载签到状态和统计
  useEffect(() => {
    loadCheckInStatus();
  }, []);

  const loadCheckInStatus = async () => {
    try {
      const [checkedToday, statsData] = await Promise.all([
        checkInService.isCheckedInToday(),
        checkInService.getCheckInStats(),
      ]);
      setIsCheckedIn(checkedToday);
      setStats(statsData);
    } catch (error) {
      console.error('加载签到状态失败:', error);
    }
  };

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(getCurrentTime());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 动画效果
  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: Animation.normal,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  // 处理签到
  const handleCheckIn = async () => {
    if (isCheckedIn || checkInLoading) return;

    setCheckInLoading(true);
    try {
      await checkInService.checkIn();
      setIsCheckedIn(true);
      await loadCheckInStatus();
      alert('签到成功！');
    } catch (error) {
      console.error('签到失败:', error);
      alert('签到失败，请重试');
    } finally {
      setCheckInLoading(false);
    }
  };

  // 导航函数
  const handlePressSOS = () => {
    router.push('/sos');
  };

  const handlePressContacts = () => {
    router.push('/contacts');
  };

  const handlePressHealth = () => {
    router.push('/health');
  };

  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* 顶部导航栏 */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.logo}>🏥</Text>
            <ThemedText variant="title" color={Colors.textPrimary} style={styles.headerTitle}>
              起了吗
            </ThemedText>
          </View>
          <View style={styles.headerRight}>
            <View style={styles.iconButton}>
              <FontAwesome6 name="bell" size={24} color={Colors.textSecondary} />
            </View>
            <View style={styles.avatar}>
              <FontAwesome6 name="user" size={20} color={Colors.primaryDark} />
            </View>
          </View>
        </View>

        {/* 情感化头部区域 */}
        <View style={styles.heroSection}>
          <Animated.View
            style={[
              styles.greetingCard,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <LinearGradient
              colors={['#FF8A65', '#FFB74D']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.greetingGradient}
            >
              <View style={styles.greetingRow}>
                <View>
                  <ThemedText
                    variant="h2"
                    color={Colors.textPrimary}
                    style={styles.greetingText}
                  >
                    {getGreeting()}{user?.username || '朋友'}
                  </ThemedText>
                  <ThemedText variant="body" color={Colors.textPrimary} style={styles.greetingSubtext}>
                    今天也要保持好心情哦 💫
                  </ThemedText>
                </View>
                <FontAwesome6 name="sun" size={48} color={Colors.backgroundDefault} style={styles.weatherIcon} />
              </View>
              <View style={styles.timeDisplay}>
                <Text style={styles.currentTime}>{currentTime}</Text>
                <Text style={styles.currentDate}>
                  {new Date().toLocaleDateString('zh-CN', {
                    month: 'long',
                    day: 'numeric',
                    weekday: 'long',
                  })}
                </Text>
              </View>
            </LinearGradient>
          </Animated.View>
        </View>

        {/* 功能网格 */}
        <View style={styles.functionSection}>
          <ThemedText variant="h3" color={Colors.textPrimary} style={styles.sectionTitle}>
            今日功能
          </ThemedText>
          <View style={styles.gridContainer}>
            {/* 签到（突出显示） */}
            <View style={styles.gridItem}>
              <View
                style={[
                  styles.signInCard,
                  isCheckedIn && styles.signInCardChecked,
                  checkInLoading && styles.signInCardDisabled,
                  Shadows.glow,
                ]}
              >
                {checkInLoading ? (
                  <FontAwesome6 name="spinner" size={40} color={Colors.backgroundDefault} style={styles.signInIcon} spin />
                ) : isCheckedIn ? (
                  <FontAwesome6 name="circle-check" size={40} color={Colors.backgroundDefault} style={styles.signInIcon} />
                ) : (
                  <FontAwesome6 name="clock" size={40} color={Colors.backgroundDefault} style={styles.signInIcon} />
                )}
                <ThemedText variant="smallMedium" color={Colors.backgroundDefault} style={styles.signInLabel}>
                  {checkInLoading ? '签到中...' : isCheckedIn ? '已签到' : '每日签到'}
                </ThemedText>
              </View>
            </View>

            {/* 紧急求助 */}
            <View style={styles.gridItem}>
              <View
                style={[
                  styles.gridItem,
                  { backgroundColor: Colors.error },
                  Shadows.medium,
                ]}
              >
                <FontAwesome6 name="phone-volume" size={36} color={Colors.backgroundDefault} style={styles.gridIcon} />
                <ThemedText variant="smallMedium" color={Colors.backgroundDefault} style={styles.gridLabel}>
                  SOS求助
                </ThemedText>
              </View>
            </View>

            {/* 联系人 */}
            <View style={styles.gridItem}>
              <View
                style={[
                  styles.gridItem,
                  { backgroundColor: Colors.accent },
                  Shadows.medium,
                ]}
              >
                <FontAwesome6 name="address-book" size={36} color={Colors.backgroundDefault} style={styles.gridIcon} />
                <ThemedText variant="smallMedium" color={Colors.backgroundDefault} style={styles.gridLabel}>
                  紧急联系人
                </ThemedText>
              </View>
            </View>

            {/* 健康档案 */}
            <View style={styles.gridItem}>
              <View
                style={[
                  styles.gridItem,
                  { backgroundColor: Colors.info },
                  Shadows.medium,
                ]}
              >
                <FontAwesome6 name="notes-medical" size={36} color={Colors.backgroundDefault} style={styles.gridIcon} />
                <ThemedText variant="smallMedium" color={Colors.backgroundDefault} style={styles.gridLabel}>
                  健康档案
                </ThemedText>
              </View>
            </View>
          </View>
        </View>

        {/* 统计卡片 */}
        <View style={styles.statsSection}>
          <View style={styles.statsCard}>
            <View style={styles.statsHeader}>
              <ThemedText variant="title" color={Colors.textPrimary} style={styles.statsTitle}>
                签到统计
              </ThemedText>
              <View style={styles.statsBadge}>
                <ThemedText variant="captionMedium" color={Colors.backgroundDefault} style={styles.statsBadgeText}>
                  🔥 连续签到
                </ThemedText>
              </View>
            </View>
            <View style={styles.statsContent}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{stats.consecutiveDays}</Text>
                <Text style={styles.statLabel}>连续天数</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={[styles.statValue, { color: Colors.accent }]}>{stats.totalCheckIns}</Text>
                <Text style={styles.statLabel}>总签到</Text>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
    </Screen>
  );
}
