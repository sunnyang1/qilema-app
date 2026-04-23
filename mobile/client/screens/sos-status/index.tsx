import React, { useCallback, useEffect, useState, useMemo } from 'react';
import { View, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { useSafeRouter, useSafeSearchParams } from '@/hooks/useSafeRouter';
import { apiClient } from '@/utils/api';
import { Screen } from '@/components/Screen';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import Toast from 'react-native-toast-message';

interface SOSStatusParams {
  requestId: string;
}

interface SOSRequestData {
  sos_id: string;
  user_id: string;
  latitude: number;
  longitude: number;
  address?: string;
  emergency_reason?: string;
  call_120: boolean;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export default function SOSStatusScreen() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { requestId } = useSafeSearchParams<SOSStatusParams>();
  const [sosData, setSosData] = useState<SOSRequestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  const styles = useMemo(() => createStyles(theme), [theme]);

  // 获取 SOS 状态
  const fetchSOSStatus = useCallback(async () => {
    if (!requestId) {
      Toast.show({
        type: 'error',
        text1: '参数错误',
        text2: '缺少 SOS 请求 ID',
        visibilityTime: 3000,
      });
      return;
    }

    try {
      setLoading(true);
      /**
       * 服务端文件：backend/app/api/sos_requests.py
       * 接口：GET /api/v1/sos/{sos_id}
       * Path 参数：sos_id: string
       */
      const data = await apiClient.get<SOSRequestData>(`/api/v1/sos/${requestId}`);
      setSosData(data);
    } catch (error: any) {
      console.error('获取 SOS 状态失败:', error);
      Toast.show({
        type: 'error',
        text1: '获取状态失败',
        text2: error.response?.data?.message || error.message || '无法获取 SOS 状态',
        visibilityTime: 3000,
      });
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  // 取消 SOS 求助
  const handleCancelSOS = useCallback(async () => {
    if (!requestId) return;

    Alert.alert(
      '确认取消',
      '确定要取消此 SOS 求助吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          style: 'destructive',
          onPress: async () => {
            try {
              setCancelling(true);
              /**
               * 服务端文件：backend/app/api/sos_requests.py
               * 接口：PUT /api/v1/sos/{sos_id}/cancel
               * Path 参数：sos_id: string
               */
              await apiClient.put(`/api/v1/sos/${requestId}/cancel`);
              Toast.show({
                type: 'success',
                text1: '取消成功',
                text2: 'SOS 求助已取消',
                visibilityTime: 3000,
              });
              // 刷新状态
              await fetchSOSStatus();
            } catch (error: any) {
              console.error('取消 SOS 求助失败:', error);
              Toast.show({
                type: 'error',
                text1: '取消失败',
                text2: error.response?.data?.message || error.message || '无法取消 SOS 求助',
                visibilityTime: 3000,
              });
            } finally {
              setCancelling(false);
            }
          }
        }
      ]
    );
  }, [requestId, fetchSOSStatus]);

  // 页面显示时刷新状态
  useFocusEffect(
    useCallback(() => {
      fetchSOSStatus();
    }, [fetchSOSStatus])
  );

  // 定期刷新状态（每 5 秒）
  useEffect(() => {
    const interval = setInterval(() => {
      fetchSOSStatus();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchSOSStatus]);

  // 获取状态显示信息
  const getStatusInfo = () => {
    if (!sosData) return null;

    switch (sosData.status) {
      case 'pending':
        return {
          icon: 'clock',
          color: theme.warning,
          title: '等待救援',
          description: '紧急联系人已收到通知，正在赶往您的位置'
        };
      case 'in_progress':
        return {
          icon: 'truck-medical',
          color: theme.primary,
          title: '救援进行中',
          description: '救援人员已出发，请保持手机畅通'
        };
      case 'completed':
        return {
          icon: 'circle-check',
          color: theme.success,
          title: '救援已完成',
          description: '救援已成功完成'
        };
      case 'cancelled':
        return {
          icon: 'circle-xmark',
          color: theme.error,
          title: '已取消',
          description: '您已取消此 SOS 求助'
        };
      default:
        return null;
    }
  };

  const statusInfo = getStatusInfo();

  if (loading && !sosData) {
    return (
      <Screen backgroundColor={theme.backgroundRoot} statusBarStyle="light">
        <View style={styles.centerContainer}>
          <ActivityIndicator size="small" color={theme.primary} />
          <ThemedText variant="body" style={styles.loadingText}>加载中...</ThemedText>
        </View>
      </Screen>
    );
  }

  return (
    <Screen backgroundColor={theme.backgroundRoot} statusBarStyle="light">
      <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
        <ThemedText variant="small" color={theme.textSecondary} style={styles.pageLead}>
          已持续监控当前求助进展，页面会自动刷新状态
        </ThemedText>
        {/* 状态卡片 */}
        <ThemedView level="root" style={styles.statusCard}>
          {statusInfo && (
            <>
              <View style={[styles.iconContainer, { backgroundColor: statusInfo.color + '20' }]}>
                <FontAwesome6 name={statusInfo.icon} size={48} color={statusInfo.color} />
              </View>
              <ThemedText variant="h2" style={styles.statusTitle} color={statusInfo.color}>
                {statusInfo.title}
              </ThemedText>
              <ThemedText variant="body" style={styles.statusDescription} color={theme.textSecondary}>
                {statusInfo.description}
              </ThemedText>
            </>
          )}
        </ThemedView>

        {/* SOS 详情 */}
        {sosData && (
          <ThemedView level="root" style={styles.detailCard}>
            <ThemedText variant="h4" style={styles.detailTitle}>
              求助详情
            </ThemedText>

            <View style={styles.detailRow}>
              <ThemedText variant="caption" color={theme.textMuted}>
                求助 ID
              </ThemedText>
              <ThemedText variant="body" style={styles.detailValue}>
                {sosData.sos_id}
              </ThemedText>
            </View>

            <View style={styles.detailRow}>
              <ThemedText variant="caption" color={theme.textMuted}>
                发起时间
              </ThemedText>
              <ThemedText variant="body" style={styles.detailValue}>
                {new Date(sosData.created_at).toLocaleString('zh-CN')}
              </ThemedText>
            </View>

            {sosData.address && (
              <View style={styles.detailRow}>
                <ThemedText variant="caption" color={theme.textMuted}>
                  当前位置
                </ThemedText>
                <ThemedText variant="body" style={styles.detailValue}>
                  {sosData.address}
                </ThemedText>
              </View>
            )}

            {sosData.emergency_reason && (
              <View style={styles.detailRow}>
                <ThemedText variant="caption" color={theme.textMuted}>
                  紧急原因
                </ThemedText>
                <ThemedText variant="body" style={styles.detailValue}>
                  {sosData.emergency_reason}
                </ThemedText>
              </View>
            )}

            <View style={styles.detailRow}>
              <ThemedText variant="caption" color={theme.textMuted}>
                已拨打 120
              </ThemedText>
              <ThemedText variant="body" style={styles.detailValue}>
                {sosData.call_120 ? '是' : '否'}
              </ThemedText>
            </View>

            <View style={styles.detailRow}>
              <ThemedText variant="caption" color={theme.textMuted}>
                位置坐标
              </ThemedText>
              <ThemedText variant="body" style={styles.detailValue}>
                {sosData.latitude.toFixed(6)}, {sosData.longitude.toFixed(6)}
              </ThemedText>
            </View>
          </ThemedView>
        )}

        {/* 操作按钮 */}
        {sosData && sosData.status === 'pending' && (
          <TouchableOpacity
            style={[styles.cancelButton, { backgroundColor: theme.error }]}
            onPress={handleCancelSOS}
            disabled={cancelling}
            activeOpacity={0.88}
          >
            <ThemedText variant="body" color={theme.buttonPrimaryText} style={styles.cancelButtonText}>
              {cancelling ? '取消中...' : '取消 SOS 求助'}
            </ThemedText>
          </TouchableOpacity>
        )}

        {/* 返回按钮 */}
        <TouchableOpacity
          style={[styles.backButton, { backgroundColor: theme.backgroundTertiary }]}
          onPress={() => router.back()}
          activeOpacity={0.88}
        >
          <FontAwesome6 name="arrow-left" size={16} color={theme.textPrimary} style={styles.backButtonIcon} />
          <ThemedText variant="body" style={styles.backButtonText}>
            返回首页
          </ThemedText>
        </TouchableOpacity>
      </ScrollView>
    </Screen>
  );
}

const createStyles = (theme: CreateStylesTheme) => StyleSheet.create({
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
  loadingText: {
    marginTop: 10,
  },
  pageLead: {
    textAlign: 'center',
    marginBottom: 12,
  },
  statusCard: {
    alignItems: 'center',
    padding: 32,
    borderRadius: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: theme.borderLight,
  },
  iconContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  statusTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 12,
    textAlign: 'center',
  },
  statusDescription: {
    textAlign: 'center',
    lineHeight: 24,
  },
  detailCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: theme.borderLight,
  },
  detailTitle: {
    marginBottom: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.borderLight,
  },
  detailValue: {
    flex: 1,
    textAlign: 'right',
    marginLeft: 16,
  },
  cancelButton: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  cancelButtonText: {
    fontWeight: '600',
    fontSize: 16,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
  },
  backButtonIcon: {
    marginRight: 8,
  },
  backButtonText: {
    fontWeight: '500',
  },
});
