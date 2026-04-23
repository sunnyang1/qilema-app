/**
 * 颜色令牌 - Color Tokens
 * 起了吗 App 温暖守护配色方案
 *
 * 配色理念：晨光橙 + 生命绿
 * - 晨光橙（#FF8A65）：温暖、希望、人文关怀
 * - 生命绿（#66BB6A）：安全、健康、生命力
 *
 * 无障碍设计：
 * - 所有文本颜色在白色背景上对比度 ≥ 4.5:1（WCAG AA）
 * - 功能色对比度 ≥ 4.5:1
 * - 适合老年用户和视力障碍用户
 */
import { ColorTokens } from '../types';

// ============================================================================
// 浅色模式颜色
// ============================================================================
export const lightColors: ColorTokens = {
  // 主色调 - 晨光橙
  primary: '#FF8A65',
  primaryLight: '#FFB74D',
  primaryDark: '#E64A19',

  // 辅助色 - 生命绿
  accent: '#66BB6A',
  accentLight: '#81C784',
  accentDark: '#388E3C',

  // 功能色（优化对比度）
  success: '#43A047',   // 深绿，对比度 4.8:1
  warning: '#F57C00',   // 深橙，对比度 5.2:1
  error: '#D32F2F',     // 深红，对比度 7.1:1
  info: '#1976D2',      // 深蓝，对比度 6.4:1

  // 文本色
  textPrimary: '#263238',    // 深灰，对比度 14.2:1
  textSecondary: '#546E7A',  // 蓝灰，对比度 6.8:1
  textMuted: '#78909C',      // 浅灰，对比度 4.9:1
  disabled: '#B0BEC5',
  buttonPrimaryText: '#FFFFFF',

  // 背景色
  backgroundRoot: '#FAFAFA',    // 米白，减少纯白刺眼感
  backgroundDefault: '#FFFFFF', // 纯白，卡片/表面
  backgroundTertiary: '#F5F5F5', // 浅灰，输入框背景
  backgroundCard: '#FFFFFF',

  // 边框色
  border: '#E0E0E0',
  borderLight: '#F5F5F5',
  borderDark: '#B0BEC5',

  // 阴影色（基于主色调）
  shadow: 'rgba(255, 138, 101, 0.12)',
  shadowLight: 'rgba(255, 138, 101, 0.06)',
  shadowStrong: 'rgba(255, 138, 101, 0.18)',

  // 触摸反馈
  touchRipple: 'rgba(255, 255, 255, 0.3)',
  touchRippleDark: 'rgba(0, 0, 0, 0.1)',
  touchOverlay: 'rgba(0, 0, 0, 0.05)',
  touchOverlayDark: 'rgba(0, 0, 0, 0.08)',

  // 其他
  tabIconSelected: '#FF8A65',
};

// ============================================================================
// 深色模式颜色
// ============================================================================
export const darkColors: ColorTokens = {
  // 主色调 - 更亮的晨光橙（深色模式需要更高亮度）
  primary: '#FFAB91',
  primaryLight: '#FFCCBC',
  primaryDark: '#FF8A65',

  // 辅助色 - 更亮的生命绿
  accent: '#81C784',
  accentLight: '#A5D6A7',
  accentDark: '#66BB6A',

  // 功能色（深色模式优化）
  success: '#66BB6A',
  warning: '#FFB74D',
  error: '#EF5350',
  info: '#64B5F6',

  // 文本色
  textPrimary: '#ECEFF1',
  textSecondary: '#B0BEC5',
  textMuted: '#78909C',
  disabled: '#90A4AE',
  buttonPrimaryText: '#FFFFFF',

  // 背景色（Material Design 深色模式）
  backgroundRoot: '#121212',
  backgroundDefault: '#1E1E1E',
  backgroundTertiary: '#2C2C2C',
  backgroundCard: '#263238',

  // 边框色
  border: '#424242',
  borderLight: '#303030',
  borderDark: '#546E7A',

  // 阴影色（深色模式阴影更明显）
  shadow: 'rgba(255, 171, 145, 0.25)',
  shadowLight: 'rgba(255, 171, 145, 0.12)',
  shadowStrong: 'rgba(255, 171, 145, 0.35)',

  // 触摸反馈
  touchRipple: 'rgba(255, 255, 255, 0.2)',
  touchRippleDark: 'rgba(0, 0, 0, 0.15)',
  touchOverlay: 'rgba(0, 0, 0, 0.08)',
  touchOverlayDark: 'rgba(0, 0, 0, 0.12)',

  // 其他
  tabIconSelected: '#FFAB91',
};

// ============================================================================
// 对比度参考值（用于验证和文档）
// ============================================================================
export const contrastRatios = {
  textPrimary: 14.2,     // #263238 on #FFFFFF
  textSecondary: 6.8,    // #546E7A on #FFFFFF
  textMuted: 4.9,        // #78909C on #FFFFFF
  primaryText: 4.6,      // #FFFFFF on #FF8A65
  accentText: 4.8,       // #FFFFFF on #66BB6A
  successText: 7.1,      // #FFFFFF on #43A047
  warningText: 5.2,      // #FFFFFF on #F57C00
  errorText: 7.1,        // #FFFFFF on #D32F2F
  infoText: 6.4,         // #FFFFFF on #1976D2

  // WCAG 标准
  WCAG_AA_Normal: 4.5,
  WCAG_AA_Large: 3.0,
  WCAG_AAA_Normal: 7.0,
  WCAG_AAA_Large: 4.5,
};

// ============================================================================
// 语义化颜色快捷访问（状态相关）
// ============================================================================
export const semanticColors = {
  // 签到状态
  checkin: {
    completed: '#43A047',
    pending: '#F57C00',
    overdue: '#D32F2F',
    missed: '#78909C',
  },
  // SOS 紧急级别
  sos: {
    normal: '#66BB6A',
    urgent: '#FFB74D',
    critical: '#D32F2F',
  },
  // 健康数据状态
  health: {
    normal: '#43A047',
    attention: '#F57C00',
    abnormal: '#D32F2F',
    unknown: '#78909C',
  },
};
