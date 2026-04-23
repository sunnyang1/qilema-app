/**
 * 动画令牌 - Animation Tokens
 * 统一动画时长，确保交互一致性
 */
import { AnimationTokens } from '../types';

export const animation: AnimationTokens = {
  instant: 100,   // 瞬间 - 微交互反馈
  fast: 150,      // 快速 - 按钮按压、开关切换
  normal: 300,    // 正常 - 页面过渡、模态框
  slow: 500,      // 慢速 - 复杂动画、展开/收起
  verySlow: 800,  // 非常慢 - 强调动画、首次加载
};
