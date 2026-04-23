/**
 * 紧急联系人列表（增强版）
 * 改进：
 * - 头像首字母彩色背景
 * - 优先级视觉层次（1/2/3 不同卡片风格）
 * - 向左滑动展示删除操作
 * - 添加按钮 FAB 式悬浮
 * - 空状态动画插画
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  AccessibilityInfo,
  Alert,
  ActivityIndicator,
  Animated,
  PanResponder,
  useWindowDimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import EmptyState from '@/components/EmptyState';
import {
  lightColors,
  spacing,
  borderRadius,
  hitSlop,
} from '@/design-system';
import { createShadows } from '@/design-system';

const shadows = createShadows(lightColors.shadow, lightColors.shadowStrong);
import { contactsService, EmergencyContact } from '@/services/contacts';
import Toast from 'react-native-toast-message';

// 头像背景色（根据首字母哈希）
const AVATAR_COLORS = [
  ['#FF6B6B', '#FF8E53'],
  ['#4FACFE', '#00F2FE'],
  ['#43E97B', '#38F9D7'],
  ['#F093FB', '#F5576C'],
  ['#667EEA', '#764BA2'],
  ['#FCC89A', '#F7971E'],
];

function getAvatarGradient(name: string): [string, string] {
  const idx = name.charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx] as [string, string];
}

// 优先级配置
const PRIORITY_CONFIG: Record<number, { label: string; color: string; border: boolean }> = {
  1: { label: '首要', color: lightColors.error, border: true },
  2: { label: '次要', color: lightColors.warning, border: false },
  3: { label: '普通', color: lightColors.info, border: false },
};

// 单张联系人卡片（支持左滑删除）
function ContactCard({
  contact,
  onEdit,
  onDelete,
  onCall,
}: {
  contact: EmergencyContact;
  onEdit: () => void;
  onDelete: () => void;
  onCall: () => void;
}) {
  const translateX = useRef(new Animated.Value(0)).current;
  const [swiped, setSwiped] = useState(false);
  const priority = contact.priority || 3;
  const pConfig = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG[3];
  const avatarGradient = getAvatarGradient(contact.name);

  const panResponder = PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dx) > 8 && Math.abs(g.dy) < 20,
    onPanResponderMove: (_, g) => {
      if (g.dx < 0) {
        translateX.setValue(Math.max(g.dx, -80));
      } else if (swiped) {
        translateX.setValue(Math.min(g.dx - 80, 0));
      }
    },
    onPanResponderRelease: (_, g) => {
      if (g.dx < -40) {
        // 打开
        Animated.spring(translateX, { toValue: -80, useNativeDriver: true, speed: 20 }).start();
        setSwiped(true);
      } else {
        // 关闭
        Animated.spring(translateX, { toValue: 0, useNativeDriver: true, speed: 20 }).start();
        setSwiped(false);
      }
    },
  });

  const closeSwipe = () => {
    Animated.spring(translateX, { toValue: 0, useNativeDriver: true, speed: 20 }).start();
    setSwiped(false);
  };

  return (
    <View style={cardStyles.container}>
      {/* 背景删除按钮 */}
      <View style={cardStyles.deleteBackground}>
        <TouchableOpacity
          style={cardStyles.deleteBtn}
          onPress={() => { closeSwipe(); onDelete(); }}
          accessibilityRole="button"
          accessibilityLabel="删除联系人"
        >
          <FontAwesome6 name="trash" size={20} color="#fff" />
          <ThemedText variant="caption" color="#fff" style={cardStyles.deleteBtnText}>删除</ThemedText>
        </TouchableOpacity>
      </View>

      {/* 滑动内容 */}
      <Animated.View
        style={[cardStyles.card, pConfig.border && cardStyles.cardHighlight, { transform: [{ translateX }] }]}
        {...panResponder.panHandlers}
      >
        {priority === 1 && (
          <View style={cardStyles.priorityStrip} />
        )}

        <TouchableOpacity
          style={cardStyles.inner}
          onPress={swiped ? closeSwipe : onEdit}
          activeOpacity={0.88}
          accessible
          accessibilityLabel={`${contact.name}，${contact.relationship}`}
          accessibilityRole="button"
        >
          {/* 头像 */}
          <LinearGradient colors={avatarGradient} style={cardStyles.avatar}>
            <ThemedText style={cardStyles.avatarText}>{contact.name.charAt(0)}</ThemedText>
          </LinearGradient>

          {/* 信息 */}
          <View style={cardStyles.info}>
            <View style={cardStyles.nameRow}>
              <ThemedText variant="bodyMedium" color={lightColors.textPrimary} style={cardStyles.name}>
                {contact.name}
              </ThemedText>
              <View style={[cardStyles.priorityBadge, { backgroundColor: pConfig.color + '18' }]}>
                <ThemedText variant="caption" color={pConfig.color} style={cardStyles.priorityText}>
                  {pConfig.label}
                </ThemedText>
              </View>
            </View>
            <View style={cardStyles.infoRow}>
              <FontAwesome6 name="users" size={12} color={lightColors.textMuted} />
              <ThemedText variant="small" color={lightColors.textSecondary}>{contact.relationship}</ThemedText>
            </View>
            <View style={cardStyles.infoRow}>
              <FontAwesome6 name="phone" size={12} color={lightColors.textMuted} />
              <ThemedText variant="small" color={lightColors.textSecondary}>{contact.phone}</ThemedText>
            </View>
          </View>

          {/* 操作按钮 */}
          <View style={cardStyles.actions}>
            <TouchableOpacity
              style={[cardStyles.actionBtn, { backgroundColor: lightColors.accent }]}
              onPress={onCall}
              activeOpacity={0.85}
              hitSlop={hitSlop.small}
              accessibilityRole="button"
              accessibilityLabel={`拨打${contact.name}的电话`}
            >
              <FontAwesome6 name="phone" size={18} color="#fff" />
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
}

