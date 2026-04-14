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
} from 'react-native';
import { useSafeRouter, useSafeSearchParams } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  Shadows,
  HitSlop,
} from '@/constants/theme-warm';
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

const styles = StyleSheet.create({
  // 头部
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.lg,
  },

  headerTextBlock: {
    flex: 1,
    alignItems: 'center',
  },

  headerTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
  },

  headerSubtitle: {
    ...Typography.small,
    color: Colors.textSecondary,
    marginTop: Spacing.xs,
  },

  cancelButton: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.lg,
  },

  cancelButtonText: {
    ...Typography.bodyMedium,
    color: Colors.textSecondary,
  },

  // 表单容器
  formContainer: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing['5xl'],
  },
  formLead: {
    ...Typography.small,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
  },

  // 表单项
  formGroup: {
    marginBottom: Spacing.xl,
  },

  formLabel: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
  },

  formLabelRequired: {
    color: Colors.error,
  },

  // 输入框
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.backgroundTertiary,
    borderRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.lg,
    height: 56,
    borderWidth: 1,
    borderColor: Colors.border,
  },

  inputContainerError: {
    borderColor: Colors.error,
  },

  inputContainerFocused: {
    borderColor: Colors.primary,
    borderWidth: 2,
  },

  inputIcon: {
    fontSize: 20,
    color: Colors.textMuted,
    marginRight: Spacing.md,
  },

  input: {
    flex: 1,
    ...Typography.body,
    color: Colors.textPrimary,
  },

  inputPlaceholder: {
    color: Colors.textMuted,
  },

  errorText: {
    ...Typography.small,
    color: Colors.error,
    marginTop: Spacing.xs,
  },

  // 下拉选择
  dropdownContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.backgroundTertiary,
    borderRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.lg,
    height: 56,
    borderWidth: 1,
    borderColor: Colors.border,
    justifyContent: 'space-between',
  },

  dropdownText: {
    ...Typography.body,
    color: Colors.textPrimary,
    flex: 1,
  },

  dropdownPlaceholder: {
    color: Colors.textMuted,
  },

  dropdownIcon: {
    fontSize: 16,
    color: Colors.textMuted,
  },

  // 优先级按钮组
  priorityContainer: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginTop: Spacing.sm,
  },

  priorityButton: {
    flex: 1,
    height: 48,
    borderRadius: BorderRadius.lg,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: Colors.border,
    backgroundColor: Colors.backgroundDefault,
  },

  priorityButtonSelected: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },

  priorityButtonText: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
  },

  priorityButtonTextSelected: {
    color: Colors.backgroundDefault,
    fontWeight: 'bold',
  },

  // 通知渠道选项
  notificationContainer: {
    marginTop: Spacing.sm,
  },

  notificationOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },

  notificationOptionSelected: {
    backgroundColor: Colors.primaryLight,
    borderColor: Colors.primary,
  },

  checkbox: {
    width: 24,
    height: 24,
    borderRadius: BorderRadius.lg,
    borderWidth: 2,
    borderColor: Colors.border,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },

  checkboxSelected: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },

  checkboxIcon: {
    fontSize: 14,
    color: Colors.backgroundDefault,
  },

  notificationText: {
    ...Typography.body,
    color: Colors.textPrimary,
    flex: 1,
  },

  // 保存按钮
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.xl,
    marginTop: Spacing.xl,
    ...Shadows.medium,
  },

  saveButtonDisabled: {
    backgroundColor: Colors.disabled,
  },

  saveButtonText: {
    ...Typography.bodyMedium,
    color: Colors.backgroundDefault,
    fontWeight: 'bold',
  },
});

