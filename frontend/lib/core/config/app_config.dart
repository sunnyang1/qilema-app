import 'environment_config.dart';

/// App配置
/// 
/// 提供向后兼容的配置访问方式，内部使用 [EnvironmentConfig]
/// 
/// 建议使用 [EnvironmentConfig.current] 来获取当前环境的配置
class AppConfig {
  /// API基础URL
  static String get baseUrl => EnvironmentConfig.current.baseUrl;

  /// 连接超时时间（毫秒）
  static int get connectTimeout => EnvironmentConfig.current.connectTimeout;

  /// 接收超时时间（毫秒）
  static int get receiveTimeout => EnvironmentConfig.current.receiveTimeout;

  /// 是否启用调试模式
  static bool get isDebugMode => EnvironmentConfig.current.enableDebugLogs;

  /// App版本
  static String get appVersion => EnvironmentConfig.current.appVersion;

  /// 发送超时时间（毫秒）
  static int get sendTimeout => EnvironmentConfig.current.sendTimeout;

  /// 是否启用错误报告
  static bool get enableErrorReporting => EnvironmentConfig.current.enableErrorReporting;

  /// 当前环境
  static Environment get environment => EnvironmentConfig.current.environment;
}
