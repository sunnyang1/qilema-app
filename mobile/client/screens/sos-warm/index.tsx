/**
 * SOS 紧急求助页面（增强版）
 * 改进：
 * - 3 秒倒计时防误触确认机制
 * - 全屏紧急感 Header 渐变
 * - 大号 SOS 按钮脉冲动画
 * - 触觉震动反馈
 * - 联系人优先级视觉
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Platform,
  AccessibilityInfo,
  Pressable,
  TouchableOpacity,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import EmptyState from '@/components/EmptyState';
import { FontAwesome6 } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import {
  spacing,
  borderRadius,
  typography,
} from '@/design-system';
import { createShadows } from '@/design-system';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import { sosService, EmergencyContact, SOSRequest } from '@/services/sos';
import Toast from 'react-native-toast-message';

const { width } = Dimensions.get('window');
const SOS_BTN_SIZE = Math.min(width * 0.45, 200);

// 静态占位联系人（API 失败时使用）
const FALLBACK_CONTACTS: EmergencyContact[] = [
  { id: 1, contactId: 'fb-1', userId: '', name: '李医生', phone: '138****5678', relationship: '家庭医生', priority: 1, notificationChannels: ['app'], isDefault: true, createdAt: '', updatedAt: '' },
  { id: 2, contactId: 'fb-2', userId: '', name: '张先生', phone: '139****1234', relationship: '儿子', priority: 2, notificationChannels: ['app'], isDefault: false, createdAt: '', updatedAt: '' },
];

export default function SOSPage() {
  const router = useSafeRouter();
  const { theme, isDark } = useTheme();
  const shadows = createShadows(theme.shadow, theme.shadowStrong);
  const s = createStyles(theme);

  const [contacts, setContacts] = useState<EmergencyContact[]>(FALLBACK_CONTACTS);
  const [loading, setLoading] = useState(false);
  const [sosRequest, setSosRequest] = useState<SOSRequest | null>(null);
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);

  // 倒计时状态：null=未开始，>0=倒计时中，0=触发
  const [countdown, setCountdown] = useState<number | null>(null);
  const countdownTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 动画
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const shakeAnim = useRef(new Animated.Value(0)).current;
  const countdownScale = useRef(new Animated.Value(1)).current;
  const pulseLoopRef = useRef<Animated.CompositeAnimation | null>(null);

  useEffect(() => {
    loadContacts();
    const sub = AccessibilityInfo.addEventListener('screenReaderChanged', setIsScreenReaderEnabled);
    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);
    return () => { sub?.remove(); stopCountdown(); };
  }, []);

  // 脉冲动画
  useEffect(() => {
    if (!isScreenReaderEnabled && !loading) {
      const loop = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.08, duration: 900, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 900, useNativeDriver: true }),
        ])
      );
      pulseLoopRef.current = loop;
      loop.start();
      return () => loop.stop();
    }
  }, [isScreenReaderEnabled, loading]);

  const loadContacts = async () => {
    try {
      const data = await sosService.getEmergencyContacts();
      if (data && data.length > 0) setContacts(data);
    } catch {
      setContacts(FALLBACK_CONTACTS);
    }
  };

  // 开始倒计时
  const startCountdown = useCallback(() => {
    if (loading || countdown !== null) return;

    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }

    setCountdown(3);
    // 倒计时动画
    Animated.loop(
      Animated.sequence([
        Animated.timing(countdownScale, { toValue: 1.15, duration: 400, useNativeDriver: true }),
        Animated.timing(countdownScale, { toValue: 1, duration: 400, useNativeDriver: true }),
      ])
    ).start();

    countdownTimerRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev === null || prev <= 1) {
          if (countdownTimerRef.current) {
            clearInterval(countdownTimerRef.current);
            countdownTimerRef.current = null;
          }
          countdownScale.stopAnimation();
          countdownScale.setValue(1);
          if (prev === 1) {
            // 触发 SOS
            triggerSOS();
          }
          return null;
        }
        if (Platform.OS !== 'web') {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        }
        return prev - 1;
      });
    }, 1000);
  }, [loading, countdown]);

  // 取消倒计时
  const stopCountdown = useCallback(() => {
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current);
      countdownTimerRef.current = null;
    }
    countdownScale.stopAnimation();
    countdownScale.setValue(1);
    setCountdown(null);
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
  }, []);

  // 执行 SOS
  const triggerSOS = useCallback(async () => {
    if (loading) return;
    setLoading(true);

    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }

    // 抖动动画
    Animated.sequence([
      Animated.timing(shakeAnim, { toValue: 10, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -10, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 6, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -6, duration: 50, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 0, duration: 50, useNativeDriver: true }),
    ]).start();

    try {
      const request = await sosService.createSOSRequest();
      setSosRequest(request);
      Toast.show({ type: 'success', text1: '🚨 求助已发送', text2: '已通知紧急联系人和急救中心', visibilityTime: 2600 });
      await sosService.callEmergencyServices();
      router.push('/sos-status', { requestId: request.id });
    } catch (error: any) {
      const msg = error.response?.data?.message || error.message || '发起求助失败，请重试';
      Toast.show({ type: 'error', text1: '求助失败', text2: msg, visibilityTime: 2600 });
    } finally {
      setLoading(false);
    }
  }, [loading, router]);

  const handleCallContact = useCallback(async (contactId: string, contactName: string) => {
    try {
      await sosService.callContact(contactId);
      Toast.show({ type: 'success', text1: '呼叫已发起', text2: `正在联系 ${contactName}`, visibilityTime: 2200 });
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '呼叫失败', text2: error.message || '请稍后重试', visibilityTime: 2600 });
    }
  }, []);

  const priorityColor = (p: number) => {
    if (p === 1) return theme.error;
    if (p === 2) return theme.warning;
    return theme.info;
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot} statusBarStyle="light">
      {/* 顶部紧急渐变 Header */}
      <LinearGradient
        colors={['#B71C1C', '#E53935', '#EF5350']}
        style={s.emergencyHeader}
      >
        <Pressable
          style={s.backButton}
          onPress={() => router.back()}
          hitSlop={16}
          accessibilityRole="button"
          accessibilityLabel="返回"
        >
          <FontAwesome6 name="arrow-left" size={22} color="#fff" />
        </Pressable>
        <View style={s.headerCenter}>
          <FontAwesome6 name="triangle-exclamation" size={20} color="rgba(255,255,255,0.9)" />
          <ThemedText variant="title" color="#fff" style={s.headerTitle}>紧急求助</ThemedText>
        </View>
        <View style={{ width: 40 }} />
      </LinearGradient>

      {/* 主内容 */}
      <View style={s.content}>
        {/* SOS 大按钮 */}
        <View style={s.sosBtnSection}>
          <ThemedText variant="body" color={theme.textSecondary} style={s.sosBtnHint}>
            {countdown !== null
              ? `将在 ${countdown} 秒后发送求助，长按可取消`
              : '长按下方按钮 3 秒触发求助'}
          </ThemedText>

          <Animated.View
            style={[
              s.sosPulseRing,
              { transform: [{ scale: pulseAnim }] },
            ]}
          />

          <Animated.View style={{ transform: [{ translateX: shakeAnim }] }}>
            <Pressable
              style={[
                s.sosBtn,
                countdown !== null && s.sosBtnCountdown,
                loading && s.sosBtnLoading,
              ]}
              onLongPress={startCountdown}
              onPress={countdown !== null ? stopCountdown : undefined}
              disabled={loading}
              delayLongPress={300}
              accessibilityRole="button"
              accessibilityLabel={loading ? '正在发送求助' : '长按触发 SOS 求助'}
              accessibilityHint="长按3秒触发紧急求助"
            >
              {loading ? (
                <View style={s.sosBtnInner}>
                  <FontAwesome6 name="spinner" size={48} color="#fff" />
                  <ThemedText variant="bodyMedium" color="#fff" style={s.sosBtnLabel}>发送中...</ThemedText>
                </View>
              ) : countdown !== null ? (
                <Animated.View style={[s.sosBtnInner, { transform: [{ scale: countdownScale }] }]}>
                  <Text style={s.countdownNumber}>{countdown}</Text>
                  <ThemedText variant="body" color="#fff" style={s.sosBtnLabel}>松手取消</ThemedText>
                </Animated.View>
              ) : (
                <View style={s.sosBtnInner}>
                  <FontAwesome6 name="phone-volume" size={48} color="#fff" />
                  <ThemedText variant="bodyMedium" color="#fff" style={s.sosBtnLabel}>SOS</ThemedText>
                  <ThemedText variant="caption" color="rgba(255,255,255,0.8)" style={s.sosBtnSubLabel}>
                    长按触发
                  </ThemedText>
                </View>
              )}
            </Pressable>
          </Animated.View>

          <ThemedText variant="small" color={theme.textMuted} style={s.sosBtnTip}>
            系统将自动拨打 120 并发送位置给联系人
          </ThemedText>
        </View>

        {/* 紧急联系人 */}
        <View style={s.contactsSection}>
          <View style={s.contactsHeader}>
            <FontAwesome6 name="address-book" size={16} color={theme.primary} />
            <ThemedText variant="title" color={theme.textPrimary} style={s.contactsTitle}>
              紧急联系人
            </ThemedText>
          </View>

          {contacts.length === 0 ? (
            <EmptyState
              icon="address-book"
              title="暂无可通知联系人"
              subtitle="请先添加紧急联系人"
              actionLabel="去添加"
              onActionPress={() => router.push('/contacts')}
            />
          ) : (
            contacts
              .sort((a, b) => (a.priority || 99) - (b.priority || 99))
              .map((contact) => (
                <TouchableOpacity
                  key={contact.id}
                  style={[s.contactCard, shadows.soft]}
                  onPress={() => handleCallContact(contact.contactId, contact.name)}
                  disabled={loading}
                  activeOpacity={0.88}
                  accessibilityRole="button"
                  accessibilityLabel={`${contact.name}，${contact.relationship}，点击拨打`}
                >
                  <View style={[s.contactAvatar, { backgroundColor: priorityColor(contact.priority || 3) + '20' }]}>
                    <ThemedText style={s.contactAvatarText}>
                      {contact.name.charAt(0)}
                    </ThemedText>
                  </View>
                  <View style={s.contactInfo}>
                    <View style={s.contactNameRow}>
                      <ThemedText variant="bodyMedium" color={theme.textPrimary}>{contact.name}</ThemedText>
                      {contact.priority === 1 && (
                        <View style={[s.priorityTag, { backgroundColor: theme.error + '20' }]}>
                          <ThemedText variant="caption" color={theme.error} style={s.priorityTagText}>首要</ThemedText>
                        </View>
                      )}
                    </View>
                    <ThemedText variant="small" color={theme.textSecondary}>{contact.relationship}</ThemedText>
                    <ThemedText variant="small" color={theme.primary}>{contact.phone}</ThemedText>
                  </View>
                  <View style={[s.callBtn, { backgroundColor: theme.accent }]}>
                    <FontAwesome6 name="phone" size={18} color="#fff" />
                  </View>
                </TouchableOpacity>
              ))
          )}
        </View>

        {/* 取消按钮 */}
        <TouchableOpacity
          style={[s.cancelBtn, { borderColor: theme.border }]}
          onPress={countdown !== null ? stopCountdown : () => router.back()}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="取消求助"
        >
          <FontAwesome6 name="xmark" size={18} color={theme.textPrimary} />
          <ThemedText variant="bodyMedium" color={theme.textPrimary}>
            {countdown !== null ? '取消倒计时' : '返回'}
          </ThemedText>
        </TouchableOpacity>
      </View>
      <Toast />
    </Screen>
  );
}

