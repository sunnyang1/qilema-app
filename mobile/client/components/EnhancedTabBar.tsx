/**
 * 增强型 TabBar 组件
 * - 渐变背景
 * - 图标按压动画
 * - 标签文字缩放效果
 * - 中间 SOS 按钮突出显示
 */
import React, { useCallback } from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  Platform,
  Dimensions,
} from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  interpolate,
  Extrapolation,
} from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { useTheme } from '@/hooks/useTheme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Tab 配置
const TABS = [
  { name: 'index', title: '首页', icon: 'sun' as const, isSpecial: false },
  { name: 'sos', title: 'SOS', icon: 'phone-volume' as const, isSpecial: true },
  { name: 'contacts', title: '联系人', icon: 'address-book' as const, isSpecial: false },
  { name: 'health', title: '健康', icon: 'heart-pulse' as const, isSpecial: false },
  { name: 'knowledge', title: '知识库', icon: 'book-medical' as const, isSpecial: false },
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface TabBarProps {
  state: any;
  descriptors: any;
  navigation: any;
  insets: any;
}

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

function TabItem({
  tab,
  isActive,
  onPress,
}: {
  tab: typeof TABS[0];
  isActive: boolean;
  onPress: () => void;
}) {
  const scale = useSharedValue(1);
  const iconScale = useSharedValue(1);
  const { theme } = useTheme();

  const handlePressIn = useCallback(() => {
    scale.value = withSpring(0.92, { damping: 15, stiffness: 400 });
    iconScale.value = withSpring(0.85, { damping: 15, stiffness: 400 });
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  }, [scale, iconScale]);

  const handlePressOut = useCallback(() => {
    scale.value = withSpring(1, { damping: 15, stiffness: 400 });
    iconScale.value = withSpring(1, { damping: 15, stiffness: 400 });
  }, [scale, iconScale]);

  const containerStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const iconStyle = useAnimatedStyle(() => ({
    transform: [{ scale: iconScale.value }],
  }));

  const titleStyle = useAnimatedStyle(() => ({
    transform: [{ scale: isActive ? 1.05 : 0.95 }],
    opacity: isActive ? 1 : 0.7,
  }));

  if (tab.isSpecial) {
    // SOS 特殊按钮 - 突出显示
    return (
      <View style={styles.sosContainer}>
        <TouchableOpacity
          onPress={onPress}
          onPressIn={handlePressIn}
          onPressOut={handlePressOut}
          activeOpacity={0.9}
          style={styles.sosButton}
        >
          <Animated.View style={containerStyle}>
            <LinearGradient
              colors={[theme.error, '#FF6B6B']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.sosGradient}
            >
              <Animated.View style={iconStyle}>
                <FontAwesome6
                  name={tab.icon}
                  size={24}
                  color="#FFFFFF"
                />
              </Animated.View>
              <Text style={styles.sosText}>{tab.title}</Text>
            </LinearGradient>
          </Animated.View>
          {/* 脉冲光环 */}
          <View style={[styles.sosPulse, { borderColor: theme.error }]} />
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <AnimatedTouchable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      activeOpacity={0.8}
      style={styles.tabItem}
    >
      <Animated.View style={containerStyle}>
        <Animated.View style={iconStyle}>
          <FontAwesome6
            name={tab.icon}
            size={20}
            color={isActive ? theme.primary : theme.textMuted}
          />
        </Animated.View>
        <Animated.Text
          style={[
            styles.tabTitle,
            {
              color: isActive ? theme.primary : theme.textMuted,
            },
            titleStyle,
          ]}
          numberOfLines={1}
        >
          {tab.title}
        </Animated.Text>
        {/* 活跃指示器 */}
        {isActive && (
          <View style={[styles.activeIndicator, { backgroundColor: theme.primary }]} />
        )}
      </Animated.View>
    </AnimatedTouchable>
  );
}

export default function EnhancedTabBar({
  state,
  descriptors,
  navigation,
}: TabBarProps) {
  const insets = useSafeAreaInsets();
  const { theme, isDark } = useTheme();

  const getTabIndex = (routeName: string) => {
    const index = TABS.findIndex(t => t.name === routeName);
    return index === -1 ? 0 : index;
  };

  return (
    <View style={[styles.container, { paddingBottom: insets.bottom }]}>
      {/* 渐变背景 */}
      <LinearGradient
        colors={
          isDark
            ? ['rgba(30,30,30,0.98)', 'rgba(30,30,30,0.95)']
            : ['rgba(255,255,255,0.98)', 'rgba(255,255,255,0.95)']
        }
        style={[
          styles.gradient,
          {
            borderTopColor: theme.border,
            paddingTop: 8,
          },
        ]}
      >
        {/* Tab 项目 */}
        <View style={styles.tabsContainer}>
          {TABS.map((tab, index) => {
            const routeName = tab.name;
            const isFocused = state.index === index;
            const onPress = () => {
              navigation.emit({
                type: 'tabPress',
                target: state.routes[index].key,
                canPreventDefault: true,
              });
              if (!isFocused) {
                navigation.navigate(routeName);
              }
            };

            return (
              <TabItem
                key={tab.name}
                tab={tab}
                isActive={isFocused}
                onPress={onPress}
              />
            );
          })}
        </View>
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  gradient: {
    borderTopWidth: StyleSheet.hairlineWidth,
    paddingBottom: 4,
  },
  tabsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    height: 56,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 4,
  },
  tabTitle: {
    fontSize: 10,
    marginTop: 2,
    fontWeight: '500',
  },
  activeIndicator: {
    position: 'absolute',
    top: -4,
    width: 20,
    height: 3,
    borderRadius: 1.5,
  },
  sosContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    top: -10,
  },
  sosButton: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  sosGradient: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#EF5350',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  sosPulse: {
    position: 'absolute',
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 2,
    opacity: 0.3,
  },
  sosText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
    marginTop: 2,
  },
});
