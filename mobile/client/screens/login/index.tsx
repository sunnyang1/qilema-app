/**
 * 登录页面（增强版）
 * 改进：
 * - 渐变背景 + 品牌视觉
 * - 输入框聚焦动画 + 边框高亮
 * - 密码可见切换
 * - 即时表单验证反馈
 * - 按钮按压缩放动画
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
  Dimensions,
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

const { width } = Dimensions.get('window');

export default function LoginPage() {
  const { theme, isDark } = useTheme();
  const router = useSafeRouter();
  const { login, isLoading } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [usernameFocused, setUsernameFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // 按钮动画
  const { scale: btnScale, pressHandlers } = usePressScale(0.96);


  // Logo 入场动画
  const logoAnim = useRef(new Animated.Value(0)).current;

  // 入场动画
  React.useEffect(() => {
    Animated.spring(logoAnim, {
      toValue: 1,
      tension: 50,
      friction: 7,
      useNativeDriver: true,
    }).start();
  }, []);

  // 表单验证
  const validateUsername = useCallback((val: string) => {
    if (!val.trim()) {
      setUsernameError('用户名不能为空');
      return false;
    }
    setUsernameError('');
    return true;
  }, []);

  const validatePassword = useCallback((val: string) => {
    if (!val) {
      setPasswordError('密码不能为空');
      return false;
    }
    if (val.length < 6) {
      setPasswordError('密码至少 6 位');
      return false;
    }
    setPasswordError('');
    return true;
  }, []);

  const handleLogin = async () => {
    const uValid = validateUsername(username);
    const pValid = validatePassword(password);
    if (!uValid || !pValid) return;

    try {
      await login(username, password);
      Toast.show({ type: 'success', text1: '登录成功', text2: '欢迎回来 👋', visibilityTime: 2200 });
      router.replace('/(tabs)');
    } catch (error: any) {
      Toast.show({ type: 'error', text1: '登录失败', text2: error.message || '用户名或密码错误', visibilityTime: 2600 });
    }
  };

  const s = createStyles(theme, isDark);

  return (
    <Screen backgroundColor={theme.backgroundRoot} statusBarStyle={isDark ? 'light' : 'dark'}>
      <KeyboardAvoidingView
        style={s.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* 顶部渐变装饰 */}
        <LinearGradient
          colors={isDark ? ['#1a1a2e', '#16213e'] : ['#FFF3E0', '#FFFFFF']}
          style={s.gradientBg}
        />

        <View style={s.content}>
          {/* Logo 区域 */}
          <Animated.View
            style={[s.logoArea, {
              opacity: logoAnim,
              transform: [{ translateY: logoAnim.interpolate({ inputRange: [0, 1], outputRange: [-20, 0] }) }],
            }]}
          >
            <View style={[s.logoCircle, { backgroundColor: theme.primary + '20' }]}>
              <ThemedText style={s.logoEmoji}>🏥</ThemedText>
            </View>
            <ThemedText variant="h2" color={theme.textPrimary} style={s.appName}>起了吗</ThemedText>
            <ThemedText variant="body" color={theme.textSecondary} style={s.appDesc}>独居人群紧急医疗服务</ThemedText>
            <View style={s.tagContainer}>
              <View style={[s.tag, { backgroundColor: theme.primary + '15' }]}>
                <FontAwesome6 name="shield-heart" size={10} color={theme.primary} />
                <ThemedText variant="caption" color={theme.primary} style={s.tagText}>安全守护</ThemedText>
              </View>
              <View style={[s.tag, { backgroundColor: theme.accent + '15' }]}>
                <FontAwesome6 name="bell" size={10} color={theme.accent} />
                <ThemedText variant="caption" color={theme.accent} style={s.tagText}>实时提醒</ThemedText>
              </View>
              <View style={[s.tag, { backgroundColor: theme.info + '15' }]}>
                <FontAwesome6 name="phone-volume" size={10} color={theme.info} />
                <ThemedText variant="caption" color={theme.info} style={s.tagText}>一键求助</ThemedText>
              </View>
            </View>
          </Animated.View>

          {/* 表单区域 */}
          <View style={[s.formCard, { backgroundColor: theme.backgroundDefault, borderColor: theme.borderLight }]}>
            {/* 用户名 */}
            <View style={s.inputGroup}>
              <View style={s.labelRow}>
                <FontAwesome6 name="user" size={13} color={theme.textMuted} />
                <ThemedText variant="smallMedium" color={theme.textPrimary} style={s.label}>用户名</ThemedText>
              </View>
              <View style={[
                s.inputWrap,
                { backgroundColor: theme.backgroundTertiary, borderColor: usernameFocused ? theme.primary : (usernameError ? theme.error : theme.border) },
                usernameFocused && s.inputFocused,
              ]}>
                <TextInput
                  style={[s.input, { color: theme.textPrimary }]}
                  placeholder="请输入用户名"
                  placeholderTextColor={theme.textMuted}
                  value={username}
                  onChangeText={(v) => { setUsername(v); if (usernameError) validateUsername(v); }}
                  onFocus={() => setUsernameFocused(true)}
                  onBlur={() => { setUsernameFocused(false); validateUsername(username); }}
                  autoCapitalize="none"
                  autoCorrect={false}
                  returnKeyType="next"
                  accessibilityLabel="用户名输入框"
                />
              </View>
              {usernameError ? (
                <View style={s.errorRow}>
                  <FontAwesome6 name="circle-exclamation" size={11} color={theme.error} />
                  <ThemedText variant="caption" color={theme.error} style={s.errorText}>{usernameError}</ThemedText>
                </View>
              ) : null}
            </View>

            {/* 密码 */}
            <View style={s.inputGroup}>
              <View style={s.labelRow}>
                <FontAwesome6 name="lock" size={13} color={theme.textMuted} />
                <ThemedText variant="smallMedium" color={theme.textPrimary} style={s.label}>密码</ThemedText>
              </View>
              <View style={[
                s.inputWrap,
                { backgroundColor: theme.backgroundTertiary, borderColor: passwordFocused ? theme.primary : (passwordError ? theme.error : theme.border) },
                passwordFocused && s.inputFocused,
              ]}>
                <TextInput
                  style={[s.input, { color: theme.textPrimary, flex: 1 }]}
                  placeholder="请输入密码"
                  placeholderTextColor={theme.textMuted}
                  value={password}
                  onChangeText={(v) => { setPassword(v); if (passwordError) validatePassword(v); }}
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => { setPasswordFocused(false); validatePassword(password); }}
                  secureTextEntry={!passwordVisible}
                  autoCapitalize="none"
                  autoCorrect={false}
                  returnKeyType="done"
                  onSubmitEditing={handleLogin}
                  accessibilityLabel="密码输入框"
                />
                <TouchableOpacity
                  style={s.eyeBtn}
                  onPress={() => setPasswordVisible(!passwordVisible)}
                  activeOpacity={0.7}
                  accessibilityLabel={passwordVisible ? '隐藏密码' : '显示密码'}
                  accessibilityRole="button"
                >
                  <FontAwesome6
                    name={passwordVisible ? 'eye-slash' : 'eye'}
                    size={16}
                    color={theme.textMuted}
                  />
                </TouchableOpacity>
              </View>
              {passwordError ? (
                <View style={s.errorRow}>
                  <FontAwesome6 name="circle-exclamation" size={11} color={theme.error} />
                  <ThemedText variant="caption" color={theme.error} style={s.errorText}>{passwordError}</ThemedText>
                </View>
              ) : null}
            </View>

            {/* 登录按钮 */}
            <Animated.View style={{ transform: [{ scale: btnScale }] }}>
              <TouchableOpacity
                style={[s.loginBtn, { opacity: isLoading ? 0.85 : 1 }]}
                onPress={handleLogin}
                onPressIn={pressHandlers.onPressIn}
                onPressOut={pressHandlers.onPressOut}
                disabled={isLoading}
                activeOpacity={1}
                accessibilityRole="button"
                accessibilityLabel="登录"
              >
                <LinearGradient
                  colors={[theme.primary, theme.primaryDark]}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={s.loginBtnGradient}
                >
                  {isLoading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <>
                      <FontAwesome6 name="right-to-bracket" size={16} color="#fff" />
                      <ThemedText variant="bodyMedium" color="#fff" style={s.loginBtnText}>登录</ThemedText>
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          </View>

          {/* 底部注册入口 */}
          <View style={s.footer}>
            <ThemedText variant="small" color={theme.textSecondary}>还没有账号？</ThemedText>
            <TouchableOpacity onPress={() => router.push('/register')} activeOpacity={0.75}>
              <ThemedText variant="smallMedium" color={theme.primary} style={s.registerLink}>立即注册</ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const createStyles = (theme: CreateStylesTheme, isDark: boolean) => StyleSheet.create({
  container: { flex: 1 },
  gradientBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '45%',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  logoArea: {
    alignItems: 'center',
    marginBottom: 28,
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  logoEmoji: {
    fontSize: 40,
  },
  appName: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 6,
  },
  appDesc: {
    fontSize: 14,
    marginBottom: 14,
  },
  tagContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 100,
  },
  tagText: {
    fontSize: 11,
  },
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
  inputGroup: {
    marginBottom: 16,
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  label: {
    fontSize: 13,
  },
  inputWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1.5,
    paddingHorizontal: 14,
    height: 50,
    overflow: 'hidden',
  },
  inputFocused: {
    shadowColor: theme.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 2,
  },
  input: {
    flex: 1,
    fontSize: 15,
    paddingVertical: 0,
  },
  eyeBtn: {
    padding: 6,
    marginLeft: 4,
  },
  errorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 5,
    paddingLeft: 2,
  },
  errorText: {
    fontSize: 12,
  },
  loginBtn: {
    borderRadius: 12,
    overflow: 'hidden',
    marginTop: 6,
  },
  loginBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 52,
    gap: 10,
  },
  loginBtnText: {
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
    gap: 4,
  },
  registerLink: {
    fontSize: 14,
    fontWeight: '600',
  },
});
