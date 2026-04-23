/**
 * 注册页面（增强版）
 * 改进：
 * - 密码强度可视化进度条
 * - 密码可见切换
 * - 即时表单校验
 * - 渐变确认按钮
 */
import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import { useSafeRouter } from '@/hooks/useSafeRouter';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import { usePressScale } from '@/hooks/usePressScale';
import { useAuth } from '@/contexts/AuthContext';
import Toast from 'react-native-toast-message';

// 密码强度计算
function getPasswordStrength(pw: string): { level: number; label: string; color: string } {
  if (!pw) return { level: 0, label: '', color: '#E0E0E0' };
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  if (score <= 1) return { level: 1, label: '弱', color: '#EF5350' };
  if (score <= 3) return { level: 2, label: '中', color: '#FFB74D' };
  return { level: 3, label: '强', color: '#66BB6A' };
}

export default function RegisterPage() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { register, isLoading } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwVisible, setPwVisible] = useState(false);
  const [confirmPwVisible, setConfirmPwVisible] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { scale: btnScale, pressHandlers } = usePressScale(0.96);
  const pwStrength = getPasswordStrength(password);

  const validate = useCallback(() => {
    const newErrors: Record<string, string> = {};
    if (!username.trim()) newErrors.username = '用户名不能为空';
    else if (username.length < 2) newErrors.username = '用户名至少 2 个字符';
    if (!password) newErrors.password = '密码不能为空';
    else if (password.length < 6) newErrors.password = '密码至少 6 位';
    if (!confirmPassword) newErrors.confirmPassword = '请再次输入密码';
    else if (password !== confirmPassword) newErrors.confirmPassword = '两次密码不一致';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [username, password, confirmPassword]);

  const handleRegister = async () => {
    if (!validate()) return;
    try {
      await register(username, password);
      Toast.show({ type: 'success', text1: '注册成功 🎉', text2: '欢迎加入起了吗', visibilityTime: 2200 });
      router.replace('/(tabs)');
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '注册失败', text2: error.message || '请稍后重试', visibilityTime: 2600 });
    }
  };

  const inputBorderColor = (field: string) =>
    errors[field] ? theme.error : focusedField === field ? theme.primary : theme.border;

  const s = createStyles(theme);

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <KeyboardAvoidingView style={s.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={s.content}>
          {/* 头部 */}
          <View style={s.header}>
            <View style={[s.logoCircle, { backgroundColor: theme.primary + '18' }]}>
              <ThemedText style={{ fontSize: 36 }}>🏥</ThemedText>
            </View>
            <ThemedText variant="h2" color={theme.textPrimary} style={s.title}>创建账号</ThemedText>
            <ThemedText variant="body" color={theme.textSecondary} style={s.subtitle}>注册后即可使用守护功能</ThemedText>
          </View>

          {/* 表单 */}
          <View style={[s.formCard, { backgroundColor: theme.backgroundDefault, borderColor: theme.borderLight }]}>

            {/* 用户名 */}
            <View style={s.inputGroup}>
              <View style={s.labelRow}>
                <FontAwesome6 name="user" size={12} color={theme.textMuted} />
                <ThemedText variant="smallMedium" color={theme.textPrimary} style={s.label}>用户名</ThemedText>
              </View>
              <View style={[s.inputWrap, { backgroundColor: theme.backgroundTertiary, borderColor: inputBorderColor('username') }]}>
                <TextInput
                  style={[s.input, { color: theme.textPrimary }]}
                  placeholder="2-20 个字符"
                  placeholderTextColor={theme.textMuted}
                  value={username}
                  onChangeText={(v) => { setUsername(v); setErrors(prev => ({ ...prev, username: '' })); }}
                  onFocus={() => setFocusedField('username')}
                  onBlur={() => setFocusedField(null)}
                  autoCapitalize="none"
                  returnKeyType="next"
                />
              </View>
              {errors.username ? <ErrorHint message={errors.username} color={theme.error} /> : null}
            </View>

            {/* 密码 */}
            <View style={s.inputGroup}>
              <View style={s.labelRow}>
                <FontAwesome6 name="lock" size={12} color={theme.textMuted} />
                <ThemedText variant="smallMedium" color={theme.textPrimary} style={s.label}>密码</ThemedText>
                {password.length > 0 && (
                  <View style={[s.strengthBadge, { backgroundColor: pwStrength.color + '20' }]}>
                    <ThemedText variant="caption" color={pwStrength.color} style={s.strengthText}>
                      {pwStrength.label}
                    </ThemedText>
                  </View>
                )}
              </View>
              <View style={[s.inputWrap, { backgroundColor: theme.backgroundTertiary, borderColor: inputBorderColor('password') }]}>
                <TextInput
                  style={[s.input, { color: theme.textPrimary, flex: 1 }]}
                  placeholder="至少 6 位"
                  placeholderTextColor={theme.textMuted}
                  value={password}
                  onChangeText={(v) => { setPassword(v); setErrors(prev => ({ ...prev, password: '' })); }}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                  secureTextEntry={!pwVisible}
                  autoCapitalize="none"
                  returnKeyType="next"
                />
                <TouchableOpacity onPress={() => setPwVisible(!pwVisible)} style={s.eyeBtn} activeOpacity={0.7}>
                  <FontAwesome6 name={pwVisible ? 'eye-slash' : 'eye'} size={15} color={theme.textMuted} />
                </TouchableOpacity>
              </View>
              {/* 密码强度条 */}
              {password.length > 0 && (
                <View style={s.strengthBar}>
                  {[1, 2, 3].map((i) => (
                    <View
                      key={i}
                      style={[
                        s.strengthSegment,
                        { backgroundColor: i <= pwStrength.level ? pwStrength.color : theme.borderLight }
                      ]}
                    />
                  ))}
                </View>
              )}
              {errors.password ? <ErrorHint message={errors.password} color={theme.error} /> : null}
            </View>

            {/* 确认密码 */}
            <View style={s.inputGroup}>
              <View style={s.labelRow}>
                <FontAwesome6 name="lock" size={12} color={theme.textMuted} />
                <ThemedText variant="smallMedium" color={theme.textPrimary} style={s.label}>确认密码</ThemedText>
                {confirmPassword.length > 0 && password === confirmPassword && (
                  <FontAwesome6 name="circle-check" size={13} color={theme.accent} />
                )}
              </View>
              <View style={[s.inputWrap, { backgroundColor: theme.backgroundTertiary, borderColor: inputBorderColor('confirmPassword') }]}>
                <TextInput
                  style={[s.input, { color: theme.textPrimary, flex: 1 }]}
                  placeholder="再次输入密码"
                  placeholderTextColor={theme.textMuted}
                  value={confirmPassword}
                  onChangeText={(v) => { setConfirmPassword(v); setErrors(prev => ({ ...prev, confirmPassword: '' })); }}
                  onFocus={() => setFocusedField('confirm')}
                  onBlur={() => setFocusedField(null)}
                  secureTextEntry={!confirmPwVisible}
                  autoCapitalize="none"
                  returnKeyType="done"
                  onSubmitEditing={handleRegister}
                />
                <TouchableOpacity onPress={() => setConfirmPwVisible(!confirmPwVisible)} style={s.eyeBtn} activeOpacity={0.7}>
                  <FontAwesome6 name={confirmPwVisible ? 'eye-slash' : 'eye'} size={15} color={theme.textMuted} />
                </TouchableOpacity>
              </View>
              {errors.confirmPassword ? <ErrorHint message={errors.confirmPassword} color={theme.error} /> : null}
            </View>

            {/* 注册按钮 */}
            <Animated.View style={{ transform: [{ scale: btnScale }] }}>
              <TouchableOpacity
                style={s.registerBtn}
                onPress={handleRegister}
                onPressIn={pressHandlers.onPressIn}
                onPressOut={pressHandlers.onPressOut}
                disabled={isLoading}
                activeOpacity={1}
                accessibilityRole="button"
                accessibilityLabel="注册账号"
              >
                <LinearGradient
                  colors={[theme.primary, theme.primaryDark]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={s.registerBtnGradient}
                >
                  {isLoading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <>
                      <FontAwesome6 name="user-plus" size={16} color="#fff" />
                      <ThemedText variant="bodyMedium" color="#fff" style={s.registerBtnText}>注册</ThemedText>
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          </View>

          {/* 返回登录 */}
          <View style={s.footer}>
            <ThemedText variant="small" color={theme.textSecondary}>已有账号？</ThemedText>
            <TouchableOpacity onPress={() => router.back()} activeOpacity={0.75}>
              <ThemedText variant="smallMedium" color={theme.primary} style={s.loginLink}>返回登录</ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

function ErrorHint({ message, color }: { message: string; color: string }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 5, paddingLeft: 2 }}>
      <FontAwesome6 name="circle-exclamation" size={11} color={color} />
      <ThemedText variant="caption" color={color} style={{ fontSize: 12 }}>{message}</ThemedText>
    </View>
  );
}

