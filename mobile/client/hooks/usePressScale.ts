/**
 * usePressScale Hook
 *
 * 提取按压缩放动画为可复用 hook，消除各页面重复的 Animated.spring 模式。
 *
 * 用法：
 * ```tsx
 * const { scale, pressHandlers } = usePressScale(0.97);
 * <Animated.View style={{ transform: [{ scale }] }} {...pressHandlers}>
 * ```
 */

import { useRef } from 'react';
import { Animated } from 'react-native';

interface PressScaleOptions {
  /** 按下时的缩放比例，默认 0.97 */
  activeScale?: number;
  /** 弹簧速度（按下），默认 50 */
  pressSpeed?: number;
  /** 弹簧速度（松开），默认 30 */
  releaseSpeed?: number;
}

interface PressScaleResult {
  /** Animated.Value，可直接用于 transform */
  scale: Animated.Value;
  /** 展开 onPressIn / onPressOut 回调，可传给 Pressable / TouchableOpacity */
  pressHandlers: {
    onPressIn: () => void;
    onPressOut: () => void;
  };
}

export function usePressScale(optionsOrScale: number | PressScaleOptions = {}): PressScaleResult {
  const opts = typeof optionsOrScale === 'number'
    ? { activeScale: optionsOrScale }
    : optionsOrScale;
  const { activeScale = 0.97, pressSpeed = 50, releaseSpeed = 30 } = opts;
  const scale = useRef(new Animated.Value(1)).current;

  const onPressIn = () =>
    Animated.spring(scale, { toValue: activeScale, useNativeDriver: true, speed: pressSpeed }).start();

  const onPressOut = () =>
    Animated.spring(scale, { toValue: 1, useNativeDriver: true, speed: releaseSpeed }).start();

  return { scale, pressHandlers: { onPressIn, onPressOut } };
}
