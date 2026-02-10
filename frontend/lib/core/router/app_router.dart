import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/shared/services/auth_service.dart';
import 'package:qilema_app/features/auth/pages/login_page.dart';
import 'package:qilema_app/features/auth/pages/register_page.dart';
import 'package:qilema_app/features/signin/pages/home_page.dart';
import 'package:qilema_app/features/signin/pages/history_page.dart';
import 'package:qilema_app/features/sos/pages/sos_page.dart';
import 'package:qilema_app/features/sos/pages/sos_status_page.dart';

/// 路由配置
class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/login',
    redirect: (context, state) async {
      final isLoggedIn = await AuthService.isLoggedIn();

      final isLoginRoute = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';

      // 如果未登录且不在登录/注册页面，跳转到登录页
      if (!isLoggedIn && !isLoginRoute) {
        return '/login';
      }

      // 如果已登录且在登录/注册页面，跳转到首页
      if (isLoggedIn && isLoginRoute) {
        return '/';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
        name: 'login',
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterPage(),
        name: 'register',
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const HomePage(),
        name: 'home',
      ),
      GoRoute(
        path: '/history',
        builder: (context, state) => const HistoryPage(),
        name: 'history',
      ),
      GoRoute(
        path: '/sos',
        builder: (context, state) => const SosPage(),
        name: 'sos',
      ),
      GoRoute(
        path: '/sos/status',
        builder: (context, state) => const SosStatusPage(),
        name: 'sos-status',
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('页面未找到: ${state.uri}'),
      ),
    ),
  );
}
