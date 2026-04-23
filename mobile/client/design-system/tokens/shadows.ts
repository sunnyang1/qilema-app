/**
 * 阴影令牌 - Shadow Tokens
 * 为不同层级组件提供一致的深度感知
 */
import { ShadowScale } from '../types';

/**
 * 生成阴影令牌
 * @param shadowColor 阴影颜色（通常为主题色的透明变体）
 * @param shadowStrongColor 强阴影颜色
 */
export function createShadows(shadowColor: string, shadowStrongColor: string): ShadowScale {
  return {
    soft: {
      shadowColor,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 1,
      shadowRadius: 8,
      elevation: 2,
    },
    medium: {
      shadowColor,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 1,
      shadowRadius: 12,
      elevation: 4,
    },
    strong: {
      shadowColor: shadowStrongColor,
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 1,
      shadowRadius: 16,
      elevation: 8,
    },
    glow: {
      shadowColor: shadowColor.replace(/[\d.]+\)$/, '0.35)'), // 提高不透明度模拟发光
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.35,
      shadowRadius: 20,
      elevation: 8,
    },
    card: {
      shadowColor,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 1,
      shadowRadius: 10,
      elevation: 3,
    },
  };
}