export default function ContactEditPage() {
  const router = useSafeRouter();
  const params = useSafeSearchParams<{ contactId?: string }>();

  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [relationship, setRelationship] = useState(0);
  const [priority, setPriority] = useState(1);
  const [notificationChannels, setNotificationChannels] = useState<string[]>(['app']);
  const [nameError, setNameError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

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
    // TODO: 显示关系选择器
  };

  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* 头部 */}
        <View style={styles.header} accessible accessibilityLabel="编辑联系人页面">
          <TouchableOpacity
            style={styles.cancelButton}
            onPress={handleCancel}
            activeOpacity={0.75}
            hitSlop={HitSlop.medium}
            accessible
            accessibilityLabel="取消"
            accessibilityHint="点击取消编辑并返回"
            accessibilityRole="button"
          >
            <ThemedText variant="bodyMedium" color={Colors.textSecondary} style={styles.cancelButtonText}>
              取消
            </ThemedText>
          </TouchableOpacity>
          <View style={styles.headerTextBlock}>
            <ThemedText variant="h1" color={Colors.textPrimary} style={styles.headerTitle}>
              {isEditing ? '编辑联系人' : '添加联系人'}
            </ThemedText>
            <ThemedText variant="small" color={Colors.textSecondary} style={styles.headerSubtitle}>
              紧急时可第一时间通知对方
            </ThemedText>
          </View>
          <View style={{ width: 60 }} />
        </View>

        {/* 表单 */}
        <ScrollView style={styles.formContainer}>
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.formLead}>
            标注 * 的字段为必填项
          </ThemedText>
          {/* 姓名 */}
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>
              姓名 <Text style={styles.formLabelRequired}>*</Text>
            </Text>
            <View
              style={[
                styles.inputContainer,
                nameError ? styles.inputContainerError : null,
              ]}
              accessible
              accessibilityLabel="姓名输入框"
              accessibilityHint="输入联系人姓名"
              accessibilityRole="none"
            >
              <FontAwesome6
                name="user"
                size={20}
                color={Colors.textMuted}
                style={styles.inputIcon}
              />
              <TextInput
                style={styles.input}
                placeholder="请输入姓名"
                placeholderTextColor={Colors.textMuted}
                value={name}
                onChangeText={setName}
                onFocus={() => setNameError('')}
                accessibilityLabel="姓名"
              />
            </View>
            {nameError ? <Text style={styles.errorText}>{nameError}</Text> : null}
          </View>

          {/* 手机号 */}
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>
              手机号 <Text style={styles.formLabelRequired}>*</Text>
            </Text>
            <View
              style={[
                styles.inputContainer,
                phoneError ? styles.inputContainerError : null,
              ]}
              accessible
              accessibilityLabel="手机号输入框"
              accessibilityHint="输入联系人手机号"
              accessibilityRole="none"
            >
              <FontAwesome6
                name="phone"
                size={20}
                color={Colors.textMuted}
                style={styles.inputIcon}
              />
              <TextInput
                style={styles.input}
                placeholder="请输入手机号"
                placeholderTextColor={Colors.textMuted}
                value={phone}
                onChangeText={setPhone}
                keyboardType="phone-pad"
                onFocus={() => setPhoneError('')}
                accessibilityLabel="手机号"
              />
            </View>
            {phoneError ? <Text style={styles.errorText}>{phoneError}</Text> : null}
          </View>

          {/* 关系 */}
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>关系</Text>
            <TouchableOpacity
              style={styles.dropdownContainer}
              onPress={() => handleSelectRelationship(relationship)}
              activeOpacity={0.85}
              hitSlop={HitSlop.small}
              accessible
              accessibilityLabel={`关系：${RELATIONSHIPS[relationship]}`}
              accessibilityHint="点击选择联系人关系"
              accessibilityRole="button"
            >
              <Text
                style={[
                  styles.dropdownText,
                  RELATIONSHIPS[relationship] ? null : styles.dropdownPlaceholder,
                ]}
              >
                {RELATIONSHIPS[relationship] || '请选择关系'}
              </Text>
              <FontAwesome6
                name="chevron-down"
                size={16}
                color={Colors.textMuted}
                style={styles.dropdownIcon}
              />
            </TouchableOpacity>
          </View>

          {/* 优先级 */}
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>优先级</Text>
            <View style={styles.priorityContainer} accessible accessibilityLabel="优先级选择">
              {[1, 2, 3, 4, 5].map((p) => (
                <TouchableOpacity
                  key={p}
                  style={[
                    styles.priorityButton,
                    priority === p ? styles.priorityButtonSelected : null,
                  ]}
                  onPress={() => setPriority(p)}
                  activeOpacity={0.85}
                  hitSlop={HitSlop.small}
                  accessible
                  accessibilityLabel={`优先级 ${p}`}
                  accessibilityHint={priority === p ? '已选择' : '点击选择'}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: priority === p }}
                >
                  <Text
                    style={[
                      styles.priorityButtonText,
                      priority === p ? styles.priorityButtonTextSelected : null,
                    ]}
                  >
                    {p}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* 通知渠道 */}
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>通知渠道</Text>
            <View style={styles.notificationContainer}>
              {['app', 'sms', 'phone'].map((channel) => (
                <TouchableOpacity
                  key={channel}
                  style={[
                    styles.notificationOption,
                    notificationChannels.includes(channel) ? styles.notificationOptionSelected : null,
                  ]}
                  onPress={() => toggleNotificationChannel(channel)}
                  activeOpacity={0.85}
                  hitSlop={HitSlop.small}
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
                      styles.checkbox,
                      notificationChannels.includes(channel) ? styles.checkboxSelected : null,
                    ]}
                  >
                    {notificationChannels.includes(channel) ? (
                      <FontAwesome6
                        name="check"
                        size={14}
                        color={Colors.backgroundDefault}
                        style={styles.checkboxIcon}
                      />
                    ) : null}
                  </View>
                  <Text style={styles.notificationText}>
                    {channel === 'app' ? 'App推送' : channel === 'sms' ? '短信' : '电话'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* 保存按钮 */}
          <TouchableOpacity
            style={[
              styles.saveButton,
              isSaving ? styles.saveButtonDisabled : null,
            ]}
            onPress={handleSave}
            disabled={isSaving}
            activeOpacity={0.88}
            hitSlop={HitSlop.medium}
            accessible
            accessibilityLabel="保存联系人"
            accessibilityHint="点击保存联系人信息"
            accessibilityRole="button"
            accessibilityState={{ disabled: isSaving }}
          >
            {isSaving ? (
              <ActivityIndicator color={Colors.backgroundDefault} />
            ) : (
              <ThemedText variant="bodyMedium" color={Colors.backgroundDefault} style={styles.saveButtonText}>
                保存
              </ThemedText>
            )}
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </Screen>
  );
}
