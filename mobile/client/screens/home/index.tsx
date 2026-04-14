import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/contexts/AuthContext';
import { FontAwesome6 } from '@expo/vector-icons';

const styles = (theme: any) => StyleSheet.create({
  container: { flex: 1 },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  header: { alignItems: 'center', marginBottom: 48 },
  logo: { fontSize: 80, marginBottom: 16 },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
  helper: {
    fontSize: 13,
    marginTop: 8,
  },
  sectionCard: {
    width: '100%',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 28,
  },
  sectionTitle: {
    marginBottom: 4,
  },
  sectionSubtitle: {
    marginBottom: 14,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 16,
    marginBottom: 32,
  },
  gridItem: {
    width: 100,
    height: 100,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  gridIcon: { fontSize: 32, marginBottom: 8 },
  gridLabel: {
    fontSize: 12,
  },
  button: {
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
    borderWidth: 1,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default function HomePage() {
  const { theme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <View style={styles(theme).content}>
        {/* Header */}
        <View style={styles(theme).header}>
          <Text style={styles(theme).logo}>🏥</Text>
          <ThemedText variant="h2" color={theme.textPrimary} style={styles(theme).title}>
            起了吗
          </ThemedText>
          <ThemedText variant="body" color={theme.textSecondary}>
            你好，{user?.username || '用户'}
          </ThemedText>
          <ThemedText variant="small" color={theme.textMuted} style={styles(theme).helper}>
            选择一个模块继续使用
          </ThemedText>
        </View>

        {/* 功能网格 */}
        <View
          style={[
            styles(theme).sectionCard,
            { backgroundColor: theme.backgroundDefault, borderColor: theme.borderLight },
          ]}
        >
          <ThemedText variant="bodyMedium" color={theme.textPrimary} style={styles(theme).sectionTitle}>
            快捷入口
          </ThemedText>
          <ThemedText variant="small" color={theme.textSecondary} style={styles(theme).sectionSubtitle}>
            常用功能一键直达
          </ThemedText>
          <View style={styles(theme).grid}>
          <TouchableOpacity style={[styles(theme).gridItem, { backgroundColor: theme.primary, borderColor: theme.primaryDark }]} activeOpacity={0.88}>
            <FontAwesome6 name="heart-pulse" size={32} color="white" style={{ marginBottom: 8 }} />
            <ThemedText variant="smallMedium" color="white" style={styles(theme).gridLabel}>
              签到
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity style={[styles(theme).gridItem, { backgroundColor: theme.error, borderColor: theme.error }]} activeOpacity={0.88}>
            <FontAwesome6 name="phone-volume" size={32} color="white" style={{ marginBottom: 8 }} />
            <ThemedText variant="smallMedium" color="white" style={styles(theme).gridLabel}>
              SOS
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity style={[styles(theme).gridItem, { backgroundColor: theme.success, borderColor: theme.success }]} activeOpacity={0.88}>
            <FontAwesome6 name="address-book" size={32} color="white" style={{ marginBottom: 8 }} />
            <ThemedText variant="smallMedium" color="white" style={styles(theme).gridLabel}>
              联系人
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity style={[styles(theme).gridItem, { backgroundColor: theme.info, borderColor: theme.info }]} activeOpacity={0.88}>
            <FontAwesome6 name="notes-medical" size={32} color="white" style={{ marginBottom: 8 }} />
            <ThemedText variant="smallMedium" color="white" style={styles(theme).gridLabel}>
              健康
            </ThemedText>
          </TouchableOpacity>
          </View>
        </View>

        {/* 登出按钮 */}
        <TouchableOpacity
          style={[styles(theme).button, { backgroundColor: theme.backgroundDefault, borderColor: theme.border }]}
          onPress={logout}
          activeOpacity={0.85}
        >
          <ThemedText variant="bodyMedium" color={theme.textSecondary} style={styles(theme).buttonText}>
            退出登录
          </ThemedText>
        </TouchableOpacity>
      </View>
    </Screen>
  );
}
