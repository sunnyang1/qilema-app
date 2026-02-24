export const Colors = {
  light: {
    textPrimary: "#212121", // Flutter: textPrimary
    textSecondary: "#757575", // Flutter: textSecondary
    textMuted: "#BDBDBD", // Flutter: textDisabled
    primary: "#2196F3", // Flutter: primary (蓝色)
    primaryDark: "#1976D2", // Flutter: primaryDark
    primaryLight: "#BBDEFB", // Flutter: primaryLight
    accent: "#FF9800", // 橙色（警告色）
    success: "#4CAF50", // 绿色（成功）
    error: "#F44336", // 红色（错误）
    info: "#2196F3", // 蓝色（信息）
    warning: "#FF9800", // 橙色（警告）
    backgroundRoot: "#F5F5F5", // Flutter: background
    backgroundDefault: "#FFFFFF", // Flutter: surface
    backgroundTertiary: "#F5F5F5", // 输入框背景
    buttonPrimaryText: "#FFFFFF",
    tabIconSelected: "#2196F3",
    border: "#E0E0E0", // Flutter: divider
    borderLight: "#E5E7EB",
  },
  dark: {
    textPrimary: "#FFFFFF",
    textSecondary: "#B0BEC5",
    textMuted: "#757575",
    primary: "#64B5F6", // 暗色模式更亮的蓝色
    primaryDark: "#42A5F5",
    primaryLight: "#90CAF9",
    accent: "#FFB74D",
    success: "#66BB6A",
    error: "#EF5350",
    info: "#64B5F6",
    warning: "#FFB74D",
    backgroundRoot: "#121212", // 暗色模式背景
    backgroundDefault: "#1E1E1E", // 暗色模式卡片背景
    backgroundTertiary: "#2C2C2C",
    buttonPrimaryText: "#FFFFFF",
    tabIconSelected: "#64B5F6",
    border: "#424242",
    borderLight: "#303030",
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  "2xl": 24,
  "3xl": 32,
  "4xl": 40,
  "5xl": 48,
  "6xl": 64,
};

export const BorderRadius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  "2xl": 24,
  "3xl": 28,
  "4xl": 32,
  full: 9999,
};

export const Typography = {
  display: {
    fontSize: 112,
    lineHeight: 112,
    fontWeight: "200" as const,
    letterSpacing: -4,
  },
  displayLarge: {
    fontSize: 112,
    lineHeight: 112,
    fontWeight: "200" as const,
    letterSpacing: -2,
  },
  displayMedium: {
    fontSize: 48,
    lineHeight: 56,
    fontWeight: "200" as const,
  },
  h1: {
    fontSize: 32,
    lineHeight: 40,
    fontWeight: "700" as const,
  },
  h2: {
    fontSize: 28,
    lineHeight: 36,
    fontWeight: "700" as const,
  },
  h3: {
    fontSize: 24,
    lineHeight: 32,
    fontWeight: "300" as const,
  },
  h4: {
    fontSize: 20,
    lineHeight: 28,
    fontWeight: "600" as const,
  },
  title: {
    fontSize: 18,
    lineHeight: 24,
    fontWeight: "700" as const,
  },
  body: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "400" as const,
  },
  bodyMedium: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "500" as const,
  },
  small: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "400" as const,
  },
  smallMedium: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "500" as const,
  },
  caption: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "400" as const,
  },
  captionMedium: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "500" as const,
  },
  label: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "500" as const,
    letterSpacing: 2,
    textTransform: "uppercase" as const,
  },
  labelSmall: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "500" as const,
    letterSpacing: 1,
    textTransform: "uppercase" as const,
  },
  labelTitle: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "700" as const,
    letterSpacing: 2,
    textTransform: "uppercase" as const,
  },
  link: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "400" as const,
  },
  stat: {
    fontSize: 30,
    lineHeight: 36,
    fontWeight: "300" as const,
  },
  tiny: {
    fontSize: 10,
    lineHeight: 14,
    fontWeight: "400" as const,
  },
  navLabel: {
    fontSize: 10,
    lineHeight: 14,
    fontWeight: "500" as const,
  },
};

export type Theme = typeof Colors.light;
