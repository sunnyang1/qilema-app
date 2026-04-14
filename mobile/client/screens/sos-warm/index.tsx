/**
 * SOS 紧急求助页面（优化版）
 * 设计重点：清晰、醒目、快速响应
 * UI/UX 优化：
 * - 使用 Pressable 替代 TouchableOpacity
 * - 添加无障碍属性
 * - 优化触摸反馈和 hitSlop
 * - 改进动画性能
 * - 增强视觉层次和对比度
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Platform,
  AccessibilityInfo,
  Pressable,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import EmptyState from '@/components/EmptyState';
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
import { sosService, EmergencyContact, SOSRequest } from '@/services/sos';
import Toast from 'react-native-toast-message';

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  // 顶部导航
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.lg,
  },

  backButton: {
    marginRight: Spacing.md,
  },

  headerTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
    flex: 1,
  },

  // 主要内容区
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing['2xl'],
  },

  // 警告提示区
  warningSection: {
    alignItems: 'center',
    marginBottom: Spacing['3xl'],
  },

  warningIcon: {
    fontSize: 80,
    marginBottom: Spacing.lg,
  },

  warningTitle: {
    ...Typography.h1,
    color: Colors.error,
    textAlign: 'center',
    marginBottom: Spacing.md,
  },

  warningSubtitle: {
    ...Typography.body,
    color: Colors.textPrimary,
    textAlign: 'center',
    opacity: 0.85,
  },

  // 紧急联系人列表
  contactsSection: {
    marginBottom: Spacing['3xl'],
  },

  sectionTitle: {
    ...Typography.title,
    color: Colors.textPrimary,
    marginBottom: Spacing.lg,
  },

  contactCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
    ...Shadows.medium,
    overflow: 'hidden',
  },

  contactAvatar: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.error,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },

  contactAvatarIcon: {
    fontSize: 24,
  },

  contactInfo: {
    flex: 1,
  },

  contactName: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
  },

  contactRelation: {
    ...Typography.small,
    color: Colors.textSecondary,
  },

  contactPhone: {
    ...Typography.smallMedium,
    color: Colors.primary,
  },

  callButton: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    ...Shadows.soft,
  },

  // 底部操作区
  actionsSection: {
    gap: Spacing.md,
  },

  // 主要按钮样式
  primaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.xl,
    ...Shadows.glow,
  },

  primaryButtonIcon: {
    fontSize: 24,
    marginRight: Spacing.md,
  },

  primaryButtonText: {
    ...Typography.bodyMedium,
    color: Colors.backgroundDefault,
  },

  // 次要按钮样式
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: BorderRadius.xl,
    borderWidth: 2,
    borderColor: Colors.border,
    backgroundColor: Colors.backgroundDefault,
  },

  secondaryButtonIcon: {
    fontSize: 24,
    marginRight: Spacing.md,
  },

  secondaryButtonText: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
  },
});

// 紧急联系人数据
const emergencyContacts: EmergencyContact[] = [
  {
    id: '1',
    name: '李医生',
    relation: '家庭医生',
    phone: '138****5678',
    priority: 1,
    isDefault: true,
  },
  {
    id: '2',
    name: '张先生',
    relation: '儿子',
    phone: '139****1234',
    priority: 2,
    isDefault: false,
  },
];

export default function SOSPage() {
  const router = useSafeRouter();

  // 状态管理
  const [contacts, setContacts] = useState<EmergencyContact[]>(emergencyContacts);
  const [loading, setLoading] = useState(false);
  const [sosRequest, setSosRequest] = useState<SOSRequest | null>(null);

  // 脉动动画（仅用于 SOS 按钮）
  const [pulseAnim] = useState(new Animated.Value(1));
  const [shakeAnim] = useState(new Animated.Value(0));

  // 按钮按压状态
  const [sosPressed, setSosPressed] = useState(false);

  // 检测屏幕阅读器状态
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);

  useEffect(() => {
    // 加载紧急联系人
    loadContacts();

    // 检测屏幕阅读器
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      (enabled) => setIsScreenReaderEnabled(enabled)
    );

    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);

    return () => {
      subscription?.remove();
    };
  }, []);

  // 加载紧急联系人
  const loadContacts = async () => {
    try {
      const data = await sosService.getEmergencyContacts();
      setContacts(data);
    } catch (error) {
      console.error('加载紧急联系人失败:', error);
      // 使用默认数据
      setContacts(emergencyContacts);
    }
  };

  // 脉动动画效果（仅当屏幕阅读器关闭时播放）
  useEffect(() => {
    if (!isScreenReaderEnabled) {
      const pulseAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      );

      pulseAnimation.start();

      return () => {
        pulseAnimation.stop();
      };
    }
  }, [isScreenReaderEnabled]);

  // 抖动动画效果 + SOS 呼叫逻辑
  const handleSOSPress = useCallback(async () => {
    if (loading) return;

    setLoading(true);

    try {
      // 播放抖动动画
      Animated.sequence([
        Animated.timing(shakeAnim, {
          toValue: 10,
          duration: 50,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: -10,
          duration: 50,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: 5,
          duration: 50,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: -5,
          duration: 50,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: 0,
          duration: 50,
          useNativeDriver: true,
        }),
      ]).start();

      // 发起 SOS 请求
      const request = await sosService.createSOSRequest();
      setSosRequest(request);

      // 显示成功提示
      Toast.show({
        type: 'success',
        text1: '求助已发送',
        text2: '已通知紧急联系人和急救中心',
        visibilityTime: 2600,
      });

      // 拨打 120
      await sosService.callEmergencyServices();

      // 导航到 SOS 状态页面
      router.push('/sos-status', { requestId: request.id });
    } catch (error: any) {
      console.error('SOS 求助失败:', error);
      const message = error.response?.data?.message || error.message || '发起求助失败，请重试';
      Toast.show({
        type: 'error',
        text1: '求助失败',
        text2: message,
        visibilityTime: 2600,
      });
    } finally {
      setLoading(false);
    }
  }, [loading, router]);

  // 拨打联系人电话
  const handleCallContact = useCallback(async (contactId: string, contactName: string) => {
    try {
      await sosService.callContact(contactId);
      Toast.show({
        type: 'success',
        text1: '呼叫已发起',
        text2: `正在联系 ${contactName}`,
        visibilityTime: 2200,
      });
    } catch (error: any) {
      console.error('拨打联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '呼叫失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 2600,
      });
    }
  }, []);

  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      {/* 顶部导航 */}
      <View style={styles.header} accessible accessibilityLabel="页面顶部导航">
        <Pressable
          style={styles.backButton}
          onPress={() => router.back()}
          hitSlop={12}
          android_ripple={{ color: 'rgba(0,0,0,0.1)', radius: 24 }}
          accessibilityLabel="返回"
          accessibilityHint="点击返回上一页"
          accessibilityRole="button"
        >
          <FontAwesome6 name="arrow-left" size={24} color={Colors.textPrimary} />
        </Pressable>
        <ThemedText variant="h1" color={Colors.textPrimary} style={styles.headerTitle}>
          紧急求助
        </ThemedText>
      </View>

      {/* 主要内容 */}
      <View style={styles.content}>
        {/* 警告提示 */}
        <View
          style={styles.warningSection}
          accessible
          accessibilityLabel="紧急求助确认"
          accessibilityRole="alert"
        >
          <Animated.View
            style={[
              {
                transform: [{ scale: pulseAnim }],
              },
            ]}
          >
            <FontAwesome6
              name="triangle-exclamation"
              size={80}
              color={Colors.error}
              style={styles.warningIcon}
              accessible={false}
            />
          </Animated.View>
          <ThemedText variant="h1" color={Colors.error} style={styles.warningTitle}>
            确认发起紧急求助？
          </ThemedText>
          <ThemedText variant="body" color={Colors.textPrimary} style={styles.warningSubtitle}>
            系统将自动拨打以下联系人并发送位置信息
          </ThemedText>
        </View>

        {/* 紧急联系人列表 */}
        <View style={styles.contactsSection} accessible accessibilityLabel="紧急联系人列表">
          <ThemedText variant="title" color={Colors.textPrimary} style={styles.sectionTitle}>
            紧急联系人
          </ThemedText>
          {contacts.length === 0 ? (
            <EmptyState
              icon="address-book"
              title="暂无可通知联系人"
              subtitle="先添加紧急联系人，SOS 才能同步通知家属"
              actionLabel="去添加联系人"
              onActionPress={() => router.push('/contacts')}
            />
          ) : contacts.map((contact) => (
            <Pressable
              key={contact.id}
              style={styles.contactCard}
              onPress={() => handleCallContact(contact.id, contact.name)}
              disabled={loading}
              hitSlop={12}
              android_ripple={{ color: 'rgba(0,0,0,0.1)' }}
              accessibilityLabel={`${contact.name}，${contact.relation}，电话${contact.phone}`}
              accessibilityHint="点击拨打联系人电话"
              accessibilityRole="button"
            >
              <View style={styles.contactAvatar} accessible={false}>
                <FontAwesome6
                  name="user-doctor"
                  size={24}
                  color={Colors.backgroundDefault}
                  style={styles.contactAvatarIcon}
                />
              </View>
              <View style={styles.contactInfo}>
                <ThemedText variant="bodyMedium" color={Colors.textPrimary}>
                  {contact.name}
                </ThemedText>
                <ThemedText variant="small" color={Colors.textSecondary}>
                  {contact.relation}
                </ThemedText>
                <ThemedText variant="smallMedium" color={Colors.primary}>
                  {contact.phone}
                </ThemedText>
              </View>
              <View
                style={[styles.callButton, loading && { opacity: 0.5 }]}
                accessible
                accessibilityLabel={`拨打${contact.name}的电话`}
                accessibilityRole="button"
              >
                <FontAwesome6 name="phone" size={20} color={Colors.backgroundDefault} />
              </View>
            </Pressable>
          ))}
        </View>

        {/* 底部操作区 */}
        <View style={styles.actionsSection} accessible accessibilityLabel="操作按钮区域">
          {/* SOS 按钮 */}
          <Animated.View
            style={{
              transform: [{ translateX: shakeAnim }, { scale: sosPressed ? 0.95 : 1 }],
            }}
          >
            <Pressable
              style={[
                styles.primaryButton,
                { backgroundColor: loading ? Colors.textMuted : Colors.error },
                loading && { opacity: 0.7 }
              ]}
              onPress={handleSOSPress}
              onPressIn={() => !loading && setSosPressed(true)}
              onPressOut={() => setSosPressed(false)}
              disabled={loading}
              hitSlop={12}
              android_ripple={{ color: 'rgba(255,255,255,0.3)', radius: 100 }}
              accessibilityLabel={loading ? "正在发送求助请求" : "立即呼叫 120 急救电话"}
              accessibilityHint="点击后将自动拨打 120 急救电话并发送位置"
              accessibilityRole="button"
              accessibilityState={{ disabled: loading }}
            >
              {loading ? (
                <FontAwesome6
                  name="spinner"
                  size={24}
                  color={Colors.backgroundDefault}
                  style={styles.primaryButtonIcon}
                  spin
                />
              ) : (
                <FontAwesome6
                  name="phone-volume"
                  size={24}
                  color={Colors.backgroundDefault}
                  style={styles.primaryButtonIcon}
                />
              )}
              <ThemedText variant="bodyMedium" color={Colors.backgroundDefault} style={styles.primaryButtonText}>
                {loading ? '发送中...' : '立即呼叫 120'}
              </ThemedText>
            </Pressable>
          </Animated.View>

          {/* 取消按钮 */}
          <Pressable
            style={styles.secondaryButton}
            onPress={() => router.back()}
            hitSlop={12}
            android_ripple={{ color: 'rgba(0,0,0,0.1)', radius: 100 }}
            accessibilityLabel="取消求助"
            accessibilityHint="点击取消紧急求助并返回"
            accessibilityRole="button"
          >
            <FontAwesome6
              name="xmark"
              size={24}
              color={Colors.textPrimary}
              style={styles.secondaryButtonIcon}
            />
            <ThemedText variant="bodyMedium" color={Colors.textPrimary} style={styles.secondaryButtonText}>
              取消求助
            </ThemedText>
          </Pressable>
        </View>
      </View>
      <Toast />
    </Screen>
  );
}
