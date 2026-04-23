/**
 * 排版令牌 - Typography Tokens
 * 基于 Material Design 3 排版尺度，针对老年用户优化行高和字重
 *
 * 设计原则：
 * - 最小字重 400，避免细体导致可读性下降
 * - 行高 ≥ 1.5 倍字号，提升阅读舒适度
 * - 标题使用负字间距，正文使用默认字间距
 */
import { TypographyScale } from '../types';

export const typography: TypographyScale = {
  // === 展示级 ===
  display: {
    fontSize: 112,
    lineHeight: 112,
    fontWeight: '200',
    letterSpacing: -4,
  },
  displayLarge: {
    fontSize: 112,
    lineHeight: 112,
    fontWeight: '200',
    letterSpacing: -2,
  },
  displayMedium: {
    fontSize: 48,
    lineHeight: 56,
    fontWeight: '200',
  },

  // === 标题级 ===
  h1: {
    fontSize: 32,
    lineHeight: 42,  // 1.31x，紧凑但清晰
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  h2: {
    fontSize: 28,
    lineHeight: 38,
    fontWeight: '600',
    letterSpacing: -0.2,
  },
  h3: {
    fontSize: 24,
    lineHeight: 34,
    fontWeight: '600',
    letterSpacing: -0.1,
  },
  h4: {
    fontSize: 20,
    lineHeight: 30,
    fontWeight: '600',
  },
  title: {
    fontSize: 18,
    lineHeight: 28,
    fontWeight: '600',
  },

  // === 正文级 ===
  body: {
    fontSize: 16,
    lineHeight: 26,  // 1.625x，适合长文本阅读
    fontWeight: '400',
  },
  bodyMedium: {
    fontSize: 16,
    lineHeight: 26,
    fontWeight: '500',
  },
  small: {
    fontSize: 14,
    lineHeight: 22,  // 1.57x
    fontWeight: '400',
  },
  smallMedium: {
    fontSize: 14,
    lineHeight: 22,
    fontWeight: '500',
  },

  // === 辅助级 ===
  caption: {
    fontSize: 12,
    lineHeight: 18,
    fontWeight: '400',
  },
  captionMedium: {
    fontSize: 12,
    lineHeight: 18,
    fontWeight: '500',
  },
  tiny: {
    fontSize: 10,
    lineHeight: 14,
    fontWeight: '400',
  },
  navLabel: {
    fontSize: 10,
    lineHeight: 14,
    fontWeight: '500',
  },

  // === 标签级 ===
  label: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '500',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },
  labelSmall: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: '500',
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  labelTitle: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '700',
    letterSpacing: 2,
    textTransform: 'uppercase',
  },

  // === 特殊级 ===
  link: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: '400',
  },
  stat: {
    fontSize: 30,
    lineHeight: 38,
    fontWeight: '300',
  },
};
