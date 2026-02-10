import 'package:dio/dio.dart';
import 'package:qilema_app/shared/services/auth_service.dart';
import 'package:flutter/foundation.dart';

/// Token拦截器 - 处理401错误和Token刷新
class TokenInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // 如果是401错误且不是刷新Token的请求
    if (err.response?.statusCode == 401 &&
        !err.requestOptions.path.contains('/auth/refresh')) {
      try {
        // 尝试刷新Token
        final success = await AuthService.refreshToken();

        if (success) {
          // 刷新成功，重试原请求
          final newToken = await AuthService.getAccessToken();
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';

          final response = await Dio().fetch(err.requestOptions);
          handler.resolve(response);
          return;
        }
      } catch (e) {
        debugPrint('Token刷新失败: $e');
      }

      // 刷新失败，清除Token
      await AuthService.logout();
    }

    handler.next(err);
  }
}
