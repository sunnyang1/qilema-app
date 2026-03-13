import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
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
    marginBottom: 48,
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
      Toast.show({ type: 'error', text1: '提示', text2: '请填写完整信息' });
      return;
    }

    if (password !== confirmPassword) {
      Toast.show({ type: 'error', text1: '提示', text2: '两次输入的密码不一致' });
      return;
    }

    try {
      await register(username, password);
      Toast.show({ type: 'success', text1: '成功', text2: '注册成功' });
      router.replace('/(tabs)');
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '注册失败', text2: error.message });
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
          </View>

          <View style={styles(theme).form}>
            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                用户名
              </ThemedText>
              <TextInput
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary }]}
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
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary }]}
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
                style={[styles(theme).input, { backgroundColor: theme.backgroundTertiary, color: theme.textPrimary }]}
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
            >
              <ThemedText variant="bodyMedium" color={theme.buttonPrimaryText} style={styles(theme).buttonText}>
                {isLoading ? '注册中...' : '注册'}
              </ThemedText>
            </TouchableOpacity>
          </View>

          <View style={styles(theme).footer}>
            <TouchableOpacity onPress={() => router.back()}>
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
