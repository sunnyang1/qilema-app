/**
 * 主题提供者 - ThemeProvider
 * 统一管理主题状态（跟随系统 / 固定浅色 / 固定深色）
 */
import React, {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  Appearance,
  ColorSchemeName,
  Platform,
  AccessibilityInfo,
} from 'react-native';
import { Theme, ThemePreference, ColorScheme } from './types';
import { warmLight, warmDark } from './themes';

// ============================================================================
// 主题配置
// ============================================================================

interface ThemeContextValue {
  /** 当前主题对象 */
  theme: Theme;
  /** 当前颜色模式 */
  colorScheme: ColorScheme;
  /** 是否深色模式 */
  isDark: boolean;
  /** 用户主题偏好设置 */
  preference: ThemePreference;
  /** 设置主题偏好 */
  setPreference: (preference: ThemePreference) => void;
  /** 切换浅色/深色 */
  toggleColorScheme: () => void;
  /** 是否启用减少动画 */
  reduceMotion: boolean;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

// ============================================================================
// Props
// ============================================================================

interface ThemeProviderProps {
  children: ReactNode;
  /** 默认主题偏好 */
  defaultPreference?: ThemePreference;
}

// ============================================================================
// Provider
// ============================================================================

export function ThemeProvider({
  children,
  defaultPreference = 'system',
}: ThemeProviderProps) {
  const [preference, setPreferenceState] = useState<ThemePreference>(defaultPreference);
  const [systemColorScheme, setSystemColorScheme] = useState<ColorSchemeName>(
    Appearance.getColorScheme()
  );
  const [reduceMotion, setReduceMotion] = useState(false);

  // 监听系统颜色模式变化
  useEffect(() => {
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      setSystemColorScheme(colorScheme);
    });
    return () => subscription.remove();
  }, []);

  // 监听减少动画设置（无障碍）
  useEffect(() => {
    let isMounted = true;
    AccessibilityInfo.isReduceMotionEnabled().then((enabled) => {
      if (isMounted) setReduceMotion(enabled);
    });

    const subscription = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      (enabled) => {
        setReduceMotion(enabled);
      }
    );

    return () => {
      isMounted = false;
      subscription.remove();
    };
  }, []);

  // 处理 Web 端 Coze Workbench 颜色方案消息
  useEffect(() => {
    if (Platform.OS !== 'web') return;

    function handleMessage(e: MessageEvent<{ event: string; colorScheme: ColorSchemeName } | undefined>) {
      if (e.data?.event === 'coze.workbench.colorScheme') {
        const cs = e.data.colorScheme;
        if (cs === 'light' || cs === 'dark') {
          setSystemColorScheme(cs);
        }
      }
    }

    window.addEventListener('message', handleMessage, false);
    return () => window.removeEventListener('message', handleMessage, false);
  }, []);

  // 计算当前有效的颜色模式
  const colorScheme: ColorScheme = useMemo(() => {
    if (preference === 'system') {
      return systemColorScheme === 'dark' ? 'dark' : 'light';
    }
    return preference;
  }, [preference, systemColorScheme]);

  const isDark = colorScheme === 'dark';

  // 当前主题
  const theme = useMemo(() => (isDark ? warmDark : warmLight), [isDark]);

  // 设置偏好
  const setPreference = useCallback((newPreference: ThemePreference) => {
    setPreferenceState(newPreference);
  }, []);

  // 切换颜色模式
  const toggleColorScheme = useCallback(() => {
    setPreferenceState((prev) => {
      if (prev === 'system') {
        return systemColorScheme === 'dark' ? 'light' : 'dark';
      }
      return prev === 'dark' ? 'light' : 'dark';
    });
  }, [systemColorScheme]);

  const value = useMemo(
    () => ({
      theme,
      colorScheme,
      isDark,
      preference,
      setPreference,
      toggleColorScheme,
      reduceMotion,
    }),
    [theme, colorScheme, isDark, preference, setPreference, toggleColorScheme, reduceMotion]
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useThemeContext(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
}
