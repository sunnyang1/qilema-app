import { Colors as WarmColors } from '@/constants/theme-warm';
import { useColorScheme } from '@/hooks/useColorScheme';

enum COLOR_SCHEME_CHOICE {
  FOLLOW_SYSTEM = 'follow-system', // 跟随系统自动变化
  DARK = 'dark', // 固定为 dark 主题，不随系统变化
  LIGHT = 'light', // 固定为 light 主题，不随系统变化
};

const userPreferColorScheme: COLOR_SCHEME_CHOICE = COLOR_SCHEME_CHOICE.FOLLOW_SYSTEM;

// 温暖守护主题配置（浅色模式 + 深色模式）
const WarmTheme = {
  light: {
    ...WarmColors,
    buttonPrimaryText: '#FFFFFF',
    tabIconSelected: WarmColors.primary,
  },
  dark: {
    primary: '#FFAB91',        // 深色模式更亮的晨光橙
    primaryLight: '#FFCCBC',
    primaryDark: '#FF8A65',
    accent: '#81C784',         // 深色模式更亮的生命绿
    accentLight: '#A5D6A7',
    accentDark: '#66BB6A',
    success: '#66BB6A',
    warning: '#FFB74D',
    error: '#EF5350',
    info: '#64B5F6',
    textPrimary: '#ECEFF1',    // 深色模式主文本
    textSecondary: '#B0BEC5',
    textMuted: '#78909C',
    disabled: '#90A4AE',
    backgroundRoot: '#121212',
    backgroundDefault: '#1E1E1E',
    backgroundTertiary: '#2C2C2C',
    backgroundCard: '#263238',
    border: '#424242',
    borderLight: '#303030',
    borderDark: '#546E7A',
    shadow: 'rgba(255, 171, 145, 0.25)',
    shadowLight: 'rgba(255, 171, 145, 0.12)',
    shadowStrong: 'rgba(255, 171, 145, 0.35)',
    touchRipple: 'rgba(255, 255, 255, 0.2)',
    touchRippleDark: 'rgba(0, 0, 0, 0.15)',
    touchOverlay: 'rgba(0, 0, 0, 0.08)',
    touchOverlayDark: 'rgba(0, 0, 0, 0.12)',
    buttonPrimaryText: '#FFFFFF',
    tabIconSelected: '#FFAB91',
  },
};

function getTheme(colorScheme?: 'dark' | 'light' | null) {
  const isDark = colorScheme === 'dark';
  const theme = WarmTheme[colorScheme ?? 'light'];

  return {
    theme,
    isDark,
  };
}

function useTheme() {
  const systemColorScheme = useColorScheme()
  const colorScheme = userPreferColorScheme === COLOR_SCHEME_CHOICE.FOLLOW_SYSTEM ?
    systemColorScheme :
    userPreferColorScheme;

  return getTheme(colorScheme);
}

export {
  useTheme,
}
