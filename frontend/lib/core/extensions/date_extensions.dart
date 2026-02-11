library;

/// DateTime 扩展方法
extension DateExtensions on DateTime {
  /// 格式化为 yyyy-MM-dd
  String toDateString() {
    return '$year-${_twoDigits(month)}-${_twoDigits(day)}';
  }

  /// 格式化为 yyyy-MM-dd HH:mm
  String toDateTimeString() {
    return '$year-${_twoDigits(month)}-${_twoDigits(day)} ${_twoDigits(hour)}:${_twoDigits(minute)}';
  }

  /// 格式化为 yyyy-MM-dd HH:mm:ss
  String toDateTimeSecondsString() {
    return '$year-${_twoDigits(month)}-${_twoDigits(day)} ${_twoDigits(hour)}:${_twoDigits(minute)}:${_twoDigits(second)}';
  }

  /// 格式化为 HH:mm
  String toTimeString() {
    return '${_twoDigits(hour)}:${_twoDigits(minute)}';
  }

  /// 格式化为相对时间（如：刚刚、5分钟前、1小时前等）
  String toRelativeTime() {
    final now = DateTime.now();
    final difference = now.difference(this);

    if (difference.inSeconds < 60) {
      return '刚刚';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 30) {
      return '${difference.inDays}天前';
    } else if (difference.inDays < 365) {
      return '${difference.inDays ~/ 30}个月前';
    } else {
      return '${difference.inDays ~/ 365}年前';
    }
  }

  /// 是否为今天
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  /// 是否为昨天
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year && month == yesterday.month && day == yesterday.day;
  }

  /// 是否为明天
  bool get isTomorrow {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    return year == tomorrow.year && month == tomorrow.month && day == tomorrow.day;
  }

  /// 是否为本月
  bool get isThisMonth {
    final now = DateTime.now();
    return year == now.year && month == now.month;
  }

  /// 是否为今年
  bool get isThisYear {
    return year == DateTime.now().year;
  }

  /// 获取月份的第一天
  DateTime get firstDayOfMonth {
    return DateTime(year, month, 1);
  }

  /// 获取月份的最后一天
  DateTime get lastDayOfMonth {
    return DateTime(year, month + 1, 0);
  }

  /// 获取本周的第一天（周一）
  DateTime get firstDayOfWeek {
    final weekday = this.weekday;
    return subtract(Duration(days: weekday - 1));
  }

  /// 获取本周的最后一天（周日）
  DateTime get lastDayOfWeek {
    final weekday = this.weekday;
    return add(Duration(days: 7 - weekday));
  }

  /// 增加天数
  DateTime addDays(int days) => add(Duration(days: days));

  /// 增加月数
  DateTime addMonths(int months) {
    return DateTime(year, month + months, day, hour, minute, second);
  }

  /// 增加年数
  DateTime addYears(int years) {
    return DateTime(year + years, month, day, hour, minute, second);
  }

  /// 只保留日期部分（时间设为00:00:00）
  DateTime get dateOnly {
    return DateTime(year, month, day);
  }

  /// 获取年龄
  int get age {
    final now = DateTime.now();
    int age = now.year - year;
    if (now.month < month || (now.month == month && now.day < day)) {
      age--;
    }
    return age;
  }

  String _twoDigits(int n) {
    if (n >= 10) return '$n';
    return '0$n';
  }
}

/// Duration 扩展方法
extension DurationExtensions on Duration {
  /// 格式化为 HH:mm:ss
  String toHmsString() {
    final hours = inHours;
    final minutes = inMinutes.remainder(60);
    final seconds = inSeconds.remainder(60);
    
    if (hours > 0) {
      return '${_twoDigits(hours)}:${_twoDigits(minutes)}:${_twoDigits(seconds)}';
    }
    return '${_twoDigits(minutes)}:${_twoDigits(seconds)}';
  }

  /// 格式化为 mm:ss
  String toMsString() {
    final minutes = inMinutes.remainder(60);
    final seconds = inSeconds.remainder(60);
    return '${_twoDigits(minutes)}:${_twoDigits(seconds)}';
  }

  /// 格式化为中文描述
  String toChineseString() {
    if (inDays > 0) {
      return '$inDays天${inHours.remainder(24)}小时';
    } else if (inHours > 0) {
      return '$inHours小时${inMinutes.remainder(60)}分钟';
    } else if (inMinutes > 0) {
      return '$inMinutes分钟';
    } else {
      return '$inSeconds秒';
    }
  }

  String _twoDigits(int n) {
    if (n >= 10) return '$n';
    return '0$n';
  }
}
