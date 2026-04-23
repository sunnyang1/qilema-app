/**
 * 设置页面
 * 主题切换、通知设置、关于我们
 */
import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  useWindowDimensions,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  FadeIn,
  FadeInDown,
  SlideInRight,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/contexts/AuthContext';
import { storage } from '@/services/storage';
import { useThemeContext } from '@/design-system/ThemeProvider';

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

// 主题选项
const THEME_OPTIONS = [
  { value: 'system', label: '跟随系统', icon: 'mobile-screen' as const },
  { value: 'light', label: '浅色模式', icon: 'sun' as const },
  { value: 'dark', label: '深色模式', icon: 'moon' as const },
];

interface SettingItemProps {
  icon: string;
  iconColor?: string;
  title: string;
  subtitle?: string;
  rightElement?: React.ReactNode;
  onPress?: () => void;
  showArrow?: boolean;
  delay?: number;
}

function SettingItem({
  icon,
  iconColor = '#007AFF',
  title,
  subtitle,
  rightElement,
  onPress,
  showArrow = true,
  delay = 0,
}: SettingItemProps) {
  const { theme } = useTheme();
  const scale = useSharedValue(1);

  const handlePressIn = () => {
    scale.value = withSpring(0.98, { damping: 15, stiffness: 400 });
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 15, stiffness: 400 });
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View entering={FadeInDown.delay(delay).springify()}>
      <AnimatedTouchable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        activeOpacity={0.9}
        style={animatedStyle}
      >
        <View style={[styles.settingItem, { backgroundColor: theme.backgroundCard }]}>
          <View style={[styles.iconContainer, { backgroundColor: iconColor + '20' }]}>
            <FontAwesome6 name={icon as any} size={18} color={iconColor} />
          </View>
          <View style={styles.settingContent}>
            <Text style={[styles.settingTitle, { color: theme.textPrimary }]}>{title}</Text>
            {subtitle && (
              <Text style={[styles.settingSubtitle, { color: theme.textMuted }]}>
                {subtitle}
              </Text>
            )}
          </View>
          {rightElement}
          {showArrow && (
            <FontAwesome6
              name="chevron-right"
              size={14}
              color={theme.textMuted}
              style={{ marginLeft: 8 }}
            />
          )}
        </View>
      </AnimatedTouchable>
    </Animated.View>
  );
}

interface SectionHeaderProps {
  title: string;
}

function SectionHeader({ title }: SectionHeaderProps) {
  const { theme } = useTheme();
  return (
    <Text style={[styles.sectionHeader, { color: theme.textMuted }]}>
      {title}
    </Text>
  );
}

