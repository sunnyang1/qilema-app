/**
 * 联系人编辑页面
 * 温暖守护风格 + UI/UX Pro Max 优化
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  AccessibilityInfo,
  Alert,
  ActivityIndicator,
  Modal,
} from 'react-native';
import { useSafeRouter, useSafeSearchParams } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import {
  spacing,
  borderRadius,
  typography,
  hitSlop,
} from '@/design-system';
import { createShadows } from '@/design-system';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import { contactsService, EmergencyContact } from '@/services/contacts';
import Toast from 'react-native-toast-message';

// 联系人数据类型
interface Contact {
  contactId: string;
  name: string;
  phone: string;
  relationship: string;
  priority: number;
  notificationChannels: string[];
}

// 关系列表
const RELATIONSHIPS = [
  '家人',
  '配偶',
  '父母',
  '子女',
  '朋友',
  '同事',
  '其他',
];

const createStyles = (theme: CreateStylesTheme, shadows: ReturnType<typeof createShadows>) => StyleSheet.create({
  // 头部
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
    paddingBottom: spacing.lg,
  },

  headerTextBlock: {
    flex: 1,
    alignItems: 'center',
  },

  headerTitle: {
    ...typography.h1,
    color: theme.textPrimary,
  },

  headerSubtitle: {
    ...typography.small,
    color: theme.textSecondary,
    marginTop: spacing.xs,
  },

  cancelButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
  },

  cancelButtonText: {
    ...typography.bodyMedium,
    color: theme.textSecondary,
  },

  // 表单容器
  formContainer: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing['5xl'],
  },
  formLead: {
    ...typography.small,
    color: theme.textSecondary,
    marginBottom: spacing.lg,
  },

  // 表单项
  formGroup: {
    marginBottom: spacing.xl,
  },

  formLabel: {
    ...typography.bodyMedium,
    color: theme.textPrimary,
    marginBottom: spacing.sm,
  },

  formLabelRequired: {
    color: theme.error,
  },

  // 输入框
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.backgroundTertiary,
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing.lg,
    height: 56,
    borderWidth: 1,
    borderColor: theme.border,
  },

  inputContainerError: {
    borderColor: theme.error,
  },

  inputContainerFocused: {
    borderColor: theme.primary,
    borderWidth: 2,
  },

  inputIcon: {
    fontSize: 20,
    color: theme.textMuted,
    marginRight: spacing.md,
  },

  input: {
    flex: 1,
    ...typography.body,
    color: theme.textPrimary,
  },

  inputPlaceholder: {
    color: theme.textMuted,
  },

  errorText: {
    ...typography.small,
    color: theme.error,
    marginTop: spacing.xs,
  },

  // 下拉选择
  dropdownContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.backgroundTertiary,
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing.lg,
    height: 56,
    borderWidth: 1,
    borderColor: theme.border,
    justifyContent: 'space-between',
  },

  dropdownText: {
    ...typography.body,
    color: theme.textPrimary,
    flex: 1,
  },

  dropdownPlaceholder: {
    color: theme.textMuted,
  },

  dropdownIcon: {
    fontSize: 16,
    color: theme.textMuted,
  },

  // 优先级按钮组
  priorityContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },

  priorityButton: {
    flex: 1,
    height: 48,
    borderRadius: borderRadius.lg,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: theme.border,
    backgroundColor: theme.backgroundDefault,
  },

  priorityButtonSelected: {
    backgroundColor: theme.primary,
    borderColor: theme.primary,
  },

  priorityButtonText: {
    ...typography.bodyMedium,
    color: theme.textPrimary,
  },

  priorityButtonTextSelected: {
    color: theme.backgroundDefault,
    fontWeight: 'bold',
  },

  // 通知渠道选项
  notificationContainer: {
    marginTop: spacing.sm,
  },

  notificationOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    backgroundColor: theme.backgroundDefault,
    borderRadius: borderRadius.xl,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: theme.border,
  },

  notificationOptionSelected: {
    backgroundColor: theme.primaryLight,
    borderColor: theme.primary,
  },

  checkbox: {
    width: 24,
    height: 24,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderColor: theme.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },

  checkboxSelected: {
    backgroundColor: theme.primary,
    borderColor: theme.primary,
  },

  checkboxIcon: {
    fontSize: 14,
    color: theme.backgroundDefault,
  },

  notificationText: {
    ...typography.body,
    color: theme.textPrimary,
    flex: 1,
  },

  // 保存按钮
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    backgroundColor: theme.primary,
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing.xl,
    marginTop: spacing.xl,
    ...shadows.medium,
  },

  saveButtonDisabled: {
    backgroundColor: theme.disabled,
  },

  saveButtonText: {
    ...typography.bodyMedium,
    color: theme.backgroundDefault,
    fontWeight: 'bold',
  },
});

const createPickerStyles = (theme: CreateStylesTheme, shadows: ReturnType<typeof createShadows>) => StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  container: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.backgroundDefault,
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
    ...shadows.strong,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.borderLight,
  },
  list: {
    maxHeight: 320,
  },
  option: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.borderLight,
  },
  optionSelected: {
    backgroundColor: theme.primaryLight,
  },
  optionText: {
    ...typography.body,
    color: theme.textPrimary,
  },
  optionTextSelected: {
    ...typography.bodyMedium,
    color: theme.primary,
  },
});

export default function ContactEditPage() {
  const router = useSafeRouter();
  const params = useSafeSearchParams<{ contactId?: string }>();
  const { theme, isDark } = useTheme();
  const shadows = createShadows(theme.shadow, theme.shadowStrong);
  const s = createStyles(theme, shadows);
  const ps = createPickerStyles(theme, shadows);

  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [relationship, setRelationship] = useState(0);
  const [priority, setPriority] = useState(1);
  const [notificationChannels, setNotificationChannels] = useState<string[]>(['app']);
  const [nameError, setNameError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [showRelationshipPicker, setShowRelationshipPicker] = useState(false);

  // 检测屏幕阅读器状态
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);

  useEffect(() => {
    // 检测屏幕阅读器
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      (enabled) => setIsScreenReaderEnabled(enabled)
    );

    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);

    // 检查是否是编辑模式
    if (params.contactId) {
      setIsEditing(true);
      loadContactData(params.contactId);
    }

    return () => {
      subscription?.remove();
    };
  }, [params.contactId]);

  // 加载联系人数据
  const loadContactData = useCallback(async (contactId: string) => {
    try {
      const contact = await contactsService.getContact(contactId);
      setName(contact.name);
      setPhone(contact.phone);
      const relIdx = RELATIONSHIPS.indexOf(contact.relationship);
      setRelationship(relIdx >= 0 ? relIdx : 0);
      setPriority(contact.priority);
      setNotificationChannels(contact.notificationChannels);
    } catch (error: any) {
      console.error('加载联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '加载失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 2600,
      });
      router.back();
    }
  }, [router]);

  // 验证表单
  const validateForm = () => {
    let isValid = true;

    // 验证姓名
    if (!name.trim()) {
      setNameError('请输入姓名');
      isValid = false;
    } else if (name.trim().length < 2) {
      setNameError('姓名至少2个字符');
      isValid = false;
    } else {
      setNameError('');
    }

    // 验证手机号
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phone.trim()) {
      setPhoneError('请输入手机号');
      isValid = false;
    } else if (!phoneRegex.test(phone.trim())) {
      setPhoneError('请输入有效的手机号');
      isValid = false;
    } else {
      setPhoneError('');
    }

    return isValid;
  };

  // 切换通知渠道
  const toggleNotificationChannel = (channel: string) => {
    if (notificationChannels.includes(channel)) {
      setNotificationChannels(notificationChannels.filter(c => c !== channel));
    } else {
      setNotificationChannels([...notificationChannels, channel]);
    }
  };

  // 保存联系人
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSaving(true);
    try {
      const contactData = {
        name: name.trim(),
        phone: phone.trim(),
        relationship: RELATIONSHIPS[relationship],
        priority,
        notificationChannels,
      };

      if (isEditing && params.contactId) {
        // 更新联系人
        await contactsService.updateContact(params.contactId, contactData);
        Toast.show({
          type: 'success',
          text1: '更新成功',
          text2: '联系人信息已保存',
          visibilityTime: 2200,
        });
      } else {
        // 添加联系人
        await contactsService.createContact(contactData);
        Toast.show({
          type: 'success',
          text1: '添加成功',
          text2: '已新增紧急联系人',
          visibilityTime: 2200,
        });
      }

      setTimeout(() => router.back(), 1500);
    } catch (error: any) {
      console.error('保存联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '保存失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 2600,
      });
    } finally {
      setIsSaving(false);
    }
  };

  // 取消编辑
  const handleCancel = () => {
    router.back();
  };

  // 选择关系
  const handleSelectRelationship = (index: number) => {
    setRelationship(index);
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* 头部 */}
        <View style={s.header} accessible accessibilityLabel="编辑联系人页面">
          <TouchableOpacity
            style={s.cancelButton}
            onPress={handleCancel}
            activeOpacity={0.75}
            hitSlop={hitSlop.medium}
            accessible
            accessibilityLabel="取消"
            accessibilityHint="点击取消编辑并返回"
            accessibilityRole="button"
          >
            <ThemedText variant="bodyMedium" color={theme.textSecondary} style={s.cancelButtonText}>
              取消
            </ThemedText>
          </TouchableOpacity>
          <View style={s.headerTextBlock}>
            <ThemedText variant="h1" color={theme.textPrimary} style={s.headerTitle}>
              {isEditing ? '编辑联系人' : '添加联系人'}
            </ThemedText>
            <ThemedText variant="small" color={theme.textSecondary} style={s.headerSubtitle}>
              紧急时可第一时间通知对方
            </ThemedText>
          </View>
          <View style={{ width: 60 }} />
        </View>

        {/* 表单 */}
        <ScrollView style={s.formContainer}>
          <ThemedText variant="small" color={theme.textSecondary} style={s.formLead}>
            标注 * 的字段为必填项
          </ThemedText>
          {/* 姓名 */}
          <View style={s.formGroup}>
            <Text style={s.formLabel}>
              姓名 <Text style={s.formLabelRequired}>*</Text>
            </Text>
            <View
              style={[
                s.inputContainer,
                nameError ? s.inputContainerError : null,
              ]}
              accessible
              accessibilityLabel="姓名输入框"
              accessibilityHint="输入联系人姓名"
              accessibilityRole="none"
            >
              <FontAwesome6
                name="user"
                size={20}
                color={theme.textMuted}
                style={s.inputIcon}
              />
              <TextInput
                style={s.input}
                placeholder="请输入姓名"
                placeholderTextColor={theme.textMuted}
                value={name}
                onChangeText={setName}
                onFocus={() => setNameError('')}
                accessibilityLabel="姓名"
              />
            </View>
            {nameError ? <Text style={s.errorText}>{nameError}</Text> : null}
          </View>

          {/* 手机号 */}
          <View style={s.formGroup}>
            <Text style={s.formLabel}>
              手机号 <Text style={s.formLabelRequired}>*</Text>
            </Text>
            <View
              style={[
                s.inputContainer,
                phoneError ? s.inputContainerError : null,
              ]}
              accessible
              accessibilityLabel="手机号输入框"
              accessibilityHint="输入联系人手机号"
              accessibilityRole="none"
            >
              <FontAwesome6
                name="phone"
                size={20}
                color={theme.textMuted}
                style={s.inputIcon}
              />
              <TextInput
                style={s.input}
                placeholder="请输入手机号"
                placeholderTextColor={theme.textMuted}
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
                onFocus={() => setPhoneError('')}
                accessibilityLabel="手机号"
              />
            </View>
            {phoneError ? <Text style={s.errorText}>{phoneError}</Text> : null}
          </View>

          {/* 关系 */}
          <View style={s.formGroup}>
            <Text style={s.formLabel}>关系</Text>
            <TouchableOpacity
              style={s.dropdownContainer}
              onPress={() => setShowRelationshipPicker(true)}
              activeOpacity={0.85}
              hitSlop={hitSlop.small}
              accessible
              accessibilityLabel={`关系：${RELATIONSHIPS[relationship]}`}
              accessibilityHint="点击选择联系人关系"
              accessibilityRole="button"
            >
              <Text
                style={[
                  s.dropdownText,
                  RELATIONSHIPS[relationship] ? null : s.dropdownPlaceholder,
                ]}
              >
                {RELATIONSHIPS[relationship] || '请选择关系'}
              </Text>
              <FontAwesome6
                name="chevron-down"
                size={16}
                color={theme.textMuted}
                style={s.dropdownIcon}
              />
            </TouchableOpacity>
          </View>

          {/* 优先级 */}
          <View style={s.formGroup}>
            <Text style={s.formLabel}>优先级</Text>
            <View style={s.priorityContainer} accessible accessibilityLabel="优先级选择">
              {[1, 2, 3, 4, 5].map((p) => (
                <TouchableOpacity
                  key={p}
                  style={[
                    s.priorityButton,
                    priority === p ? s.priorityButtonSelected : null,
                  ]}
                  onPress={() => setPriority(p)}
                  activeOpacity={0.85}
                  hitSlop={hitSlop.small}
                  accessible
                  accessibilityLabel={`优先级 ${p}`}
                  accessibilityHint={priority === p ? '已选择' : '点击选择'}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: priority === p }}
                >
                  <Text
                    style={[
                      s.priorityButtonText,
                      priority === p ? s.priorityButtonTextSelected : null,
                    ]}
                  >
                    {p}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* 通知渠道 */}
          <View style={s.formGroup}>
            <Text style={s.formLabel}>通知渠道</Text>
            <View style={s.notificationContainer}>
              {['app', 'sms', 'phone'].map((channel) => (
                <TouchableOpacity
                  key={channel}
                  style={[
                    s.notificationOption,
                    notificationChannels.includes(channel) ? s.notificationOptionSelected : null,
                  ]}
                  onPress={() => toggleNotificationChannel(channel)}
                  activeOpacity={0.85}
                  hitSlop={hitSlop.small}
                  accessible
                  accessibilityLabel={
                    channel === 'app' ? 'App推送' : channel === 'sms' ? '短信' : '电话'
                  }
                  accessibilityHint={notificationChannels.includes(channel) ? '已选择' : '点击选择'}
                  accessibilityRole="checkbox"
                  accessibilityState={{
                    checked: notificationChannels.includes(channel),
                  }}
                >
                  <View
                    style={[
                      s.checkbox,
                      notificationChannels.includes(channel) ? s.checkboxSelected : null,
                    ]}
                  >
                    {notificationChannels.includes(channel) ? (
                      <FontAwesome6
                        name="check"
                        size={14}
                        color={theme.backgroundDefault}
                        style={s.checkboxIcon}
                      />
                    ) : null}
                  </View>
                  <Text style={s.notificationText}>
                    {channel === 'app' ? 'App推送' : channel === 'sms' ? '短信' : '电话'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* 保存按钮 */}
          <TouchableOpacity
            style={[
              s.saveButton,
              isSaving ? s.saveButtonDisabled : null,
            ]}
            onPress={handleSave}
            disabled={isSaving}
            activeOpacity={0.88}
            hitSlop={hitSlop.medium}
            accessible
            accessibilityLabel="保存联系人"
            accessibilityHint="点击保存联系人信息"
            accessibilityRole="button"
            accessibilityState={{ disabled: isSaving }}
          >
            {isSaving ? (
              <ActivityIndicator color={theme.backgroundDefault} />
            ) : (
              <ThemedText variant="bodyMedium" color={theme.backgroundDefault} style={s.saveButtonText}>
                保存
              </ThemedText>
            )}
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* 关系选择器 Modal */}
      <Modal
        visible={showRelationshipPicker}
        transparent
        animationType="fade"
        onRequestClose={() => setShowRelationshipPicker(false)}
      >
        <TouchableOpacity
          style={ps.overlay}
          activeOpacity={1}
          onPress={() => setShowRelationshipPicker(false)}
        >
          <View style={ps.container}>
            <View style={ps.header}>
              <ThemedText variant="title" color={theme.textPrimary}>选择关系</ThemedText>
              <TouchableOpacity
                onPress={() => setShowRelationshipPicker(false)}
                hitSlop={hitSlop.medium}
                accessibilityRole="button"
                accessibilityLabel="关闭"
              >
                <FontAwesome6 name="xmark" size={20} color={theme.textMuted} />
              </TouchableOpacity>
            </View>
            <ScrollView style={ps.list} showsVerticalScrollIndicator={false}>
              {RELATIONSHIPS.map((rel, idx) => (
                <TouchableOpacity
                  key={rel}
                  style={[
                    ps.option,
                    idx === relationship && ps.optionSelected,
                  ]}
                  onPress={() => {
                    handleSelectRelationship(idx);
                    setShowRelationshipPicker(false);
                  }}
                  activeOpacity={0.75}
                  accessibilityRole="radio"
                  accessibilityLabel={rel}
                  accessibilityState={{ selected: idx === relationship }}
                >
                  <Text style={[
                    ps.optionText,
                    idx === relationship && ps.optionTextSelected,
                  ]}>
                    {rel}
                  </Text>
                  {idx === relationship && (
                    <FontAwesome6 name="check" size={16} color={theme.primary} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </TouchableOpacity>
      </Modal>
    </Screen>
  );
}
