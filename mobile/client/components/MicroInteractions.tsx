/**
 * 微交互组件库
 * 提供常用的微交互动画效果
 */
import React, { useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Platform,
  ViewStyle,
  TextStyle,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  withRepeat,
  withSequence,
  withDelay,
  interpolate,
  Extrapolation,
  runOnJS,
  Easing,
  FadeIn,
  FadeOut,
  SlideInDown,
  SlideInUp,
  SlideOutUp,
  SlideOutDown,
  ZoomIn,
  ZoomOut,
  Layout,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

// ============================================================================
// PressableCard - 带按压反馈的卡片
// ============================================================================
interface PressableCardProps {
  children: React.ReactNode;
  onPress?: () => void;
  style?: ViewStyle;
  disabled?: boolean;
  hapticFeedback?: boolean;
}

export function PressableCard({
  children,
  onPress,
  style,
  disabled = false,
  hapticFeedback = true,
}: PressableCardProps) {
  const scale = useSharedValue(1);
  const shadow = useSharedValue(1);

  const handlePressIn = useCallback(() => {
    if (disabled) return;
    scale.value = withSpring(0.97, { damping: 15, stiffness: 400 });
    shadow.value = withTiming(0.8, { duration: 100 });
    if (hapticFeedback && Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  }, [disabled, scale, shadow, hapticFeedback]);

  const handlePressOut = useCallback(() => {
    if (disabled) return;
    scale.value = withSpring(1, { damping: 15, stiffness: 400 });
    shadow.value = withTiming(1, { duration: 100 });
  }, [disabled, scale, shadow]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    shadowOpacity: shadow.value * 0.15,
  }));

  return (
    <Animated.View
      onTouchStart={handlePressIn}
      onTouchEnd={handlePressOut}
      onTouchCancel={handlePressOut}
      style={[styles.card, animatedStyle, style]}
    >
      {children}
    </Animated.View>
  );
}

// ============================================================================
// AnimatedButton - 带动画效果的按钮
// ============================================================================
interface AnimatedButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function AnimatedButton({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon,
  style,
  textStyle,
}: AnimatedButtonProps) {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  const handlePressIn = useCallback(() => {
    if (disabled || loading) return;
    scale.value = withSpring(0.95, { damping: 15, stiffness: 400 });
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  }, [disabled, loading, scale]);

  const handlePressOut = useCallback(() => {
    if (disabled || loading) return;
    scale.value = withSpring(1, { damping: 15, stiffness: 400 });
  }, [disabled, loading, scale]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: disabled ? 0.5 : opacity.value,
  }));

  const sizeStyles = {
    small: { paddingVertical: 8, paddingHorizontal: 16, fontSize: 13 },
    medium: { paddingVertical: 12, paddingHorizontal: 24, fontSize: 15 },
    large: { paddingVertical: 16, paddingHorizontal: 32, fontSize: 17 },
  };

  return (
    <Animated.View
      onTouchStart={handlePressIn}
      onTouchEnd={onPress}
      onTouchCancel={handlePressOut}
      style={[
        styles.button,
        styles[`button_${variant}`],
        {
          paddingVertical: sizeStyles[size].paddingVertical,
          paddingHorizontal: sizeStyles[size].paddingHorizontal,
        },
        animatedStyle,
        style,
      ]}
    >
      {loading ? (
        <Animated.Text
          entering={FadeIn}
          style={[styles.buttonText, { fontSize: sizeStyles[size].fontSize }, textStyle]}
        >
          加载中...
        </Animated.Text>
      ) : (
        <>
          {icon}
          <Text
            style={[
              styles.buttonText,
              { fontSize: sizeStyles[size].fontSize },
              textStyle,
            ]}
          >
            {title}
          </Text>
        </>
      )}
    </Animated.View>
  );
}

// ============================================================================
// PulseAnimation - 脉冲动画（用于未读提示等）
// ============================================================================
interface PulseAnimationProps {
  children: React.ReactNode;
  active?: boolean;
  color?: string;
}

export function PulseAnimation({
  children,
  active = true,
  color = '#EF5350',
}: PulseAnimationProps) {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(0.6);

  useEffect(() => {
    if (active) {
      scale.value = withRepeat(
        withSequence(
          withTiming(1.2, { duration: 800, easing: Easing.inOut(Easing.ease) }),
          withTiming(1, { duration: 800, easing: Easing.inOut(Easing.ease) })
        ),
        -1,
        false
      );
      opacity.value = withRepeat(
        withSequence(
          withTiming(0.3, { duration: 800 }),
          withTiming(0.6, { duration: 800 })
        ),
        -1,
        false
      );
    } else {
      scale.value = withTiming(1);
      opacity.value = withTiming(0);
    }
  }, [active, scale, opacity]);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <View style={styles.pulseContainer}>
      <Animated.View
        style={[
          styles.pulse,
          { backgroundColor: color },
          pulseStyle,
        ]}
      />
      {children}
    </View>
  );
}

