library;

import 'package:dio/dio.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/network/exception_converter.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// BaseApi 抽象类
///
/// 封装通用的HTTP请求逻辑，提供统一的错误处理和响应处理
/// 子类只需专注于业务逻辑，无需关心网络请求的细节
abstract class BaseApi {
  /// ApiClient 实例，用于发起HTTP请求
  final ApiClient apiClient;

  BaseApi(this.apiClient);

  /// 处理API响应
  ///
  /// 统一处理响应数据、错误转换、日志记录等
  ///
  /// Parameters:
  /// - [request]: 要执行的HTTP请求Future
  /// - [operation]: 操作描述，用于日志记录（如"获取用户列表"）
  ///
  /// Returns: 响应数据（T类型）
  /// Throws:
  /// - [ApiException]: API错误（4xx, 5xx）
  /// - [NetworkException]: 网络错误（超时、无连接）
  Future<T> _handleResponse<T>(Future<Response> request, String operation) async {
    try {
      final response = await request;

      // 检查响应状态码
      if (response.statusCode == 200 || response.statusCode == 201) {
        // 成功响应，返回数据
        return response.data as T;
      }

      // 错误响应，抛出ApiException
      throw ExceptionConverter.convertDioException(
        DioException(
          requestOptions: response.requestOptions,
          type: DioExceptionType.badResponse,
          response: response,
        ),
      );
    } on DioException catch (e, stackTrace) {
      // 处理Dio异常
      Logger.e('$operation - Dio异常', error: e, stackTrace: stackTrace);

      throw ExceptionConverter.convertDioException(e);
    } catch (e, stackTrace) {
      // 其他未知异常
      Logger.e('$operation - 未知异常', error: e, stackTrace: stackTrace);
      throw ExceptionConverter.convertDioException(
        DioException(
          requestOptions: RequestOptions(path: '/unknown'),
          type: DioExceptionType.unknown,
          message: e.toString(),
        ),
      );
    }
  }

  /// GET 请求
  ///
  /// Parameters:
  /// - [path]: API路径
  /// - [queryParameters]: 查询参数（可选）
  /// - [operation]: 操作描述，用于日志记录（默认为"GET请求"）
  ///
  /// Returns: 响应数据
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    String operation = 'GET请求',
  }) {
    Logger.d('GET $path, params: $queryParameters');
    return _handleResponse<T>(
      apiClient.get(path, queryParameters: queryParameters),
      operation,
    );
  }

  /// POST 请求
  ///
  /// Parameters:
  /// - [path]: API路径
  /// - [data]: 请求体数据（可选）
  /// - [queryParameters]: 查询参数（可选）
  /// - [operation]: 操作描述，用于日志记录（默认为"POST请求"）
  ///
  /// Returns: 响应数据
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    String operation = 'POST请求',
  }) {
    Logger.d('POST $path, data: $data');
    return _handleResponse<T>(
      apiClient.post(path, data: data, queryParameters: queryParameters),
      operation,
    );
  }

  /// PUT 请求
  ///
  /// Parameters:
  /// - [path]: API路径
  /// - [data]: 请求体数据（可选）
  /// - [queryParameters]: 查询参数（可选）
  /// - [operation]: 操作描述，用于日志记录（默认为"PUT请求"）
  ///
  /// Returns: 响应数据
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    String operation = 'PUT请求',
  }) {
    Logger.d('PUT $path, data: $data');
    return _handleResponse<T>(
      apiClient.put(path, data: data, queryParameters: queryParameters),
      operation,
    );
  }

  /// DELETE 请求
  ///
  /// Parameters:
  /// - [path]: API路径
  /// - [data]: 请求体数据（可选）
  /// - [queryParameters]: 查询参数（可选）
  /// - [operation]: 操作描述，用于日志记录（默认为"DELETE请求"）
  ///
  /// Returns: 响应数据
  Future<T> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    String operation = 'DELETE请求',
  }) {
    Logger.d('DELETE $path, data: $data');
    return _handleResponse<T>(
      apiClient.delete(path, data: data, queryParameters: queryParameters),
      operation,
    );
  }
}
