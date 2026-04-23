import '@/utils/auth-interceptor';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { LogBox } from 'react-native';
import { enableFreeze } from 'react-native-screens';
import Toast from 'react-native-toast-message';
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from '@/design-system';
import { RouteGuard } from '@/components/RouteGuard';

LogBox.ignoreLogs([
  "TurboModuleRegistry.getEnforcing(...): 'RNMapsAirModule' could not be found",
]);

enableFreeze(true);

export default function RootLayout() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <GestureHandlerRootView style={{ flex: 1 }}>
          <StatusBar style="auto"></StatusBar>
          <RouteGuard />
          <Stack screenOptions={{
            animation: 'slide_from_right',
            gestureEnabled: true,
            gestureDirection: 'horizontal',
            headerShown: false
          }}>
            {/* 登录/注册 */}
            <Stack.Screen name="login" options={{ title: "登录" }} />
            <Stack.Screen name="register" options={{ title: "注册" }} />

            {/* 主应用 */}
            <Stack.Screen name="(tabs)" options={{ headerShown: false }} />

            {/* 紧急求助模块 */}
            <Stack.Screen name="sos" options={{ title: "紧急求助" }} />
            <Stack.Screen name="sos-status" options={{ title: "SOS状态" }} />

            {/* 联系人模块 */}
            <Stack.Screen name="contacts" options={{ title: "紧急联系人" }} />
            <Stack.Screen name="contacts/edit" options={{ title: "编辑联系人" }} />
            <Stack.Screen name="contact-detail" options={{ title: "联系人详情" }} />

            {/* 健康档案模块 */}
            <Stack.Screen name="health" options={{ title: "健康档案" }} />
            <Stack.Screen name="history" options={{ title: "病史" }} />
            <Stack.Screen name="medication" options={{ title: "药物" }} />
            <Stack.Screen name="allergies" options={{ title: "过敏史" }} />

            {/* 知识库模块 */}
            <Stack.Screen name="knowledge/categories" options={{ title: "知识库分类" }} />
            <Stack.Screen name="knowledge/articles" options={{ title: "文章列表" }} />
            <Stack.Screen name="knowledge/article-detail" options={{ title: "文章详情" }} />

            {/* 用药提醒模块 */}
            <Stack.Screen name="medication/reminders" options={{ title: "用药提醒" }} />
            <Stack.Screen name="medication/add" options={{ title: "添加药物" }} />

            {/* 设备模块 */}
            <Stack.Screen name="devices/list" options={{ title: "设备列表" }} />
            <Stack.Screen name="devices/data" options={{ title: "设备数据" }} />

            {/* 急救资源模块 */}
            <Stack.Screen name="emergency/hospitals" options={{ title: "医院列表" }} />
            <Stack.Screen name="emergency/aed" options={{ title: "AED地图" }} />

            {/* 签到模块 */}
            <Stack.Screen name="signin/history" options={{ title: "签到历史" }} />
          </Stack>
          <Toast />
        </GestureHandlerRootView>
      </ThemeProvider>
    </AuthProvider>
  );
}
