library;

/// 应用相关常量
class AppConstants {
  AppConstants._();

  /// 应用名称
  static const String appName = '起了吗';

  /// 应用英文名称
  static const String appNameEn = 'QiLeMa';

  /// 应用版本
  static const String appVersion = '1.0.0';

  /// 应用构建号
  static const String buildNumber = '1';

  /// 版权信息
  static const String copyright = '© 2024 QiLeMa. All rights reserved.';

  /// 隐私政策URL
  static const String privacyPolicyUrl = 'https://qilema.com/privacy';

  /// 服务条款URL
  static const String termsOfServiceUrl = 'https://qilema.com/terms';

  /// 帮助中心URL
  static const String helpCenterUrl = 'https://qilema.com/help';
}

/// API相关常量
class ApiConstants {
  ApiConstants._();

  /// 默认连接超时时间（毫秒）
  static const int defaultConnectTimeout = 10000;

  /// 默认接收超时时间（毫秒）
  static const int defaultReceiveTimeout = 10000;

  /// 默认发送超时时间（毫秒）
  static const int defaultSendTimeout = 10000;

  /// 最大重试次数
  static const int maxRetries = 3;

  /// 重试延迟（毫秒）
  static const int retryDelay = 1000;

  /// 分页默认每页数量
  static const int defaultPageSize = 20;

  /// 分页最大每页数量
  static const int maxPageSize = 100;
}

/// UI相关常量
class UIConstants {
  UIConstants._();

  // ==================== 间距 ====================
  
  /// 极小间距
  static const double spacingXSmall = 4.0;

  /// 小间距
  static const double spacingSmall = 8.0;

  /// 中间距
  static const double spacingMedium = 16.0;

  /// 大间距
  static const double spacingLarge = 24.0;

  /// 极大间距
  static const double spacingXLarge = 32.0;

  // ==================== 圆角 ====================
  
  /// 小圆角
  static const double radiusSmall = 4.0;

  /// 中圆角
  static const double radiusMedium = 8.0;

  /// 大圆角
  static const double radiusLarge = 12.0;

  /// 极大圆角
  static const double radiusXLarge = 16.0;

  /// 圆形
  static const double radiusCircular = 9999.0;

  // ==================== 字体大小 ====================
  
  /// 极小字体
  static const double fontSizeXSmall = 10.0;

  /// 小字体
  static const double fontSizeSmall = 12.0;

  /// 中字体
  static const double fontSizeMedium = 14.0;

  /// 大字体
  static const double fontSizeLarge = 16.0;

  /// 极大字体
  static const double fontSizeXLarge = 18.0;

  /// 标题字体
  static const double fontSizeTitle = 20.0;

  /// 大标题字体
  static const double fontSizeHeadline = 24.0;

  /// 显示字体
  static const double fontSizeDisplay = 32.0;

  // ==================== 图标大小 ====================
  
  /// 小图标
  static const double iconSizeSmall = 16.0;

  /// 中图标
  static const double iconSizeMedium = 24.0;

  /// 大图标
  static const double iconSizeLarge = 32.0;

  /// 极大图标
  static const double iconSizeXLarge = 48.0;

  // ==================== 按钮 ====================
  
  /// 按钮最小高度
  static const double buttonMinHeight = 44.0;

  /// 按钮水平内边距
  static const double buttonHorizontalPadding = 24.0;

  // ==================== 卡片 ====================
  
  /// 卡片内边距
  static const double cardPadding = 16.0;

  /// 卡片阴影高度
  static const double cardElevation = 2.0;

  // ==================== 输入框 ====================
  
  /// 输入框高度
  static const double inputFieldHeight = 48.0;

  /// 输入框内边距
  static const double inputFieldPadding = 12.0;

  // ==================== 动画时长 ====================
  
  /// 短动画时长
  static const Duration animationShort = Duration(milliseconds: 150);

  /// 中动画时长
  static const Duration animationMedium = Duration(milliseconds: 300);

  /// 长动画时长
  static const Duration animationLong = Duration(milliseconds: 500);
}

/// 存储相关常量
class StorageConstants {
  StorageConstants._();

  /// SharedPreferences 键：用户Token
  static const String keyAuthToken = 'auth_token';

  /// SharedPreferences 键：刷新Token
  static const String keyRefreshToken = 'refresh_token';

  /// SharedPreferences 键：用户信息
  static const String keyUserInfo = 'user_info';

  /// SharedPreferences 键：首次启动
  static const String keyFirstLaunch = 'first_launch';

  /// SharedPreferences 键：主题模式
  static const String keyThemeMode = 'theme_mode';

  /// SharedPreferences 键：语言
  static const String keyLocale = 'locale';

  /// SharedPreferences 键：最后登录时间
  static const String keyLastLoginTime = 'last_login_time';

  /// SharedPreferences 键：通知设置
  static const String keyNotificationSettings = 'notification_settings';
}

/// 错误消息常量
class ErrorMessages {
  ErrorMessages._();

  /// 通用错误
  static const String genericError = '操作失败，请稍后重试';

  /// 网络错误
  static const String networkError = '网络连接失败，请检查网络设置';

  /// 超时错误
  static const String timeoutError = '连接超时，请稍后重试';

  /// 服务器错误
  static const String serverError = '服务器错误，请稍后重试';

  /// 未授权错误
  static const String unauthorizedError = '登录已过期，请重新登录';

  /// 未找到错误
  static const String notFoundError = '请求的资源不存在';

  /// 验证错误
  static const String validationError = '输入信息有误，请检查';

  /// 空数据错误
  static const String emptyDataError = '暂无数据';

  /// 加载失败
  static const String loadFailed = '加载失败，请下拉刷新重试';

  /// 保存失败
  static const String saveFailed = '保存失败，请稍后重试';

  /// 删除失败
  static const String deleteFailed = '删除失败，请稍后重试';
}

/// 验证相关常量
class ValidationConstants {
  ValidationConstants._();

  /// 手机号正则表达式
  static final RegExp phoneRegExp = RegExp(r'^1[3-9]\d{9}$');

  /// 邮箱正则表达式
  static final RegExp emailRegExp = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );

  /// 密码最小长度
  static const int passwordMinLength = 6;

  /// 密码最大长度
  static const int passwordMaxLength = 20;

  /// 昵称最小长度
  static const int nicknameMinLength = 2;

  /// 昵称最大长度
  static const int nicknameMaxLength = 20;

  /// 验证码长度
  static const int verificationCodeLength = 6;
}

/// 功能模块相关常量
class FeatureConstants {
  FeatureConstants._();

  /// SOS长按时间（毫秒）
  static const int sosLongPressDuration = 3000;

  /// 位置更新间隔（毫秒）
  static const int locationUpdateInterval = 5000;

  /// 签到最大连续天数
  static const int maxStreakDays = 365;

  /// 用药提醒最大提前时间（分钟）
  static const int maxMedicationReminderAdvance = 60;

  /// 蓝牙扫描超时（秒）
  static const int bluetoothScanTimeout = 30;

  /// 默认紧急联系人数量上限
  static const int maxEmergencyContacts = 5;

  /// 默认医院搜索半径（公里）
  static const double defaultHospitalSearchRadius = 10.0;

  /// 默认AED搜索半径（公里）
  static const double defaultAedSearchRadius = 5.0;
}
