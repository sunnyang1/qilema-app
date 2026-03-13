/**
 * 联系人编辑表单逻辑 Hook
 */
import { useState, useEffect, useCallback } from 'react';
import { AccessibilityInfo } from 'react-native';
import { contactsService } from '@/services/contacts';
import Toast from 'react-native-toast-message';

// 关系列表
export const RELATIONSHIPS = [
  '家人',
  '配偶',
  '父母',
  '子女',
  '朋友',
  '同事',
  '其他',
] as const;

export type Relationship = typeof RELATIONSHIPS[number];

export interface ContactFormData {
  name: string;
  phone: string;
  relationship: number;
  priority: number;
  notificationChannels: string[];
}

export interface ContactFormErrors {
  name: string;
  phone: string;
}

export interface UseContactFormOptions {
  contactId?: string;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useContactForm({ contactId, onSuccess, onError }: UseContactFormOptions) {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // 表单数据
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    phone: '',
    relationship: 0,
    priority: 1,
    notificationChannels: ['app'],
  });

  // 错误状态
  const [errors, setErrors] = useState<ContactFormErrors>({
    name: '',
    phone: '',
  });

  // 屏幕阅读器状态
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);

  // 初始化
  useEffect(() => {
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      (enabled) => setIsScreenReaderEnabled(enabled)
    );

    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);

    if (contactId) {
      setIsEditing(true);
      loadContactData(contactId);
    }

    return () => {
      subscription?.remove();
    };
  }, [contactId]);

  // 加载联系人数据
  const loadContactData = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      const contact = await contactsService.getContact(id);
      setFormData({
        name: contact.name,
        phone: contact.phone,
        relationship: RELATIONSHIPS.indexOf(contact.relationship as Relationship) || 0,
        priority: contact.priority,
        notificationChannels: contact.notificationChannels,
      });
    } catch (error: any) {
      console.error('加载联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '加载失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 3000,
      });
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  // 更新表单字段
  const updateField = useCallback(<K extends keyof ContactFormData>(
    field: K,
    value: ContactFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (field === 'name' || field === 'phone') {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  }, []);

  // 切换通知渠道
  const toggleNotificationChannel = useCallback((channel: string) => {
    setFormData(prev => {
      const channels = prev.notificationChannels.includes(channel)
        ? prev.notificationChannels.filter(c => c !== channel)
        : [...prev.notificationChannels, channel];
      return { ...prev, notificationChannels: channels };
    });
  }, []);

  // 验证表单
  const validateForm = useCallback((): boolean => {
    const newErrors: ContactFormErrors = { name: '', phone: '' };
    let isValid = true;

    // 验证姓名
    if (!formData.name.trim()) {
      newErrors.name = '请输入姓名';
      isValid = false;
    } else if (formData.name.trim().length < 2) {
      newErrors.name = '姓名至少2个字符';
      isValid = false;
    }

    // 验证手机号
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!formData.phone.trim()) {
      newErrors.phone = '请输入手机号';
      isValid = false;
    } else if (!phoneRegex.test(formData.phone.trim())) {
      newErrors.phone = '请输入有效的手机号';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  }, [formData.name, formData.phone]);

  // 保存联系人
  const saveContact = useCallback(async (): Promise<boolean> => {
    if (!validateForm()) {
      return false;
    }

    setIsSaving(true);
    try {
      const contactData = {
        name: formData.name.trim(),
        phone: formData.phone.trim(),
        relationship: RELATIONSHIPS[formData.relationship],
        priority: formData.priority,
        notificationChannels: formData.notificationChannels,
      };

      if (isEditing && contactId) {
        await contactsService.updateContact(contactId, contactData);
        Toast.show({
          type: 'success',
          text1: '更新成功',
          text2: '联系人信息已更新',
          visibilityTime: 2000,
        });
      } else {
        await contactsService.createContact(contactData);
        Toast.show({
          type: 'success',
          text1: '添加成功',
          text2: '联系人已添加',
          visibilityTime: 2000,
        });
      }

      onSuccess?.();
      return true;
    } catch (error: any) {
      console.error('保存联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '保存失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 3000,
      });
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [formData, isEditing, contactId, validateForm, onSuccess]);

  return {
    isEditing,
    isLoading,
    isSaving,
    isScreenReaderEnabled,
    formData,
    errors,
    updateField,
    toggleNotificationChannel,
    saveContact,
  };
}