const createStyles = (theme: CreateStylesTheme) => StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1, justifyContent: 'center', paddingHorizontal: 24, paddingBottom: 40 },
  header: { alignItems: 'center', marginBottom: 24 },
  logoCircle: { width: 70, height: 70, borderRadius: 35, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  title: { fontSize: 26, fontWeight: '700', marginBottom: 6 },
  subtitle: { fontSize: 14 },
  formCard: {
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 4,
  },
  inputGroup: { marginBottom: 14 },
  labelRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 },
  label: { fontSize: 13, flex: 1 },
  strengthBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 100 },
  strengthText: { fontSize: 11, fontWeight: '600' },
  inputWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1.5,
    paddingHorizontal: 14,
    height: 50,
  },
  input: { flex: 1, fontSize: 15, paddingVertical: 0 },
  eyeBtn: { padding: 6, marginLeft: 4 },
  strengthBar: { flexDirection: 'row', gap: 4, marginTop: 6 },
  strengthSegment: { flex: 1, height: 3, borderRadius: 2 },
  registerBtn: { borderRadius: 12, overflow: 'hidden', marginTop: 6 },
  registerBtnGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', height: 52, gap: 10 },
  registerBtnText: { fontSize: 16, fontWeight: '600' },
  footer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 18, gap: 4 },
  loginLink: { fontSize: 14, fontWeight: '600' },
});
