/**
 * 底部 TabBar 布局
 * 使用增强型 TabBar 组件
 */
import { Tabs } from 'expo-router';
import { Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import EnhancedTabBar from '@/components/EnhancedTabBar';

export default function TabLayout() {
  const insets = useSafeAreaInsets();

  return (
    <Tabs
      screenOptions={{
        freezeOnBlur: true,
        headerShown: false,
        tabBarStyle: {
          display: 'none', // 隐藏原生 TabBar，使用自定义的 EnhancedTabBar
        },
      }}
      tabBar={(props) => <EnhancedTabBar {...props} />}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '首页',
        }}
      />
      <Tabs.Screen
        name="sos"
        options={{
          title: 'SOS',
        }}
      />
      <Tabs.Screen
        name="contacts"
        options={{
          title: '联系人',
        }}
      />
      <Tabs.Screen
        name="health"
        options={{
          title: '健康',
        }}
      />
      <Tabs.Screen
        name="knowledge"
        options={{
          title: '知识库',
        }}
      />
    </Tabs>
  );
}
