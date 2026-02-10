import 'package:dio/dio.dart';
import 'package:qilema_app/core/config/app_config.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 日志拦截器 - 打印请求和响应日志
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (AppConfig.isDebugMode) {
      Logger.i('Request: ${options.method} ${options.uri}');
      Logger.d('Headers: ${options.headers}');
      Logger.d('Data: ${options.data}');
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (AppConfig.isDebugMode) {
      Logger.i('Response: ${response.statusCode} ${response.requestOptions.uri}');
      Logger.d('Data: ${response.data}');
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (AppConfig.isDebugMode) {
      Logger.e('Error: ${err.message}');
      Logger.d('Response: ${err.response?.data}');
    }
    handler.next(err);
  }
}
