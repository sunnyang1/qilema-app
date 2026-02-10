/// App配置
class AppConfig {
  /// API基础URL
  static const String baseUrl = 'http://localhost:8000/api/v1';

  /// 连接超时时间（毫秒）
  static const int connectTimeout = 10000;

  /// 接收超时时间（毫秒）
  static const int receiveTimeout = 10000;

  /// 是否启用调试模式
  static const bool isDebugMode = true;

  /// App版本
  static const String appVersion = '1.0.0';
}