// ============================================================================
// ShimmerLoading - 骨架屏闪烁动画
// ============================================================================
interface ShimmerLoadingProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export function ShimmerLoading({
  width = '100%',
  height = 20,
  borderRadius = 4,
  style,
}: ShimmerLoadingProps) {
  const translateX = useSharedValue(-200);

  useEffect(() => {
    translateX.value = withRepeat(
      withTiming(400, { duration: 1200, easing: Easing.linear }),
      -1,
      false
    );
  }, [translateX]);

  const shimmerStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <View
      style={[
        styles.shimmer,
        {
          width: width as any,
          height,
          borderRadius,
        },
        style,
      ]}
    >
      <Animated.View
        style={[styles.shimmerGradient, shimmerStyle]}
      />
    </View>
  );
}

// ============================================================================
// FlipSwitch - 翻转开关动画
// ============================================================================
interface FlipSwitchProps {
  value: boolean;
  onValueChange: (value: boolean) => void;
  disabled?: boolean;
  activeColor?: string;
  inactiveColor?: string;
}

export function FlipSwitch({
  value,
  onValueChange,
  disabled = false,
  activeColor = '#34C759',
  inactiveColor = '#E9E9EB',
}: FlipSwitchProps) {
  const translateX = useSharedValue(value ? 22 : 0);

  useEffect(() => {
    translateX.value = withSpring(value ? 22 : 0, {
      damping: 15,
      stiffness: 300,
    });
    if (Platform.OS !== 'web') {
      Haptics.selectionAsync();
    }
  }, [value, translateX]);

  const thumbStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  const handlePress = () => {
    if (!disabled) {
      onValueChange(!value);
    }
  };

  return (
    <Animated.View
      onTouchStart={handlePress}
      style={[
        styles.switchTrack,
        {
          backgroundColor: value ? activeColor : inactiveColor,
          opacity: disabled ? 0.5 : 1,
        },
      ]}
    >
      <Animated.View style={[styles.switchThumb, thumbStyle]} />
    </Animated.View>
  );
}

// ============================================================================
// CountUpNumber - 数字滚动动画
// ============================================================================
interface CountUpNumberProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  style?: TextStyle;
}

export function CountUpNumber({
  value,
  duration = 1500,
  prefix = '',
  suffix = '',
  style,
}: CountUpNumberProps) {
  const animatedValue = useSharedValue(0);

  useEffect(() => {
    animatedValue.value = withTiming(value, {
      duration,
      easing: Easing.out(Easing.cubic),
    });
  }, [value, duration, animatedValue]);

  const displayStyle = useAnimatedStyle(() => ({
    opacity: interpolate(
      animatedValue.value,
      [0, value],
      [0.3, 1],
      Extrapolation.CLAMP
    ),
  }));

  return (
    <Animated.Text style={[styles.countUpText, style, displayStyle]}>
      {prefix}{Math.round(animatedValue.value)}{suffix}
    </Animated.Text>
  );
}

// ============================================================================
// PageTransition - 页面过渡效果
// ============================================================================
interface PageTransitionProps {
  children: React.ReactNode;
  visible: boolean;
  type?: 'fade' | 'slide' | 'zoom';
}

export function PageTransition({
  children,
  visible,
  type = 'fade',
}: PageTransitionProps) {
  if (!visible) return null;

  const entering = {
    fade: FadeIn.duration(300),
    slide: SlideInDown.duration(300),
    zoom: ZoomIn.duration(300),
  }[type];

  const exiting = {
    fade: FadeOut.duration(200),
    slide: SlideOutUp.duration(200),
    zoom: ZoomOut.duration(200),
  }[type];

  return (
    <Animated.View entering={entering} exiting={exiting}>
      {children}
    </Animated.View>
  );
}

// ============================================================================
// BounceIn - 弹入动画
// ============================================================================
interface BounceInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}

export function BounceIn({
  children,
  delay = 0,
  duration = 600,
}: BounceInProps) {
  return (
    <Animated.View
      entering={ZoomIn.delay(delay).springify().damping(12).stiffness(180)}
    >
      {children}
    </Animated.View>
  );
}

// ============================================================================
// SkeletonList - 骨架屏列表
// ============================================================================
interface SkeletonListProps {
  count?: number;
  height?: number;
}

export function SkeletonList({ count = 5, height = 60 }: SkeletonListProps) {
  return (
    <View style={styles.skeletonList}>
      {Array.from({ length: count }).map((_, index) => (
        <Animated.View
          key={index}
          entering={FadeIn.delay(index * 100).duration(300)}
          style={styles.skeletonItem}
        >
          <ShimmerLoading width={50} height={50} borderRadius={25} />
          <View style={styles.skeletonContent}>
            <ShimmerLoading width="60%" height={16} style={{ marginBottom: 8 }} />
            <ShimmerLoading width="40%" height={12} />
          </View>
        </Animated.View>
      ))}
    </View>
  );
}