const createStyles = (theme: CreateStylesTheme) => StyleSheet.create({
  emergencyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
    paddingTop: Platform.OS === 'ios' ? 56 : spacing['2xl'],
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
  },
  sosBtnSection: {
    alignItems: 'center',
    marginBottom: spacing['2xl'],
  },
  sosBtnHint: {
    fontSize: 13,
    textAlign: 'center',
    marginBottom: spacing.lg,
    color: theme.textSecondary,
  },
  sosPulseRing: {
    position: 'absolute',
    width: SOS_BTN_SIZE + 32,
    height: SOS_BTN_SIZE + 32,
    borderRadius: (SOS_BTN_SIZE + 32) / 2,
    backgroundColor: theme.error + '18',
    top: 32,
  },
  sosBtn: {
    width: SOS_BTN_SIZE,
    height: SOS_BTN_SIZE,
    borderRadius: SOS_BTN_SIZE / 2,
    backgroundColor: theme.error,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: theme.error,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 12,
  },
  sosBtnCountdown: {
    backgroundColor: '#FF6F00',
  },
  sosBtnLoading: {
    opacity: 0.75,
    backgroundColor: theme.textMuted,
  },
  sosBtnInner: {
    alignItems: 'center',
    gap: spacing.xs,
  },
  countdownNumber: {
    fontSize: 72,
    fontWeight: '900',
    color: '#fff',
    lineHeight: 76,
  },
  sosBtnLabel: {
    fontSize: 20,
    fontWeight: '800',
    color: '#fff',
    letterSpacing: 2,
  },
  sosBtnSubLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.75)',
  },
  sosBtnTip: {
    fontSize: 12,
    textAlign: 'center',
    marginTop: spacing.lg,
    color: theme.textMuted,
    paddingHorizontal: spacing['2xl'],
  },
  contactsSection: {
    flex: 1,
  },
  contactsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  contactsTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: theme.textPrimary,
  },
  contactCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.backgroundDefault,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    marginBottom: spacing.md,
    gap: spacing.md,
  },
  contactAvatar: {
    width: 50,
    height: 50,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contactAvatarText: {
    fontSize: 20,
    fontWeight: '700',
    color: theme.textPrimary,
  },
  contactInfo: {
    flex: 1,
    gap: 2,
  },
  contactNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  priorityTag: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.full,
  },
  priorityTagText: {
    fontSize: 11,
    fontWeight: '600',
  },
  callBtn: {
    width: 46,
    height: 46,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: theme.accent,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  cancelBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 52,
    borderRadius: borderRadius.xl,
    borderWidth: 1.5,
    marginBottom: spacing['2xl'],
    gap: spacing.md,
    backgroundColor: theme.backgroundDefault,
  },
});
