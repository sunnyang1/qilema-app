/**
 * Toast 反馈组件
 * 用于显示成功、错误、警告等消息
 * 温暖守护风格
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Platform,
} from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import {
  Colors,
  Spacing,
  BorderRadius,
  Typography,
  Shadows,
  Animation,
} from '@/constants/theme-warm';

const { width } = Dimensions.get('window');

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  visible: boolean;
  message: string;
  type?: ToastType;
  duration?: number;
  onDismiss?: () => void;
}

export const Toast: React.FC<ToastProps> = ({
  visible,
  message,
  type = 'success',
  duration = 3000,
  onDismiss,
}) => {
  const [fadeAnim] = useState(new Animated.Value(0));
  const [translateY] = useState(new Animated.Value(-100));

  const handleDismiss = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: Animation.fast,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: -100,
        duration: Animation.fast,
        useNativeDriver: true,
      }),
    ]).start(() => {
      onDismiss?.();
    });
  };

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: Animation.normal,
          useNativeDriver: true,
        }),
        Animated.spring(translateY, {
          toValue: 0,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
      ]).start();

      const timer = setTimeout(() => {
        handleDismiss();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [visible, duration, fadeAnim, translateY]);

  if (!visible) return null;

  const getToastConfig = () => {
    switch (type) {
      case 'success':
        return {
          gradient: ['#43A047', '#66BB6A'],
          icon: 'check-circle',
          bgColor: Colors.success,
        };
      case 'error':
        return {
          gradient: ['#D32F2F', '#E64A19'],
          icon: 'circle-exclamation',
          bgColor: Colors.error,
        };
      case 'warning':
        return {
          gradient: ['#F57C00', '#FF8A65'],
          icon: 'triangle-exclamation',
          bgColor: Colors.warning,
        };
      case 'info':
      default:
        return {
          gradient: ['#1976D2', '#42A5F5'],
          icon: 'circle-info',
          bgColor: Colors.info,
        };
    }
  };

  const config = getToastConfig();

  return (
    <Animated.View
      style={[
        styles.container,
        {
          opacity: fadeAnim,
          transform: [{ translateY }],
        },
      ]}
    >
      <View style={styles.toastContent}>
        <LinearGradient
          colors={config.gradient as any}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.iconContainer}
        >
          <FontAwesome6 name={config.icon} size={24} color="#FFFFFF" />
        </LinearGradient>
        <Text style={styles.message}>{message}</Text>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 50 : 30,
    left: Spacing.lg,
    right: Spacing.lg,
    zIndex: 1000,
    ...Shadows.strong,
  },

  toastContent: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.xl,
    padding: Spacing.md,
    gap: Spacing.md,
    minHeight: 56,
  },

  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: BorderRadius.lg,
    justifyContent: 'center',
    alignItems: 'center',
  },

  message: {
    ...Typography.bodyMedium,
    color: Colors.textPrimary,
    flex: 1,
  },
});

export default Toast;
