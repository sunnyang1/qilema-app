import React from 'react';
import { View, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import { Spacing, BorderRadius } from '@/constants/theme-warm';
import { useSafeRouter } from '@/hooks/useSafeRouter';

export default function HealthScreen() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const styles = createStyles(theme);

  const healthItems = [
    {
      id: 'medical-history',
      title: '病史记录',
      description: '查看和管理病史记录',
      icon: 'notes-medical',
      color: theme.primary,
      route: '/health/medical-history',
    },
    {
      id: 'medication',
      title: '用药管理',
      description: '查看和管理用药记录',
      icon: 'pills',
      color: theme.accent,
      route: '/health/medication',
    },
    {
      id: 'allergies',
      title: '过敏史',
      description: '查看和管理过敏史',
      icon: 'allergies',
      color: theme.warning,
      route: '/health/allergies',
    },
    {
      id: 'vaccination',
      title: '疫苗接种',
      description: '查看疫苗接种记录',
      icon: 'syringe',
      color: theme.info,
      route: '/health/vaccination',
    },
  ];

  const handleItemPress = (route: string) => {
    router.push(route);
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <ThemedText variant="h1" color={theme.textPrimary}>
            健康档案
          </ThemedText>
          <ThemedText variant="body" color={theme.textSecondary}>
            管理您的健康信息，守护您的安全
          </ThemedText>
          <ThemedText variant="small" color={theme.textMuted} style={styles.headerHelper}>
            点击卡片可进入对应模块编辑
          </ThemedText>
        </View>

        <View style={styles.grid}>
          {healthItems.map((item) => (
            <TouchableOpacity
              key={item.id}
              style={styles.card}
              onPress={() => handleItemPress(item.route)}
              activeOpacity={0.86}
            >
              <View style={[styles.iconContainer, { backgroundColor: `${item.color}15` }]}>
                <FontAwesome6 name={item.icon as any} size={32} color={item.color} />
              </View>
              <ThemedText variant="title" color={theme.textPrimary} style={styles.cardTitle}>
                {item.title}
              </ThemedText>
              <ThemedText variant="small" color={theme.textMuted} style={styles.cardDescription}>
                {item.description}
              </ThemedText>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={styles.exportButton}
          onPress={() => router.push('/health/export')}
          activeOpacity={0.88}
        >
          <FontAwesome6 name="file-export" size={20} color="#FFFFFF" style={styles.buttonIcon} />
          <ThemedText variant="bodyMedium" color="#FFFFFF">
            导出健康档案
          </ThemedText>
        </TouchableOpacity>
      </ScrollView>
    </Screen>
  );
}

const createStyles = (theme: any) => StyleSheet.create({
  container: { flex: 1 },
  content: {
    paddingBottom: Spacing['3xl'],
  },
  header: {
    padding: Spacing['2xl'],
    paddingBottom: Spacing.xl,
  },
  headerHelper: {
    marginTop: Spacing.xs,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: Spacing.lg,
    gap: Spacing.lg,
  },
  card: {
    width: '47%',
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: theme.borderLight,
    backgroundColor: theme.backgroundDefault,
    shadowColor: theme.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: BorderRadius.lg,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  cardTitle: {
    marginBottom: Spacing.xs,
  },
  cardDescription: {
    lineHeight: 20,
  },
  exportButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    margin: Spacing['2xl'],
    paddingVertical: Spacing.lg,
    paddingHorizontal: Spacing['2xl'],
    borderRadius: BorderRadius.lg,
    backgroundColor: theme.primary,
    shadowColor: theme.shadowStrong,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonIcon: {
    marginRight: Spacing.md,
  },
});