// ============================================================================
// SuccessCheckmark - 成功打勾动画
// ============================================================================
interface SuccessCheckmarkProps {
  size?: number;
  color?: string;
}

export function SuccessCheckmark({
  size = 60,
  color = '#34C759',
}: SuccessCheckmarkProps) {
  const scale = useSharedValue(0);
  const checkScale = useSharedValue(0);

  useEffect(() => {
    scale.value = withSpring(1, { damping: 10, stiffness: 200 });
    checkScale.value = withDelay(
      200,
      withSpring(1, { damping: 12, stiffness: 300 })
    );
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  }, [scale, checkScale]);

  const circleStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const checkStyle = useAnimatedStyle(() => ({
    transform: [{ scale: checkScale.value }],
  }));

  return (
    <Animated.View style={[styles.checkmarkCircle, { width: size, height: size }, circleStyle]}>
      <Animated.View style={checkStyle}>
        <View style={[styles.checkmark, { borderColor: color }]} />
      </Animated.View>
    </Animated.View>
  );
}

// ============================================================================
// Shake - 摇晃动画（用于错误提示）
// ============================================================================
interface ShakeProps {
  children: React.ReactNode;
  trigger?: boolean;
}

export function Shake({ children, trigger }: ShakeProps) {
  const translateX = useSharedValue(0);

  useEffect(() => {
    if (trigger) {
      translateX.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
    }
  }, [trigger, translateX]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return <Animated.View style={animatedStyle}>{children}</Animated.View>;
}

// ============================================================================
// WaterWave - 水波纹效果
// ============================================================================
interface WaterWaveProps {
  children?: React.ReactNode;
  active?: boolean;
  color?: string;
}

export function WaterWave({ children, active = true, color = '#007AFF' }: WaterWaveProps) {
  const wave1 = useSharedValue(0);
  const wave2 = useSharedValue(0);

  useEffect(() => {
    if (active) {
      wave1.value = withRepeat(
        withTiming(360, { duration: 2000, easing: Easing.linear }),
        -1,
        false
      );
      wave2.value = withRepeat(
        withTiming(360, { duration: 2500, easing: Easing.linear }),
        -1,
        false
      );
    }
  }, [active, wave1, wave2]);

  const wave1Style = useAnimatedStyle(() => ({
    transform: [{ translateX: Math.sin(wave1.value * (Math.PI / 180)) * 20 }],
  }));

  const wave2Style = useAnimatedStyle(() => ({
    transform: [{ translateX: Math.sin(wave2.value * (Math.PI / 180)) * 15 }],
  }));

  if (!active) return <>{children}</>;

  return (
    <View style={styles.waterWaveContainer}>
      <Animated.View style={[styles.waterWave, wave1Style]} />
      <Animated.View style={[styles.waterWave, styles.waterWave2, wave2Style]} />
      {children}
    </View>
  );
}

// ============================================================================
// Styles
// ============================================================================
const styles = StyleSheet.create({
  // PressableCard
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },

  // Button
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
  },
  button_primary: {
    backgroundColor: '#007AFF',
  },
  button_secondary: {
    backgroundColor: '#5856D6',
  },
  button_outline: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: '#007AFF',
  },
  button_ghost: {
    backgroundColor: 'transparent',
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },

  // Pulse
  pulseContainer: {
    position: 'relative',
  },
  pulse: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    borderRadius: 999,
  },

  // Shimmer
  shimmer: {
    backgroundColor: '#E0E0E0',
    overflow: 'hidden',
  },
  shimmerGradient: {
    width: 200,
    height: '100%',
    backgroundColor: 'rgba(255,255,255,0.4)',
    transform: [{ skewX: '-20deg' }],
  },

  // Switch
  switchTrack: {
    width: 51,
    height: 31,
    borderRadius: 16,
    padding: 2,
  },
  switchThumb: {
    width: 27,
    height: 27,
    borderRadius: 14,
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },

  // CountUp
  countUpText: {
    fontVariant: ['tabular-nums'],
  },

  // Skeleton
  skeletonList: {
    padding: 16,
  },
  skeletonItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  skeletonContent: {
    flex: 1,
    marginLeft: 12,
  },

  // Checkmark
  checkmarkCircle: {
    borderRadius: 999,
    backgroundColor: '#34C759',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkmark: {
    width: 20,
    height: 10,
    borderLeftWidth: 3,
    borderBottomWidth: 3,
    borderColor: '#FFFFFF',
    transform: [{ rotate: '-45deg' }],
    marginTop: -5,
  },

  // WaterWave
  waterWaveContainer: {
    position: 'relative',
    overflow: 'hidden',
  },
  waterWave: {
    position: 'absolute',
    width: '200%',
    height: '100%',
    backgroundColor: 'rgba(0,122,255,0.1)',
    borderRadius: 999,
  },
  waterWave2: {
    backgroundColor: 'rgba(0,122,255,0.05)',
  },
});
