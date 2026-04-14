import { Tabs } from 'expo-router';
import { Platform } from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function TabLayout() {
  const { theme, isDark } = useTheme();
  const insets = useSafeAreaInsets();

  return (
    <Tabs
      screenOptions={{
        freezeOnBlur: true,
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.backgroundDefault,
          borderTopColor: theme.border,
          height: Platform.OS === 'web' ? 60 : 50 + insets.bottom,
          paddingBottom: Platform.OS === 'web' ? 0 : insets.bottom,
        },
        tabBarActiveTintColor: theme.primary,
        tabBarInactiveTintColor: theme.textMuted,
        tabBarItemStyle: {
          height: Platform.OS === 'web' ? 60 : undefined,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '首页',
          tabBarIcon: ({ color, size }) => (
            <FontAwesome6 name="sun" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="sos"
        options={{
          title: 'SOS',
          tabBarIcon: ({ color, size }) => (
            <FontAwesome6 name="phone-volume" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="contacts"
        options={{
          title: '联系人',
          tabBarIcon: ({ color, size }) => (
            <FontAwesome6 name="address-book" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="health"
        options={{
          title: '健康',
          tabBarIcon: ({ color, size }) => (
            <FontAwesome6 name="heart-pulse" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="knowledge"
        options={{
          title: '知识库',
          tabBarIcon: ({ color, size }) => (
            <FontAwesome6 name="book-medical" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
