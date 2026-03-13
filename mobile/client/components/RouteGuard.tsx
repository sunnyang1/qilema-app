import { useEffect } from 'react';
import { useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';

/**
 * 路由守卫组件
 * 功能：
 * 1. 检测用户登录状态
 * 2. 自动跳转到登录/首页
 * 3. 处理 Token 过期情况
 */
export function RouteGuard() {
  const router = useRouter();
  const segments = useSegments();
  const rootState = useRootNavigationState();
  const { isAuthenticated, isLoading, logout } = useAuth();

  // 需要认证的路由路径
  const protectedRoutes = [
    '(tabs)',
    'sos',
    'sos-status',
    'contacts',
    'health',
    'history',
    'medication',
    'allergies',
    'knowledge',
    'devices',
    'signin',
  ];

  // 公开路由（不需要认证）
  const publicRoutes = ['login', 'register', '+not-found'];

  useEffect(() => {
    // 1. 导航未就绪或鉴权正在加载中，直接返回
    if (!rootState?.key || isLoading) {
      return;
    }

    // 2. 当前路由路径
    const currentPath = segments.join('/');

    // 3. 检查是否是公开路由
    const isPublicRoute = publicRoutes.some(route => currentPath.includes(route));

    // 4. 检查是否是受保护路由
    const isProtectedRoute = protectedRoutes.some(route => currentPath.includes(route));

    // 5. 未登录访问受保护路由 → 跳转到登录页
    if (!isAuthenticated && isProtectedRoute && !isPublicRoute) {
      router.replace('/login');
      return;
    }

    // 6. 已登录访问登录/注册页 → 跳转到首页
    if (isAuthenticated && isPublicRoute && (currentPath.includes('login') || currentPath.includes('register'))) {
      router.replace('/(tabs)/index');
      return;
    }
  }, [rootState?.key, isAuthenticated, isLoading, segments, router]);

  // 组件不渲染任何 UI
  return null;
}