const cardStyles = StyleSheet.create({
  container: {
    position: 'relative',
    overflow: 'hidden',
    borderRadius: borderRadius.xl,
    marginBottom: spacing.md,
  },
  deleteBackground: {
    position: 'absolute',
    right: 0,
    top: 0,
    bottom: 0,
    width: 80,
    backgroundColor: lightColors.error,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: borderRadius.xl,
  },
  deleteBtn: {
    alignItems: 'center',
    gap: 2,
    paddingHorizontal: 8,
  },
  deleteBtnText: { fontSize: 11, color: '#fff', fontWeight: '600' },
  card: {
    backgroundColor: lightColors.backgroundDefault,
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: lightColors.borderLight,
    ...shadows.medium,
  },
  cardHighlight: {
    borderColor: lightColors.error + '50',
    borderWidth: 1.5,
  },
  priorityStrip: {
    height: 3,
    backgroundColor: lightColors.error,
    borderRadius: 0,
  },
  inner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    gap: spacing.md,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 22,
    fontWeight: '800',
    color: '#fff',
  },
  info: { flex: 1, gap: 3 },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  name: { fontSize: 15, fontWeight: '700', color: lightColors.textPrimary },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 100,
  },
  priorityText: { fontSize: 11, fontWeight: '600' },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 5 },
  actions: { gap: spacing.xs },
  actionBtn: {
    width: 44,
    height: 44,
    borderRadius: borderRadius.full,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.soft,
  },
});

