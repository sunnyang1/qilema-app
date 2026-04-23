/**
 * 设置页面路由入口
 */
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useTheme } from '@/hooks/useTheme';

export default function SettingsLayout() {
  const { isDark } = useTheme();

  return (
    <>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <Stack
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
          contentStyle: { backgroundColor: 'transparent' },
        }}
      />
    </>
  );
}
