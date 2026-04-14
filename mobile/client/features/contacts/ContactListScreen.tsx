/**
 * 紧急联系人列表（US-P05）
 * R-W5：自 `screens/contacts` 迁入 `features/contacts`，路由仍经 `app/(tabs)/contacts` → screens 薄封装。
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  AccessibilityInfo,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import EmptyState from '@/components/EmptyState';
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

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.md,
  },

  headerTextBlock: {
    flex: 1,
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

  countBadge: {
    marginTop: Spacing.sm,
    alignSelf: 'flex-start',
    backgroundColor: Colors.backgroundTertiary,
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: 4,
  },

  countBadgeText: {
    ...Typography.captionMedium,
    color: Colors.textSecondary,
  },

  addButton: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...Shadows.medium,
  },

  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },

  emptyIcon: {
    fontSize: 64,
    marginBottom: Spacing.lg,
  },

  emptyTitle: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
    textAlign: 'center',
  },

  emptySubtitle: {
    ...Typography.small,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
    textAlign: 'center',
  },

  emptyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 48,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.xl,
    backgroundColor: Colors.primary,
    gap: Spacing.sm,
    ...Shadows.medium,
  },

  emptyButtonText: {
    ...Typography.bodyMedium,
    color: Colors.backgroundDefault,
  },

  listContainer: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
  },

  listContentContainer: {
    paddingTop: Spacing.sm,
    paddingBottom: Spacing['5xl'],
  },

  contactCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.backgroundDefault,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.borderLight,
    ...Shadows.medium,
    overflow: 'hidden',
  },

  avatar: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },

  avatarIcon: {
    fontSize: 24,
    color: Colors.primaryDark,
  },

  infoContainer: {
    flex: 1,
  },

  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },

  nameText: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
    marginRight: Spacing.sm,
  },

  priorityBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.lg,
  },

  priorityBadgeText: {
    ...Typography.captionMedium,
    color: Colors.backgroundDefault,
    fontWeight: 'bold',
  },

  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },

  infoRowIcon: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginRight: Spacing.xs,
  },

  infoRowText: {
    ...Typography.small,
    color: Colors.textSecondary,
  },

  actionsContainer: {
    flexDirection: 'row',
    gap: Spacing.xs,
  },

  actionButton: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },

  callButton: {
    backgroundColor: Colors.accent,
    ...Shadows.soft,
  },

  editButton: {
    backgroundColor: Colors.backgroundTertiary,
    borderWidth: 1,
    borderColor: Colors.border,
  },

  cardSeparator: {
    height: Spacing.md,
  },

  loadingText: {
    marginTop: Spacing.md,
  },
});

export default function ContactListScreen() {
  const router = useSafeRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [, setIsScreenReaderEnabled] = useState(false);

  useEffect(() => {
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      (enabled) => setIsScreenReaderEnabled(enabled)
    );

    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);

    loadContacts();

    return () => {
      subscription?.remove();
    };
  }, []);

  const loadContacts = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await contactsService.getContacts();
      setContacts(data);
    } catch (error: any) {
      console.error('加载联系人失败:', error);
      Toast.show({
        type: 'error',
        text1: '加载失败',
        text2: error.message || '请稍后重试',
        visibilityTime: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadContacts();
    setRefreshing(false);
  };

  const handleAddContact = () => {
    router.push('/contacts/edit');
  };

  const handleEditContact = (contact: EmergencyContact) => {
    router.push('/contacts/edit', { contactId: String(contact.id) });
  };

  const handleCallPhone = async (phone: string) => {
    try {
      Alert.alert('拨打电话', `正在拨打 ${phone}`);
      console.log(`Calling ${phone}`);
    } catch (error) {
      Alert.alert('错误', '无法拨打电话');
    }
  };

  const handleDeleteContact = useCallback(
    async (contact: EmergencyContact) => {
      Alert.alert('确认删除', `确定要删除联系人"${contact.name}"吗？`, [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              await contactsService.deleteContact(String(contact.id));
              Toast.show({
                type: 'success',
                text1: '删除成功',
                visibilityTime: 2000,
              });
              await loadContacts();
            } catch (error: any) {
              Toast.show({
                type: 'error',
                text1: '删除失败',
                text2: error.message || '请稍后重试',
                visibilityTime: 3000,
              });
            }
          },
        },
      ]);
    },
    [loadContacts]
  );

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return Colors.error;
      case 2:
        return Colors.warning;
      case 3:
        return Colors.info;
      default:
        return Colors.textSecondary;
    }
  };

  const getPriorityText = (priority: number) => {
    switch (priority) {
      case 1:
        return '高优先';
      case 2:
        return '中优先';
      case 3:
        return '低优先';
      default:
        return '普通';
    }
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <EmptyState
        icon="address-book"
        title="暂无紧急联系人"
        subtitle="至少需要添加 1 位紧急联系人"
        actionLabel="添加联系人"
        onActionPress={handleAddContact}
      />
    </View>
  );

  const renderContactCard = ({ item }: { item: EmergencyContact }) => (
    <TouchableOpacity
      style={styles.contactCard}
      onPress={() => handleEditContact(item)}
      onLongPress={() => handleDeleteContact(item)}
      activeOpacity={0.9}
      hitSlop={HitSlop.small}
      delayLongPress={500}
      accessible
      accessibilityLabel={`${item.name}，${item.relationship}，电话${item.phone}`}
      accessibilityHint="点击编辑联系人信息，长按删除联系人"
      accessibilityRole="button"
    >
      <View style={styles.avatar} accessible={false}>
        <FontAwesome6 name="user" size={24} color={Colors.primaryDark} style={styles.avatarIcon} />
      </View>

      <View style={styles.infoContainer}>
        <View style={styles.nameRow}>
          <ThemedText variant="bodyMedium" color={Colors.textPrimary} style={styles.nameText}>
            {item.name}
          </ThemedText>
          <View
            style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}
            accessible
            accessibilityLabel={`${getPriorityText(item.priority)}`}
          >
            <ThemedText variant="captionMedium" color={Colors.backgroundDefault} style={styles.priorityBadgeText}>
              {getPriorityText(item.priority)}
            </ThemedText>
          </View>
        </View>

        <View style={styles.infoRow}>
          <FontAwesome6 name="phone" size={14} color={Colors.textSecondary} style={styles.infoRowIcon} />
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.infoRowText}>
            {item.phone}
          </ThemedText>
        </View>

        <View style={styles.infoRow}>
          <FontAwesome6 name="users" size={14} color={Colors.textSecondary} style={styles.infoRowIcon} />
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.infoRowText}>
            {item.relationship}
          </ThemedText>
        </View>
      </View>

      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[styles.actionButton, styles.callButton]}
          onPress={() => handleCallPhone(item.phone)}
          activeOpacity={0.85}
          hitSlop={HitSlop.small}
          accessible
          accessibilityLabel={`拨打${item.name}的电话`}
          accessibilityHint={`点击拨打${item.phone}`}
          accessibilityRole="button"
        >
          <FontAwesome6 name="phone" size={20} color={Colors.backgroundDefault} />
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.editButton]}
          onPress={() => handleEditContact(item)}
          activeOpacity={0.85}
          hitSlop={HitSlop.small}
          accessible
          accessibilityLabel={`编辑${item.name}的信息`}
          accessibilityHint="点击编辑联系人"
          accessibilityRole="button"
        >
          <FontAwesome6 name="pencil" size={16} color={Colors.textPrimary} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      <View style={styles.header} accessible accessibilityLabel="联系人列表页面">
        <View style={styles.headerTextBlock}>
          <ThemedText variant="h1" color={Colors.textPrimary} style={styles.headerTitle}>
            紧急联系人
          </ThemedText>
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.headerSubtitle}>
            一键触达最重要的人
          </ThemedText>
          <View style={styles.countBadge}>
            <ThemedText variant="captionMedium" color={Colors.textSecondary} style={styles.countBadgeText}>
              共 {contacts.length} 位联系人
            </ThemedText>
          </View>
        </View>
        <TouchableOpacity
          style={styles.addButton}
          onPress={handleAddContact}
          activeOpacity={0.88}
          hitSlop={HitSlop.medium}
          accessible
          accessibilityLabel="添加联系人"
          accessibilityHint="点击添加新的紧急联系人"
          accessibilityRole="button"
        >
          <FontAwesome6 name="plus" size={20} color={Colors.backgroundDefault} />
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="small" color={Colors.primary} />
          <ThemedText variant="body" color={Colors.textSecondary} style={styles.loadingText}>
            加载中...
          </ThemedText>
        </View>
      ) : contacts.length === 0 ? (
        renderEmptyState()
      ) : (
        <FlatList
          style={styles.listContainer}
          data={contacts}
          renderItem={renderContactCard}
          keyExtractor={(item) => item.contactId || String(item.id)}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />
          }
          ItemSeparatorComponent={() => <View style={styles.cardSeparator} />}
          contentContainerStyle={styles.listContentContainer}
          accessible
          accessibilityLabel="联系人列表"
        />
      )}
      <Toast />
    </Screen>
  );
}
