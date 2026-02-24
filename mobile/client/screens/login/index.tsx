import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/contexts/AuthContext';
import Toast from 'react-native-toast-message';

const styles = (theme: any) => StyleSheet.create({
  container: {
    flex: 1,
  },
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
  logo: {
    fontSize: 64,
    marginBottom: 16,
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
  form: {
    width: '100%',
  },
  inputContainer: {
    marginBottom: 16,
  },
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
  footerText: {
    fontSize: 14,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '600',
  },
});

export default function LoginPage() {
  const { theme, isDark } = useTheme();
  const router = useSafeRouter();
  const { login, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!username || !password) {
      Toast.show({
        type: 'error',
        text1: '提示',
        text2: '请输入用户名和密码',
      });
      return;
    }

    try {
      await login(username, password);
      Toast.show({
        type: 'success',
        text1: '成功',
        text2: '登录成功',
      });
      router.replace('/(tabs)');
    } catch (error: any) {
      Toast.show({
        type: 'error',
        text1: '登录失败',
        text2: error.message || '用户名或密码错误',
      });
    }
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <KeyboardAvoidingView
        style={styles(theme).container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles(theme).content}>
          {/* Header */}
          <View style={styles(theme).header}>
            <Text style={[styles(theme).logo, { color: theme.primary }]}>🏥</Text>
            <ThemedText variant="h2" color={theme.textPrimary} style={styles(theme).title}>
              起了吗
            </ThemedText>
            <ThemedText variant="body" color={theme.textSecondary}>
              独居人群紧急医疗服务
            </ThemedText>
          </View>

          {/* Form */}
          <View style={styles(theme).form}>
            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                用户名
              </ThemedText>
              <TextInput
                style={[
                  styles(theme).input,
                  {
                    backgroundColor: theme.backgroundTertiary,
                    color: theme.textPrimary,
                  },
                ]}
                placeholder="请输入用户名"
                placeholderTextColor={theme.textMuted}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <View style={styles(theme).inputContainer}>
              <ThemedText variant="smallMedium" color={theme.textPrimary} style={styles(theme).inputLabel}>
                密码
              </ThemedText>
              <TextInput
                style={[
                  styles(theme).input,
                  {
                    backgroundColor: theme.backgroundTertiary,
                    color: theme.textPrimary,
                  },
                ]}
                placeholder="请输入密码"
                placeholderTextColor={theme.textMuted}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            <TouchableOpacity
              style={[styles(theme).button, { backgroundColor: theme.primary }]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <ThemedText
                variant="bodyMedium"
                color={theme.buttonPrimaryText}
                style={styles(theme).buttonText}
              >
                {isLoading ? '登录中...' : '登录'}
              </ThemedText>
            </TouchableOpacity>
          </View>

          {/* Footer */}
          <View style={styles(theme).footer}>
            <ThemedText variant="small" color={theme.textSecondary}>
              还没有账号？{' '}
            </ThemedText>
            <TouchableOpacity onPress={() => router.push('/register')}>
              <ThemedText variant="smallMedium" color={theme.primary}>
                立即注册
              </ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}