export default function SettingsScreen() {
  const router = useRouter();
  const { width } = useWindowDimensions();
  const { theme, isDark } = useTheme();
  const { user, logout } = useAuth();
  const { preference, setPreference } = useThemeContext();

  const isTablet = width >= 768;
  const maxWidth = isTablet ? 600 : width;

  // 本地状态
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [vibrationEnabled, setVibrationEnabled] = useState(true);
  const [reduceMotion, setReduceMotion] = useState(false);

  // 主题切换
  const handleThemeChange = useCallback((themeValue: string) => {
    setPreference(themeValue as 'system' | 'light' | 'dark');
    if (Platform.OS !== 'web') {
      Haptics.selectionAsync();
    }
  }, [setPreference]);

  // 退出登录
  const handleLogout = useCallback(() => {
    Alert.alert(
      '退出登录',
      '确定要退出当前账号吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '退出',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/login');
          },
        },
      ]
    );
  }, [logout, router]);

  // 检查更新
  const handleCheckUpdate = useCallback(async () => {
    if (Platform.OS !== 'web') {
      // 模拟检查更新功能
      Alert.alert('已是最新版本', '当前版本已是最新');
    } else {
      Alert.alert('提示', 'Web 版本无需更新');
    }
  }, []);

  // 清除缓存
  const handleClearCache = useCallback(() => {
    Alert.alert(
      '清除缓存',
      '确定要清除本地缓存吗？这不会删除您的账号数据。',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '清除',
          onPress: () => {
            if (Platform.OS !== 'web') {
              Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            }
            Alert.alert('清除成功', '缓存已清除');
          },
        },
      ]
    );
  }, []);

  return (
    <View style={[styles.container, { backgroundColor: theme.backgroundRoot }]}>
      {/* 渐变 Header */}
      <LinearGradient
        colors={isDark ? ['#2C2C2C', '#1E1E1E'] : ['#FFF5F0', '#FFFFFF']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <FontAwesome6 name="arrow-left" size={20} color={theme.textPrimary} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: theme.textPrimary }]}>设置</Text>
          <View style={{ width: 40 }} />
        </View>

        {/* 用户信息卡片 */}
        <Animated.View
          entering={FadeIn.duration(500)}
          style={[styles.userCard, { backgroundColor: theme.backgroundCard }]}
        >
          <LinearGradient
            colors={isDark ? ['#3C3C3C', '#2C2C2C'] : ['#FFFAF8', '#FFF5F0']}
            style={styles.userGradient}
          >
            <View style={[styles.avatar, { backgroundColor: theme.primary }]}>
              <Text style={styles.avatarText}>
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={[styles.userName, { color: theme.textPrimary }]}>
                {user?.username || '用户'}
              </Text>
              <Text style={[styles.userPhone, { color: theme.textMuted }]}>
                {user?.phone || user?.email || '未设置联系方式'}
              </Text>
            </View>
            <TouchableOpacity
              onPress={() => router.push('/profile')}
              style={[styles.editButton, { borderColor: theme.primary }]}
            >
              <FontAwesome6 name="pen" size={14} color={theme.primary} />
            </TouchableOpacity>
          </LinearGradient>
        </Animated.View>
      </LinearGradient>

      {/* 设置列表 */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={[styles.scrollContent, { maxWidth }]}
        showsVerticalScrollIndicator={false}
      >
        {/* 外观设置 */}
        <SectionHeader title="外观" />
        <View style={styles.section}>
          <View style={[styles.themeSelector, { backgroundColor: theme.backgroundCard }]}>
            {THEME_OPTIONS.map((option, index) => {
              const isSelected = preference === option.value;
              return (
                <TouchableOpacity
                  key={option.value}
                  onPress={() => handleThemeChange(option.value)}
                  style={[
                    styles.themeOption,
                    isSelected && { backgroundColor: theme.primary + '20' },
                  ]}
                >
                  <FontAwesome6
                    name={option.icon}
                    size={20}
                    color={isSelected ? theme.primary : theme.textMuted}
                  />
                  <Text
                    style={[
                      styles.themeLabel,
                      { color: isSelected ? theme.primary : theme.textSecondary },
                    ]}
                  >
                    {option.label}
                  </Text>
                  {isSelected && (
                    <View style={[styles.checkmark, { backgroundColor: theme.primary }]}>
                      <FontAwesome6 name="check" size={10} color="#FFFFFF" />
                    </View>
                  )}
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* 通知设置 */}
        <SectionHeader title="通知" />
        <View style={styles.section}>
          <SettingItem
            icon="bell"
            iconColor="#FF9500"
            title="推送通知"
            subtitle="接收签到提醒和紧急通知"
            rightElement={
              <Switch
                value={notificationsEnabled}
                onValueChange={setNotificationsEnabled}
                trackColor={{ false: theme.border, true: theme.primary }}
                thumbColor="#FFFFFF"
              />
            }
            showArrow={false}
          />
          <SettingItem
            icon="volume-up"
            iconColor="#5856D6"
            title="提示音"
            subtitle="通知声音"
            rightElement={
              <Switch
                value={soundEnabled}
                onValueChange={setSoundEnabled}
                trackColor={{ false: theme.border, true: theme.primary }}
                thumbColor="#FFFFFF"
              />
            }
            showArrow={false}
          />
          <SettingItem
            icon="mobile-screen-button"
            iconColor="#34C759"
            title="震动"
            subtitle="触觉反馈"
            rightElement={
              <Switch
                value={vibrationEnabled}
                onValueChange={setVibrationEnabled}
                trackColor={{ false: theme.border, true: theme.primary }}
                thumbColor="#FFFFFF"
              />
            }
            showArrow={false}
          />
          <SettingItem
            icon="wand-magic-sparkles"
            iconColor="#FF2D55"
            title="减少动画"
            subtitle="降低界面动效"
            rightElement={
              <Switch
                value={reduceMotion}
                onValueChange={setReduceMotion}
                trackColor={{ false: theme.border, true: theme.primary }}
                thumbColor="#FFFFFF"
              />
            }
            showArrow={false}
          />
        </View>

        {/* 数据与存储 */}
        <SectionHeader title="数据与存储" />
        <View style={styles.section}>
          <SettingItem
            icon="trash"
            iconColor="#FF3B30"
            title="清除缓存"
            subtitle="释放存储空间"
            onPress={handleClearCache}
          />
        </View>

        {/* 关于 */}
        <SectionHeader title="关于" />
        <View style={styles.section}>
          <SettingItem
            icon="cloud-arrow-down"
            iconColor="#007AFF"
            title="检查更新"
            subtitle="当前版本 1.0.0"
            onPress={handleCheckUpdate}
          />
          <SettingItem
            icon="file-contract"
            iconColor="#8E8E93"
            title="用户协议"
            onPress={() => router.push('/agreement')}
          />
          <SettingItem
            icon="shield-halved"
            iconColor="#8E8E93"
            title="隐私政策"
            onPress={() => router.push('/privacy')}
          />
          <SettingItem
            icon="info-circle"
            iconColor="#8E8E93"
            title="关于我们"
            subtitle="起了吗 App v1.0.0"
            onPress={() => Alert.alert('起了吗 App', '独居人群紧急医疗救助平台\n版本 1.0.0')}
          />
        </View>

        {/* 退出登录 */}
        <Animated.View entering={FadeInDown.delay(300).springify()}>
          <TouchableOpacity
            onPress={handleLogout}
            style={[styles.logoutButton, { backgroundColor: theme.error + '15' }]}
          >
            <FontAwesome6 name="right-from-bracket" size={18} color={theme.error} />
            <Text style={[styles.logoutText, { color: theme.error }]}>退出登录</Text>
          </TouchableOpacity>
        </Animated.View>

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  userCard: {
    marginHorizontal: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  userGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  userInfo: {
    flex: 1,
    marginLeft: 14,
  },
  userName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 2,
  },
  userPhone: {
    fontSize: 13,
  },
  editButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
  },
  sectionHeader: {
    fontSize: 13,
    fontWeight: '600',
    marginTop: 24,
    marginBottom: 8,
    marginLeft: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  section: {
    marginBottom: 8,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    borderRadius: 12,
    marginBottom: 6,
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 15,
    fontWeight: '500',
  },
  settingSubtitle: {
    fontSize: 12,
    marginTop: 1,
  },
  themeSelector: {
    flexDirection: 'row',
    borderRadius: 12,
    padding: 6,
  },
  themeOption: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 10,
    position: 'relative',
  },
  themeLabel: {
    fontSize: 12,
    marginTop: 6,
    fontWeight: '500',
  },
  checkmark: {
    position: 'absolute',
    top: 6,
    right: 6,
    width: 16,
    height: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginTop: 24,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});
