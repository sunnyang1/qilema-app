library;

/// 异常类体系
///
/// 提供统一的异常处理机制，包括：
/// - AppException: 基础异常类
/// - ApiException: API 相关异常
/// - NetworkException: 网络相关异常
/// - ValidationException: 验证相关异常

/// 网络异常类型
enum NetworkExceptionType {
  /// 无网络连接
  noConnection,

  /// 请求超时
  timeout,

  /// 服务器错误
  serverError,
}

/// 基础异常类
///
/// 所有应用异常的基类，包含错误码、错误信息和可选的详细信息
class AppException implements Exception {
  /// 错误码，用于唯一标识异常类型
  final String code;

  /// 错误消息，用于显示给用户
  final String message;

  /// 额外的详细信息，可选
  final Map<String, dynamic>? details;

  AppException({
    required this.code,
    required this.message,
    this.details,
  });

  @override
  String toString() {
    final buffer = StringBuffer('AppException(code: $code, message: $message');
    if (details != null && details!.isNotEmpty) {
      buffer.write(', details: $details');
    }
    buffer.write(')');
    return buffer.toString();
  }
}

/// API 异常类
///
/// 用于表示 API 调用过程中的错误，包含 HTTP 状态码
class ApiException extends AppException {
  /// HTTP 状态码
  final int statusCode;

  ApiException({
    required super.code,
    required super.message,
    required this.statusCode,
    super.details,
  });

  @override
  String toString() {
    final buffer = StringBuffer('ApiException(code: $code, message: $message, statusCode: $statusCode');
    if (details != null && details!.isNotEmpty) {
      buffer.write(', details: $details');
    }
    buffer.write(')');
    return buffer.toString();
  }
}

/// 网络异常类
///
/// 用于表示网络连接相关的错误，如无网络、超时等
class NetworkException extends AppException {
  /// 网络异常类型
  final NetworkExceptionType type;

  NetworkException({
    required super.code,
    required super.message,
    required this.type,
    super.details,
  });

  @override
  String toString() {
    final buffer = StringBuffer('NetworkException(code: $code, message: $message, type: $type');
    if (details != null && details!.isNotEmpty) {
      buffer.write(', details: $details');
    }
    buffer.write(')');
    return buffer.toString();
  }
}

/// 验证异常类
///
/// 用于表示数据验证失败，如无效的输入字段
class ValidationException extends AppException {
  /// 验证失败的字段名
  final String field;

  ValidationException({
    required super.code,
    required super.message,
    required this.field,
    super.details,
  });

  @override
  String toString() {
    final buffer = StringBuffer('ValidationException(code: $code, message: $message, field: $field');
    if (details != null && details!.isNotEmpty) {
      buffer.write(', details: $details');
    }
    buffer.write(')');
    return buffer.toString();
  }
}
