/**
 * 联系人表单组件
 */
import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
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
import { RELATIONSHIPS, ContactFormData, ContactFormErrors } from '../useContactForm';

interface ContactFormProps {
  formData: ContactFormData;
  errors: ContactFormErrors;
  isSaving: boolean;
  onUpdateField: <K extends keyof ContactFormData>(field: K, value: ContactFormData[K]) => void;
  onToggleChannel: (channel: string) => void;
  onSave: () => void;
}

const styles = StyleSheet.create({
  formContainer: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing['5xl'],
  },

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

  errorText: {
    ...Typography.small,
    color: Colors.error,
    marginTop: Spacing.xs,
  },

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

  dropdownIcon: {
    fontSize: 16,
    color: Colors.textMuted,
  },

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

const CHANNEL_LABELS: Record<string, string> = {
  app: 'App推送',
  sms: '短信',
  phone: '电话',
};

export function ContactForm({
  formData,
  errors,
  isSaving,
  onUpdateField,
  onToggleChannel,
  onSave,
}: ContactFormProps) {
  const { name, phone, relationship, priority, notificationChannels } = formData;

  return (
    <View style={styles.formContainer}>
      {/* 姓名 */}
      <View style={styles.formGroup}>
        <Text style={styles.formLabel}>
          姓名 <Text style={styles.formLabelRequired}>*</Text>
        </Text>
        <View
          style={[styles.inputContainer, errors.name ? { borderColor: Colors.error } : null]}
          accessible
          accessibilityLabel="姓名输入框"
          accessibilityHint="输入联系人姓名"
        >
          <FontAwesome6 name="user" size={20} color={Colors.textMuted} style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="请输入姓名"
            placeholderTextColor={Colors.textMuted}
            value={name}
            onChangeText={(value) => onUpdateField('name', value)}
            accessibilityLabel="姓名"
          />
        </View>
        {errors.name ? <Text style={styles.errorText}>{errors.name}</Text> : null}
      </View>

      {/* 手机号 */}
      <View style={styles.formGroup}>
        <Text style={styles.formLabel}>
          手机号 <Text style={styles.formLabelRequired}>*</Text>
        </Text>
        <View
          style={[styles.inputContainer, errors.phone ? { borderColor: Colors.error } : null]}
          accessible
          accessibilityLabel="手机号输入框"
          accessibilityHint="输入联系人手机号"
        >
          <FontAwesome6 name="phone" size={20} color={Colors.textMuted} style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="请输入手机号"
            placeholderTextColor={Colors.textMuted}
            value={phone}
            onChangeText={(value) => onUpdateField('phone', value)}
            keyboardType="phone-pad"
            accessibilityLabel="手机号"
          />
        </View>
        {errors.phone ? <Text style={styles.errorText}>{errors.phone}</Text> : null}
      </View>

      {/* 关系 */}
      <View style={styles.formGroup}>
        <Text style={styles.formLabel}>关系</Text>
        <TouchableOpacity
          style={styles.dropdownContainer}
          hitSlop={HitSlop.small}
          accessible
          accessibilityLabel={`关系：${RELATIONSHIPS[relationship]}`}
          accessibilityHint="点击选择联系人关系"
          accessibilityRole="button"
        >
          <Text style={styles.dropdownText}>{RELATIONSHIPS[relationship]}</Text>
          <FontAwesome6 name="chevron-down" size={16} color={Colors.textMuted} style={styles.dropdownIcon} />
        </TouchableOpacity>
      </View>

      {/* 优先级 */}
      <View style={styles.formGroup}>
        <Text style={styles.formLabel}>优先级</Text>
        <View style={styles.priorityContainer} accessible accessibilityLabel="优先级选择">
          {[1, 2, 3, 4, 5].map((p) => (
            <TouchableOpacity
              key={p}
              style={[styles.priorityButton, priority === p ? styles.priorityButtonSelected : null]}
              onPress={() => onUpdateField('priority', p)}
              hitSlop={HitSlop.small}
              accessible
              accessibilityLabel={`优先级 ${p}`}
              accessibilityHint={priority === p ? '已选择' : '点击选择'}
              accessibilityRole="radio"
              accessibilityState={{ selected: priority === p }}
            >
              <Text style={[styles.priorityButtonText, priority === p ? styles.priorityButtonTextSelected : null]}>
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
              onPress={() => onToggleChannel(channel)}
              hitSlop={HitSlop.small}
              accessible
              accessibilityLabel={CHANNEL_LABELS[channel]}
              accessibilityHint={notificationChannels.includes(channel) ? '已选择' : '点击选择'}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: notificationChannels.includes(channel) }}
            >
              <View style={[styles.checkbox, notificationChannels.includes(channel) ? styles.checkboxSelected : null]}>
                {notificationChannels.includes(channel) ? (
                  <FontAwesome6 name="check" size={14} color={Colors.backgroundDefault} style={styles.checkboxIcon} />
                ) : null}
              </View>
              <Text style={styles.notificationText}>{CHANNEL_LABELS[channel]}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 保存按钮 */}
      <TouchableOpacity
        style={[styles.saveButton, isSaving ? styles.saveButtonDisabled : null]}
        onPress={onSave}
        disabled={isSaving}
        hitSlop={HitSlop.medium}
        accessible
        accessibilityLabel="保存联系人"
        accessibilityHint="点击保存联系人信息"
        accessibilityRole="button"
        accessibilityState={{ disabled: isSaving }}
      >
        <ThemedText variant="bodyMedium" color={Colors.backgroundDefault} style={styles.saveButtonText}>
          {isSaving ? '保存中...' : '保存'}
        </ThemedText>
      </TouchableOpacity>
    </View>
  );
}
