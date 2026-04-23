/**
 * 交互令牌 - Interaction Tokens
 * 触摸反馈、动画配置等交互相关常量
 */
import { InteractionTokens } from '../types';

export const interaction: InteractionTokens = {
  // 按压缩放比例
  buttonScale: 0.96,
  cardScale: 0.98,

  // 涟漪效果半径
  rippleRadius: {
    small: 20,
    medium: 24,
    large: 30,
    extraLarge: 40,
  },

  // 动画性能优化
  useNativeDriver: true,

  // 尊重系统"减少动画"设置
  respectReducedMotion: true,
};
