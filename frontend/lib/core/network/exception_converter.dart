library;

import 'package:dio/dio.dart';
import 'package:qilema_app/core/exceptions/exceptions.dart';

/// Dio异常转换工具
///
/// 将DioException转换为AppException子类
class ExceptionConverter {
  /// 转换DioException为AppException
  ///
  /// 根据DioException的类型转换为对应的AppException子类
  static AppException convertDioException(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
      case DioExceptionType.sendTimeout:
        return NetworkException(
          code: 'NETWORK_TIMEOUT',
          message: '网络请求超时，请检查网络连接',
          type: NetworkExceptionType.timeout,
        );

      case DioExceptionType.connectionError:
        return NetworkException(
          code: 'NO_CONNECTION',
          message: '网络连接失败，请检查网络设置',
          type: NetworkExceptionType.noConnection,
        );

      case DioExceptionType.badResponse:
        // 检查状态码
        final statusCode = e.response?.statusCode;
        if (statusCode != null && statusCode >= 500) {
          return NetworkException(
            code: 'SERVER_ERROR_$statusCode',
            message: '服务器错误，请稍后重试',
            type: NetworkExceptionType.serverError,
          );
        }

        // 4xx错误转换为ApiException
        final errorMessage = extractErrorMessage(e.response?.data);
        return ApiException(
          code: 'API_ERROR_$statusCode',
          message: errorMessage,
          statusCode: statusCode ?? 400,
          details: e.response?.data as Map<String, dynamic>?,
        );

      case DioExceptionType.cancel:
        return NetworkException(
          code: 'REQUEST_CANCELLED',
          message: '请求已取消',
          type: NetworkExceptionType.noConnection,
        );

      case DioExceptionType.unknown:
      default:
        return NetworkException(
          code: 'UNKNOWN_NETWORK_ERROR',
          message: '网络请求失败: ${e.message}',
          type: NetworkExceptionType.noConnection,
        );
    }
  }

  /// 提取错误消息
  ///
  /// 从响应数据中提取错误消息，支持多种格式
  static String extractErrorMessage(dynamic data) {
    if (data == null) return '请求失败';

    if (data is Map<String, dynamic>) {
      // 尝试从不同的字段中提取错误消息
      return data['message'] ??
          data['error'] ??
          data['detail'] ??
          data['msg'] ??
          '请求失败';
    }

    if (data is String) {
      return data;
    }

    return '请求失败';
  }
}
