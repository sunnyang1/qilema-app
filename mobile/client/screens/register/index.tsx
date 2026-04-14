import React, { useState } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/contexts/AuthContext';
import Toast from 'react-native-toast-message';

const styles = (theme: any) => StyleSheet.create({
  container: { flex: 1 },
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingBottom: 48,
  },
  header: {
    alignItems: 'center',
    marginBottom: 28,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  helperText: {
    fontSize: 13,
    textAlign: 'center',
    marginTop: 8,
  },
  formCard: {
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
  },
  form: { width: '100%' },
  inputContainer: { marginBottom: 16 },
  inputLabel: {
    fontSize: 14,
    marginBottom: 8,
  },
  input: {
    height: 48,
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
    borderWidth: 1,
  },
  button: {
    height: 48,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    alignItems: 'center',
    marginTop: 24,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '600',
  },
});

export default function RegisterPage() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { register, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegister = async () => {
    if (!username || !password || !confirmPassword) {
      Toast.show({ type: 'error', text1: '注册失败', text2: '请填写完整信息', visibilityTime: 2600 });
      return;
    }

    if (password !== confirmPassword) {
      Toast.show({ type: 'error', text1: '注册失败', text2: '两次输入的密码不一致', visibilityTime: 2600 });
      return;
    }

    try {
      await register(username, password);
      Toast.show({ type: 'success', text1: '注册成功', text2: '欢迎使用起了吗', visibilityTime: 2200 });
      router.replace('/(tabs)');
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '注册失败', text2: error.message || '请稍后重试', visibilityTime: 2600 });
    }
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <KeyboardAvoidingView
        style={styles(theme).container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles(theme).content}>
          <View style={styles(theme).header}>
            <ThemedText variant="h2" color={theme.textPrimary} style={styles(theme).title}>
              创建账号
            </ThemedText>
            <ThemedText variant="body" color={theme.textSecondary}>
              注册成为起了吗用户
            </ThemedText>
            <ThemedText variant="small" color={theme.textMuted} style={styles(theme).helperText}>
              创建账号后可立即使用联系人与健康守护功能
            </ThemedText>
          </View>

          <View
            style={[
              styles(theme).form,
              styles(theme).formCard,
              { backgroundColor: theme.backgroundDefault, borderColor: theme.borderLight },
            ]}
          >
            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                用户名
              </ThemedText>
              <TextInput
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary, borderColor: theme.border }]}
                placeholder="请输入用户名"
                placeholderTextColor={theme.textMuted}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
              />
            </View>

            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                密码
              </ThemedText>
              <TextInput
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary, borderColor: theme.border }]}
                placeholder="请输入密码"
                placeholderTextColor={theme.textMuted}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
              />
            </View>

            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                确认密码
              </ThemedText>
              <TextInput
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary, borderColor: theme.border }]}
                placeholder="请再次输入密码"
                placeholderTextColor={theme.textMuted}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry
                autoCapitalize="none"
              />
            </View>

            <TouchableOpacity
              style={[styles(theme).button, { backgroundColor: theme.primary }]}
              onPress={handleRegister}
              disabled={isLoading}
              activeOpacity={0.88}
            >
              {isLoading ? (
                <ActivityIndicator color={theme.buttonPrimaryText} />
              ) : (
                <ThemedText variant="bodyMedium" color={theme.buttonPrimaryText} style={styles(theme).buttonText}>
                  注册
                </ThemedText>
              )}
            </TouchableOpacity>
          </View>

          <View style={styles(theme).footer}>
            <TouchableOpacity onPress={() => router.back()} activeOpacity={0.75}>
              <ThemedText variant="smallMedium" color={theme.primary} style={styles(theme).linkText}>
                返回登录
              </ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}
