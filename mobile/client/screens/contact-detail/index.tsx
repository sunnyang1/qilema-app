import React, { useCallback, useMemo, useState } from 'react';
import { View, StyleSheet, TouchableOpacity, ScrollView, Alert, Linking } from 'react-native';
import { useSafeRouter, useSafeSearchParams } from '@/hooks/useSafeRouter';
import { useFocusEffect } from 'expo-router';
import { contactsService, EmergencyContact } from '@/services/contacts';
import { Screen } from '@/components/Screen';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import Toast from 'react-native-toast-message';

interface ContactDetailParams {
  /** 数据库主键 id（与列表项 `contact.id` 一致，字符串形式） */
  contactId: string;
}

export default function ContactDetailScreen() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { contactId } = useSafeSearchParams<ContactDetailParams>();
  const [contactData, setContactData] = useState<EmergencyContact | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const styles = useMemo(() => createStyles(theme), [theme]);

  // 获取联系人详情
  const fetchContactDetail = useCallback(async () => {
    if (!contactId) {
      Toast.show({
        type: 'error',
        text1: '参数错误',
        text2: '缺少联系人 ID',
        visibilityTime: 3000,
      });
      return;
    }

    try {
      setLoading(true);
      /** GET /api/v1/contacts/{id}（数据库主键），见 contactsService */
      const data = await contactsService.getContact(contactId);
      setContactData(data);
    } catch (error: any) {
      console.error('获取联系人详情失败:', error);
      Toast.show({
        type: 'error',
        text1: '获取详情失败',
        text2: error.response?.data?.message || error.message || '无法获取联系人详情',
        visibilityTime: 3000,
      });
    } finally {
      setLoading(false);
    }
  }, [contactId]);

  // 删除联系人
  const handleDeleteContact = useCallback(async () => {
    if (!contactId) return;

    Alert.alert(
      '确认删除',
      '确定要删除此紧急联系人吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              setDeleting(true);
              await contactsService.deleteContact(contactId);
              Toast.show({
                type: 'success',
                text1: '删除成功',
                text2: '紧急联系人已删除',
                visibilityTime: 3000,
              });
              router.back();
            } catch (error: any) {
              console.error('删除联系人失败:', error);
              Toast.show({
                type: 'error',
                text1: '删除失败',
                text2: error.response?.data?.message || error.message || '无法删除联系人',
                visibilityTime: 3000,
              });
            } finally {
              setDeleting(false);
            }
          }
        }
      ]
    );
  }, [contactId, router]);

  // 拨打电话
  const handleCallContact = useCallback(async () => {
    if (!contactData) return;

    const tel = `tel:${contactData.phone.replace(/\s/g, '')}`;
    const supported = await Linking.canOpenURL(tel);
    if (!supported) {
      Toast.show({
        type: 'error',
        text1: '无法拨号',
        text2: '当前环境不支持系统拨号',
        visibilityTime: 3000,
      });
      return;
    }
    await Linking.openURL(tel);
  }, [contactData]);

  // 编辑联系人
  const handleEditContact = useCallback(() => {
    router.push('/contacts/edit', { contactId });
  }, [contactId, router]);

  // 页面显示时刷新数据
  useFocusEffect(
    useCallback(() => {
      fetchContactDetail();
    }, [fetchContactDetail])
  );

  if (loading && !contactData) {
    return (
      <Screen backgroundColor={theme.backgroundRoot} statusBarStyle="light">
        <View style={styles.centerContainer}>
          <ThemedText variant="body">加载中...</ThemedText>
        </View>
      </Screen>
    );
  }

  return (
    <Screen backgroundColor={theme.backgroundRoot} statusBarStyle="light">
      <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
        {/* 联系人信息卡片 */}
        {contactData && (
          <ThemedView level="root" style={styles.contactCard}>
            <View style={styles.avatarContainer}>
              <View style={[styles.avatar, { backgroundColor: theme.primary + '20' }]}>
                <FontAwesome6 name="user" size={32} color={theme.primary} />
              </View>
              {contactData.isDefault && (
                <View style={[styles.primaryBadge, { backgroundColor: theme.primary }]}>
                  <ThemedText variant="caption" color={theme.buttonPrimaryText} style={styles.primaryBadgeText}>
                    主要联系人
                  </ThemedText>
                </View>
              )}
            </View>

            <ThemedText variant="h2" style={styles.contactName}>
              {contactData.name}
            </ThemedText>
            <ThemedText variant="body" color={theme.textSecondary} style={styles.contactRelation}>
              {contactData.relationship}
            </ThemedText>
          </ThemedView>
        )}

        {/* 详细信息 */}
        {contactData && (
          <ThemedView level="root" style={styles.detailCard}>
            <ThemedText variant="h4" style={styles.detailTitle}>
              联系信息
            </ThemedText>

            <TouchableOpacity style={styles.detailRow} onPress={handleCallContact}>
              <View style={styles.detailIcon}>
                <FontAwesome6 name="phone" size={20} color={theme.primary} />
              </View>
              <View style={styles.detailContent}>
                <ThemedText variant="caption" color={theme.textMuted}>
                  电话号码
                </ThemedText>
                <ThemedText variant="body" style={styles.detailValue}>
                  {contactData.phone}
                </ThemedText>
              </View>
              <FontAwesome6 name="chevron-right" size={16} color={theme.textMuted} />
            </TouchableOpacity>

            <View style={styles.detailRow}>
              <View style={styles.detailIcon}>
                <FontAwesome6 name="users" size={20} color={theme.primary} />
              </View>
              <View style={styles.detailContent}>
                <ThemedText variant="caption" color={theme.textMuted}>
                  关系
                </ThemedText>
                <ThemedText variant="body" style={styles.detailValue}>
                  {contactData.relationship}
                </ThemedText>
              </View>
            </View>

            <View style={styles.detailRow}>
              <View style={styles.detailIcon}>
                <FontAwesome6 name="sort-numeric-up" size={20} color={theme.primary} />
              </View>
              <View style={styles.detailContent}>
                <ThemedText variant="caption" color={theme.textMuted}>
                  优先级
                </ThemedText>
                <ThemedText variant="body" style={styles.detailValue}>
                  {contactData.priority}
                </ThemedText>
              </View>
            </View>

            {contactData.createdAt ? (
              <View style={styles.detailRow}>
                <View style={styles.detailIcon}>
                  <FontAwesome6 name="calendar" size={20} color={theme.primary} />
                </View>
                <View style={styles.detailContent}>
                  <ThemedText variant="caption" color={theme.textMuted}>
                    添加时间
                  </ThemedText>
                  <ThemedText variant="body" style={styles.detailValue}>
                    {new Date(contactData.createdAt).toLocaleString('zh-CN')}
                  </ThemedText>
                </View>
              </View>
            ) : null}
          </ThemedView>
        )}

        {/* 操作按钮 */}
        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: theme.backgroundTertiary }]}
          onPress={handleEditContact}
        >
          <FontAwesome6 name="pencil" size={18} color={theme.textPrimary} style={styles.actionButtonIcon} />
          <ThemedText variant="body" style={styles.actionButtonText}>
            编辑联系人
          </ThemedText>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, { backgroundColor: theme.error + '15' }]}
          onPress={handleDeleteContact}
          disabled={deleting}
        >
          <FontAwesome6 name="trash" size={18} color={theme.error} style={styles.actionButtonIcon} />
          <ThemedText variant="body" color={theme.error} style={styles.actionButtonText}>
            {deleting ? '删除中...' : '删除联系人'}
          </ThemedText>
        </TouchableOpacity>

        {/* 返回按钮 */}
        <TouchableOpacity
          style={[styles.backButton, { backgroundColor: theme.backgroundTertiary }]}
          onPress={() => router.back()}
        >
          <FontAwesome6 name="arrow-left" size={16} color={theme.textPrimary} style={styles.backButtonIcon} />
          <ThemedText variant="body" style={styles.backButtonText}>
            返回
          </ThemedText>
        </TouchableOpacity>
      </ScrollView>
    </Screen>
  );
}

const createStyles = (theme: any) => StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contactCard: {
    alignItems: 'center',
    padding: 32,
    borderRadius: 16,
    marginBottom: 20,
  },
  avatarContainer: {
    marginBottom: 16,
    position: 'relative',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  primaryBadge: {
    position: 'absolute',
    bottom: -8,
    left: '50%',
    transform: [{ translateX: -50 }],
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  primaryBadgeText: {
    fontSize: 11,
  },
  contactName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  contactRelation: {
    fontSize: 16,
  },
  detailCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 20,
  },
  detailTitle: {
    marginBottom: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.borderLight,
  },
  detailIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.backgroundTertiary,
    marginRight: 16,
  },
  detailContent: {
    flex: 1,
  },
  detailValue: {
    marginTop: 4,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  actionButtonIcon: {
    marginRight: 12,
  },
  actionButtonText: {
    fontWeight: '500',
    fontSize: 16,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 8,
  },
  backButtonIcon: {
    marginRight: 8,
  },
  backButtonText: {
    fontWeight: '500',
  },
});
