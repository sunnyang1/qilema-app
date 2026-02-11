library;

/// String 扩展方法
extension StringExtensions on String {
  /// 限制字符串长度，超出部分显示省略号
  String truncate(int maxLength, {String ellipsis = '...'}) {
    if (length <= maxLength) return this;
    return '${substring(0, maxLength - ellipsis.length)}$ellipsis';
  }

  /// 将首字母大写
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }

  /// 将首字母小写
  String uncapitalize() {
    if (isEmpty) return this;
    return '${this[0].toLowerCase()}${substring(1)}';
  }

  /// 转换为驼峰命名（下划线分割）
  String toCamelCase() {
    if (isEmpty) return this;
    final words = split('_');
    if (words.length == 1) return uncapitalize();
    return words.first + words.skip(1).map((w) => w.capitalize()).join();
  }

  /// 转换为帕斯卡命名（下划线分割）
  String toPascalCase() {
    if (isEmpty) return this;
    return split('_').map((w) => w.capitalize()).join();
  }

  /// 转换为下划线命名
  String toSnakeCase() {
    if (isEmpty) return this;
    return replaceAllMapped(
      RegExp(r'[A-Z]'),
      (match) => '_${match.group(0)!.toLowerCase()}',
    ).replaceAll(RegExp(r'^_'), '');
  }

  /// 移除所有空白字符
  String removeWhitespace() => replaceAll(RegExp(r'\s+'), '');

  /// 判断是否为有效的手机号（中国大陆）
  bool get isValidPhoneNumber {
    final regex = RegExp(r'^1[3-9]\d{9}$');
    return regex.hasMatch(this);
  }

  /// 判断是否为有效的邮箱
  bool get isValidEmail {
    final regex = RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
    return regex.hasMatch(this);
  }

  /// 判断是否为有效的URL
  bool get isValidUrl {
    final regex = RegExp(r'^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(:\d+)?(/.*)?$');
    return regex.hasMatch(this);
  }

  /// 隐藏手机号中间四位
  String maskPhoneNumber() {
    if (length != 11) return this;
    return '${substring(0, 3)}****${substring(7)}';
  }

  /// 隐藏邮箱用户名部分
  String maskEmail() {
    if (!contains('@')) return this;
    final parts = split('@');
    final username = parts[0];
    final domain = parts[1];
    if (username.length <= 2) return this;
    return '${username.substring(0, 2)}***@$domain';
  }
}

/// Nullable String 扩展
extension NullableStringExtensions on String? {
  /// 判断是否为空或null
  bool get isNullOrEmpty => this == null || this!.isEmpty;

  /// 判断是否不为空且不为null
  bool get isNotNullOrEmpty => !isNullOrEmpty;

  /// 如果为空或null则返回默认值
  String orDefault(String defaultValue) => isNullOrEmpty ? defaultValue : this!;
}
