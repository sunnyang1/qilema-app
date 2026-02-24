/**
 * 联系人列表页面
 * 温暖守护风格 + UI/UX Pro Max 优化
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  AccessibilityInfo,
  Alert,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  Shadows,
  Animation,
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

const styles = StyleSheet.create({
  // 头部
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.lg,
  },

  headerTitle: {
    ...Typography.h1,
    color: Colors.textPrimary,
    flex: 1,
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

  // 空状态
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

  // 列表容器
  listContainer: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
  },

  // 联系人卡片
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

  // 头像
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

  // 信息区
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

  // 优先级标签
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

  // 信息行
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

  // 操作按钮
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
  },
});

export default function ContactsPage() {
  const router = useSafeRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 检测屏幕阅读器状态
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);

  useEffect(() => {
    // 检测屏幕阅读器
    const subscription = AccessibilityInfo.addEventListener(
      'screenReaderChanged',
      (enabled) => setIsScreenReaderEnabled(enabled)
    );

    AccessibilityInfo.isScreenReaderEnabled().then(setIsScreenReaderEnabled);

    // 加载联系人数据
    loadContacts();

    return () => {
      subscription?.remove();
    };
  }, []);

  // 加载联系人数据
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

  // 下拉刷新
  const onRefresh = async () => {
    setRefreshing(true);
    await loadContacts();
    setRefreshing(false);
  };

  // 添加联系人
  const handleAddContact = () => {
    router.push('/contacts/edit');
  };

  // 编辑联系人
  const handleEditContact = (contact: Contact) => {
    router.push('/contacts/edit', { contactId: contact.contactId });
  };

  // 拨打电话
  const handleCallPhone = async (phone: string) => {
    try {
      // TODO: 使用 Linking API 拨打电话
      Alert.alert('拨打电话', `正在拨打 ${phone}`);
      console.log(`Calling ${phone}`);
    } catch (error) {
      Alert.alert('错误', '无法拨打电话');
    }
  };

  // 删除联系人
  const handleDeleteContact = useCallback(async (contact: EmergencyContact) => {
    Alert.alert(
      '确认删除',
      `确定要删除联系人"${contact.name}"吗？`,
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              await contactsService.deleteContact(contact.contactId);
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
      ]
    );
  }, [loadContacts]);

  // 获取优先级颜色
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

  // 获取优先级文本
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

  // 渲染空状态
  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <FontAwesome6
        name="address-book"
        size={64}
        color={Colors.textMuted}
        style={styles.emptyIcon}
      />
      <ThemedText variant="bodyMedium" color={Colors.textPrimary} style={styles.emptyTitle}>
        暂无紧急联系人
      </ThemedText>
      <ThemedText variant="small" color={Colors.textSecondary} style={styles.emptySubtitle}>
        至少需要添加1位紧急联系人
      </ThemedText>
      <TouchableOpacity
        style={styles.emptyButton}
        onPress={handleAddContact}
        hitSlop={HitSlop.medium}
        accessible
        accessibilityLabel="添加联系人"
        accessibilityHint="点击添加紧急联系人"
        accessibilityRole="button"
      >
        <FontAwesome6
          name="plus"
          size={20}
          color={Colors.backgroundDefault}
        />
        <ThemedText variant="bodyMedium" color={Colors.backgroundDefault} style={styles.emptyButtonText}>
          添加联系人
        </ThemedText>
      </TouchableOpacity>
    </View>
  );

  // 渲染联系人卡片
  const renderContactCard = ({ item }: { item: EmergencyContact }) => (
    <TouchableOpacity
      style={styles.contactCard}
      onPress={() => handleEditContact(item)}
      onLongPress={() => handleDeleteContact(item)}
      hitSlop={HitSlop.small}
      delayLongPress={500}
      accessible
      accessibilityLabel={`${item.name}，${item.relationship}，电话${item.phone}`}
      accessibilityHint="点击编辑联系人信息，长按删除联系人"
      accessibilityRole="button"
    >
      {/* 头像 */}
      <View style={styles.avatar} accessible={false}>
        <FontAwesome6
          name="user"
          size={24}
          color={Colors.primaryDark}
          style={styles.avatarIcon}
        />
      </View>

      {/* 信息区 */}
      <View style={styles.infoContainer}>
        {/* 姓名和优先级 */}
        <View style={styles.nameRow}>
          <ThemedText variant="bodyMedium" color={Colors.textPrimary} style={styles.nameText}>
            {item.name}
          </ThemedText>
          <View
            style={[
              styles.priorityBadge,
              { backgroundColor: getPriorityColor(item.priority) },
            ]}
            accessible
            accessibilityLabel={`${getPriorityText(item.priority)}`}
          >
            <ThemedText variant="captionMedium" color={Colors.backgroundDefault} style={styles.priorityBadgeText}>
              {getPriorityText(item.priority)}
            </ThemedText>
          </View>
        </View>

        {/* 电话 */}
        <View style={styles.infoRow}>
          <FontAwesome6
            name="phone"
            size={14}
            color={Colors.textSecondary}
            style={styles.infoRowIcon}
          />
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.infoRowText}>
            {item.phone}
          </ThemedText>
        </View>

        {/* 关系 */}
        <View style={styles.infoRow}>
          <FontAwesome6
            name="users"
            size={14}
            color={Colors.textSecondary}
            style={styles.infoRowIcon}
          />
          <ThemedText variant="small" color={Colors.textSecondary} style={styles.infoRowText}>
            {item.relationship}
          </ThemedText>
        </View>
      </View>

      {/* 操作按钮 */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[styles.actionButton, styles.callButton]}
          onPress={() => handleCallPhone(item.phone)}
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
      {/* 头部 */}
      <View style={styles.header} accessible accessibilityLabel="联系人列表页面">
        <ThemedText variant="h1" color={Colors.textPrimary} style={styles.headerTitle}>
          紧急联系人
        </ThemedText>
        <TouchableOpacity
          style={styles.addButton}
          onPress={handleAddContact}
          hitSlop={HitSlop.medium}
          accessible
          accessibilityLabel="添加联系人"
          accessibilityHint="点击添加新的紧急联系人"
          accessibilityRole="button"
        >
          <FontAwesome6 name="plus" size={20} color={Colors.backgroundDefault} />
        </TouchableOpacity>
      </View>

      {/* 内容区 */}
      {isLoading ? (
        <View style={styles.emptyContainer}>
          <ThemedText variant="body" color={Colors.textSecondary}>
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
          keyExtractor={(item) => item.contactId}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={Colors.primary}
            />
          }
          contentContainerStyle={{ paddingBottom: Spacing['5xl'] }}
          accessible
          accessibilityLabel="联系人列表"
        />
      )}
      <Toast />
    </Screen>
  );
}
