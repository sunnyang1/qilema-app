import React from 'react';
import { View, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import { Spacing, BorderRadius } from '@/constants/theme-warm';
import { useSafeRouter } from '@/hooks/useSafeRouter';

export default function HealthScreen() {
  const { theme, isDark } = useTheme();
  const router = useSafeRouter();

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
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <ThemedText variant="h1" color={theme.textPrimary}>
          健康档案
        </ThemedText>
        <ThemedText variant="body" color={theme.textSecondary}>
          管理您的健康信息，守护您的安全
        </ThemedText>
      </View>

      <View style={styles.grid}>
        {healthItems.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={[styles.card, { backgroundColor: theme.backgroundDefault }]}
            onPress={() => handleItemPress(item.route)}
            activeOpacity={0.7}
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
        style={[styles.exportButton, { backgroundColor: theme.primary }]}
        onPress={() => router.push('/health/export')}
        activeOpacity={0.8}
      >
        <FontAwesome6 name="file-export" size={20} color="#FFFFFF" style={styles.buttonIcon} />
        <ThemedText variant="bodyMedium" color="#FFFFFF">
          导出健康档案
        </ThemedText>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  header: {
    padding: Spacing['2xl'],
    paddingBottom: Spacing.xl,
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonIcon: {
    marginRight: Spacing.md,
  },
});