// 主页面
export default function ContactListScreen() {
  const router = useSafeRouter();
  const { width } = useWindowDimensions();
  const [refreshing, setRefreshing] = useState(false);
  const [contacts, setContacts] = useState<EmergencyContact[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fabScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const sub = AccessibilityInfo.addEventListener('screenReaderChanged', () => {});
    loadContacts();
    return () => sub?.remove();
  }, []);

  const loadContacts = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await contactsService.getContacts();
      setContacts(data);
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '加载失败', text2: error.message || '请稍后重试', visibilityTime: 3000 });
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
    Animated.sequence([
      Animated.timing(fabScale, { toValue: 0.85, duration: 80, useNativeDriver: true }),
      Animated.spring(fabScale, { toValue: 1, tension: 200, useNativeDriver: true }),
    ]).start();
    router.push('/contacts/edit');
  };

  const handleEdit = (contact: EmergencyContact) =>
    router.push('/contacts/edit', { contactId: String(contact.id) });

  const handleCall = (phone: string) =>
    Alert.alert('拨打电话', `正在拨打 ${phone}`);

  const handleDelete = useCallback(
    async (contact: EmergencyContact) => {
      Alert.alert('确认删除', `确定删除"${contact.name}"？`, [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: async () => {
            try {
              await contactsService.deleteContact(String(contact.id));
              Toast.show({ type: 'success', text1: '删除成功', visibilityTime: 2000 });
              await loadContacts();
            } catch (e: any) {
              Toast.show({ type: 'error', text1: '删除失败', text2: e.message, visibilityTime: 3000 });
            }
          },
        },
      ]);
    },
    [loadContacts]
  );

  const sortedContacts = [...contacts].sort((a, b) => (a.priority || 99) - (b.priority || 99));

  return (
    <Screen backgroundColor={lightColors.backgroundRoot}>
      {/* 顶部 Banner */}
      <LinearGradient
        colors={['#667EEA', '#764BA2']}
        style={styles.banner}
      >
        <View style={styles.bannerContent}>
          <View>
            <ThemedText variant="h2" color="#fff" style={styles.bannerTitle}>紧急联系人</ThemedText>
            <ThemedText variant="body" color="rgba(255,255,255,0.85)" style={styles.bannerSubtitle}>
              一键触达最重要的人
            </ThemedText>
            <View style={styles.countBadge}>
              <FontAwesome6 name="users" size={12} color="rgba(255,255,255,0.8)" />
              <ThemedText variant="caption" color="rgba(255,255,255,0.9)" style={styles.countText}>
                共 {contacts.length} 位联系人
              </ThemedText>
            </View>
          </View>
          <View style={styles.bannerIllustration}>
            <ThemedText style={{ fontSize: 52, opacity: 0.25 }}>📱</ThemedText>
          </View>
        </View>
      </LinearGradient>

      {/* 提示 */}
      {contacts.length > 0 && (
        <View style={[styles.tipBar, { backgroundColor: lightColors.info + '12' }]}>
          <FontAwesome6 name="circle-info" size={13} color={lightColors.info} />
          <ThemedText variant="caption" color={lightColors.info} style={styles.tipText}>
            左滑联系人卡片可快速删除
          </ThemedText>
        </View>
      )}

      {/* 内容 */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={lightColors.primary} />
          <ThemedText variant="body" color={lightColors.textSecondary} style={styles.loadingText}>加载中...</ThemedText>
        </View>
      ) : contacts.length === 0 ? (
        <View style={styles.emptyContainer}>
          <EmptyState
            icon="address-book"
            title="暂无紧急联系人"
            subtitle="至少需要添加 1 位紧急联系人，SOS 时系统才能通知到家人"
            actionLabel="+ 添加联系人"
            onActionPress={handleAddContact}
          />
        </View>
      ) : (
        <FlatList
          style={styles.list}
          data={sortedContacts}
          keyExtractor={(item) => item.contactId || String(item.id)}
          renderItem={({ item }) => (
            <ContactCard
              contact={item}
              onEdit={() => handleEdit(item)}
              onDelete={() => handleDelete(item)}
              onCall={() => handleCall(item.phone)}
            />
          )}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={lightColors.primary} />}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* FAB 添加按钮 */}
      <Animated.View style={[styles.fab, { transform: [{ scale: fabScale }] }]}>
        <TouchableOpacity
          style={styles.fabBtn}
          onPress={handleAddContact}
          activeOpacity={0.88}
          accessibilityRole="button"
          accessibilityLabel="添加紧急联系人"
        >
          <LinearGradient
            colors={['#667EEA', '#764BA2']}
            style={styles.fabGradient}
          >
            <FontAwesome6 name="plus" size={24} color="#fff" />
          </LinearGradient>
        </TouchableOpacity>
      </Animated.View>

      <Toast />
    </Screen>
  );
}

const styles = StyleSheet.create({
  banner: {
    paddingHorizontal: spacing.lg,
    paddingTop: 56,
    paddingBottom: spacing.xl,
  },
  bannerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  bannerTitle: { fontSize: 24, fontWeight: '800', color: '#fff', marginBottom: 4 },
  bannerSubtitle: { fontSize: 13, color: 'rgba(255,255,255,0.85)', marginBottom: spacing.sm },
  countBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 100,
    alignSelf: 'flex-start',
  },
  countText: { fontSize: 12, color: 'rgba(255,255,255,0.9)' },
  bannerIllustration: { opacity: 0.5 },
  tipBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  tipText: { fontSize: 12 },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.md,
  },
  loadingText: { marginTop: spacing.sm },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
  },
  list: { flex: 1 },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: 100,
  },
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 24,
  },
  fabBtn: {
    width: 60,
    height: 60,
    borderRadius: 30,
    overflow: 'hidden',
    shadowColor: '#667EEA',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.45,
    shadowRadius: 12,
    elevation: 10,
  },
  fabGradient: {
    width: 60,
    height: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
