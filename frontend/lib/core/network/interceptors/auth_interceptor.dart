import 'package:dio/dio.dart';
import 'package:qilema_app/shared/services/auth_service.dart';

/// 认证拦截器 - 自动添加Token到请求头
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // 从存储中获取Token
    final token = await AuthService.getAccessToken();

    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }
}
