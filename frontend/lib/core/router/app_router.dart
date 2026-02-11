import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/shared/services/auth_service.dart';
import 'package:qilema_app/features/auth/pages/login_page.dart';
import 'package:qilema_app/features/auth/pages/register_page.dart';
import 'package:qilema_app/features/signin/pages/home_page.dart';
import 'package:qilema_app/features/signin/pages/history_page.dart';
import 'package:qilema_app/features/sos/pages/sos_page.dart';
import 'package:qilema_app/features/sos/pages/sos_status_page.dart';
import 'package:qilema_app/features/contacts/pages/contacts_page.dart';
import 'package:qilema_app/features/contacts/pages/contact_edit_page.dart';
import 'package:qilema_app/features/health/pages/health_page.dart';
import 'package:qilema_app/features/health/pages/medical_histories_page.dart';
import 'package:qilema_app/features/health/pages/medications_page.dart';
import 'package:qilema_app/features/health/pages/allergies_page.dart';
import 'package:qilema_app/features/devices/pages/devices_page.dart';
import 'package:qilema_app/features/devices/pages/device_data_page.dart';
import 'package:qilema_app/features/emergency/pages/aed_map_page.dart';
import 'package:qilema_app/features/emergency/pages/hospitals_page.dart';
import 'package:qilema_app/features/knowledge/pages/knowledge_categories_page.dart';
import 'package:qilema_app/features/knowledge/pages/articles_page.dart';
import 'package:qilema_app/features/knowledge/pages/article_detail_page.dart';
import 'package:qilema_app/features/medication/pages/medication_reminders_page.dart';
import 'package:qilema_app/features/medication/pages/add_medication_page.dart';

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
      GoRoute(
        path: '/contacts',
        builder: (context, state) => const ContactsPage(),
        name: 'contacts',
      ),
      GoRoute(
        path: '/contacts/edit',
        builder: (context, state) => const ContactEditPage(),
        name: 'contact-edit',
      ),
      GoRoute(
        path: '/health',
        builder: (context, state) => const HealthPage(),
        name: 'health',
      ),
      GoRoute(
        path: '/medical-histories',
        builder: (context, state) => const MedicalHistoriesPage(),
        name: 'medical-histories',
      ),
      GoRoute(
        path: '/medications',
        builder: (context, state) => const MedicationsPage(),
        name: 'medications',
      ),
      GoRoute(
        path: '/allergies',
        builder: (context, state) => const AllergiesPage(),
        name: 'allergies',
      ),
      GoRoute(
        path: '/devices',
        builder: (context, state) => const DevicesPage(),
        name: 'devices',
      ),
      GoRoute(
        path: '/devices/:deviceId/data',
        builder: (context, state) {
          final deviceId = state.pathParameters['deviceId']!;
          return DeviceDataPage(deviceId: deviceId);
        },
        name: 'device-data',
      ),
      GoRoute(
        path: '/aed-map',
        builder: (context, state) => const AedMapPage(),
        name: 'aed-map',
      ),
      GoRoute(
        path: '/hospitals',
        builder: (context, state) => const HospitalsPage(),
        name: 'hospitals',
      ),
      GoRoute(
        path: '/knowledge',
        builder: (context, state) => const KnowledgeCategoriesPage(),
        name: 'knowledge',
      ),
      GoRoute(
        path: '/knowledge/category/:categoryId',
        builder: (context, state) {
          final categoryId = state.pathParameters['categoryId'];
          return ArticlesPage(categoryId: categoryId);
        },
        name: 'knowledge-articles',
      ),
      GoRoute(
        path: '/knowledge/articles/:articleId',
        builder: (context, state) {
          final articleId = state.pathParameters['articleId']!;
          return ArticleDetailPage(articleId: articleId);
        },
        name: 'article-detail',
      ),
      GoRoute(
        path: '/medication',
        builder: (context, state) => const MedicationRemindersPage(),
        name: 'medication',
      ),
      GoRoute(
        path: '/medication/add',
        builder: (context, state) => const AddMedicationPage(),
        name: 'medication-add',
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('页面未找到: ${state.uri}'),
      ),
    ),
  );
}
