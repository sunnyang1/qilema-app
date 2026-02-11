library;

/// 环境枚举
enum Environment {
  /// 开发环境
  dev,
  
  /// 测试环境
  staging,
  
  /// 生产环境
  prod,
}

/// 环境配置扩展
extension EnvironmentExtension on Environment {
  /// 环境名称
  String get name {
    switch (this) {
      case Environment.dev:
        return 'development';
      case Environment.staging:
        return 'staging';
      case Environment.prod:
        return 'production';
    }
  }
  
  /// 是否是生产环境
  bool get isProduction => this == Environment.prod;
  
  /// 是否是开发环境
  bool get isDevelopment => this == Environment.dev;
  
  /// 是否是测试环境
  bool get isStaging => this == Environment.staging;
}

/// 环境配置类
/// 
/// 用于管理不同环境的配置参数，包括API基础URL、超时时间等
class EnvironmentConfig {
  /// 当前环境
  final Environment environment;
  
  /// API基础URL
  final String baseUrl;
  
  /// 连接超时时间（毫秒）
  final int connectTimeout;
  
  /// 接收超时时间（毫秒）
  final int receiveTimeout;
  
  /// 发送超时时间（毫秒）
  final int sendTimeout;
  
  /// 是否启用调试模式
  final bool enableDebugLogs;
  
  /// App版本
  final String appVersion;
  
  /// 是否启用错误报告
  final bool enableErrorReporting;

  const EnvironmentConfig._({
    required this.environment,
    required this.baseUrl,
    required this.connectTimeout,
    required this.receiveTimeout,
    required this.sendTimeout,
    required this.enableDebugLogs,
    required this.appVersion,
    required this.enableErrorReporting,
  });

  /// 开发环境配置
  static const EnvironmentConfig dev = EnvironmentConfig._(
    environment: Environment.dev,
    baseUrl: 'http://localhost:8000/api/v1',
    connectTimeout: 10000,
    receiveTimeout: 10000,
    sendTimeout: 10000,
    enableDebugLogs: true,
    appVersion: '1.0.0-dev',
    enableErrorReporting: false,
  );

  /// 测试环境配置
  static const EnvironmentConfig staging = EnvironmentConfig._(
    environment: Environment.staging,
    baseUrl: 'https://staging.qilema.com/api/v1',
    connectTimeout: 15000,
    receiveTimeout: 15000,
    sendTimeout: 15000,
    enableDebugLogs: true,
    appVersion: '1.0.0-staging',
    enableErrorReporting: true,
  );

  /// 生产环境配置
  static const EnvironmentConfig prod = EnvironmentConfig._(
    environment: Environment.prod,
    baseUrl: 'https://api.qilema.com/api/v1',
    connectTimeout: 15000,
    receiveTimeout: 15000,
    sendTimeout: 15000,
    enableDebugLogs: false,
    appVersion: '1.0.0',
    enableErrorReporting: true,
  );

  /// 获取当前环境配置
  /// 
  /// 可以通过设置 `ENVIRONMENT` 环境变量来指定环境
  /// 支持的值：'dev', 'development', 'staging', 'test', 'prod', 'production'
  /// 默认为开发环境
  static EnvironmentConfig get current {
    const String env = String.fromEnvironment('ENVIRONMENT', defaultValue: 'dev');
    return fromString(env);
  }

  /// 从字符串创建环境配置
  /// 
  /// 支持的值：
  /// - 'dev', 'development' -> 开发环境
  /// - 'staging', 'test' -> 测试环境
  /// - 'prod', 'production' -> 生产环境
  static EnvironmentConfig fromString(String env) {
    final lowerEnv = env.toLowerCase();
    switch (lowerEnv) {
      case 'dev':
      case 'development':
        return dev;
      case 'staging':
      case 'test':
        return staging;
      case 'prod':
      case 'production':
        return prod;
      default:
        return dev;
    }
  }

  /// 验证配置是否有效
  /// 
  /// 检查：
  /// - baseUrl 不能为空且必须是有效的URL格式
  /// - 超时时间必须大于0
  /// - appVersion 不能为空
  /// 
  /// 返回验证错误列表，如果为空则表示验证通过
  List<String> validate() {
    final errors = <String>[];

    // 验证 baseUrl
    if (baseUrl.isEmpty) {
      errors.add('baseUrl cannot be empty');
    } else {
      try {
        final uri = Uri.parse(baseUrl);
        if (!uri.isScheme('http') && !uri.isScheme('https')) {
          errors.add('baseUrl must use http or https scheme');
        }
      } catch (e) {
        errors.add('baseUrl is not a valid URL: $baseUrl');
      }
    }

    // 验证超时时间
    if (connectTimeout <= 0) {
      errors.add('connectTimeout must be greater than 0');
    }
    if (receiveTimeout <= 0) {
      errors.add('receiveTimeout must be greater than 0');
    }
    if (sendTimeout <= 0) {
      errors.add('sendTimeout must be greater than 0');
    }

    // 验证 appVersion
    if (appVersion.isEmpty) {
      errors.add('appVersion cannot be empty');
    }

    return errors;
  }

  /// 检查配置是否有效
  bool get isValid => validate().isEmpty;

  /// 创建配置的副本，可以覆盖部分属性
  EnvironmentConfig copyWith({
    Environment? environment,
    String? baseUrl,
    int? connectTimeout,
    int? receiveTimeout,
    int? sendTimeout,
    bool? enableDebugLogs,
    String? appVersion,
    bool? enableErrorReporting,
  }) {
    return EnvironmentConfig._(
      environment: environment ?? this.environment,
      baseUrl: baseUrl ?? this.baseUrl,
      connectTimeout: connectTimeout ?? this.connectTimeout,
      receiveTimeout: receiveTimeout ?? this.receiveTimeout,
      sendTimeout: sendTimeout ?? this.sendTimeout,
      enableDebugLogs: enableDebugLogs ?? this.enableDebugLogs,
      appVersion: appVersion ?? this.appVersion,
      enableErrorReporting: enableErrorReporting ?? this.enableErrorReporting,
    );
  }

  @override
  String toString() {
    return 'EnvironmentConfig('
        'environment: ${environment.name}, '
        'baseUrl: $baseUrl, '
        'connectTimeout: $connectTimeout, '
        'receiveTimeout: $receiveTimeout, '
        'sendTimeout: $sendTimeout, '
        'enableDebugLogs: $enableDebugLogs, '
        'appVersion: $appVersion, '
        'enableErrorReporting: $enableErrorReporting'
        ')';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is EnvironmentConfig &&
        other.environment == environment &&
        other.baseUrl == baseUrl &&
        other.connectTimeout == connectTimeout &&
        other.receiveTimeout == receiveTimeout &&
        other.sendTimeout == sendTimeout &&
        other.enableDebugLogs == enableDebugLogs &&
        other.appVersion == appVersion &&
        other.enableErrorReporting == enableErrorReporting;
  }

  @override
  int get hashCode {
    return Object.hash(
      environment,
      baseUrl,
      connectTimeout,
      receiveTimeout,
      sendTimeout,
      enableDebugLogs,
      appVersion,
      enableErrorReporting,
    );
  }
}
