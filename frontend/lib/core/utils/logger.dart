import 'package:flutter/foundation.dart';

/// 日志工具类
class Logger {
  /// 打印信息
  static void i(String message) {
    if (kDebugMode) {
      print('[INFO] $message');
    }
  }

  /// 打印调试信息
  static void d(String message) {
    if (kDebugMode) {
      print('[DEBUG] $message');
    }
  }

  /// 打印警告信息
  static void w(String message) {
    if (kDebugMode) {
      print('[WARNING] $message');
    }
  }

  /// 打印错误信息
  static void e(String message, {Object? error, StackTrace? stackTrace}) {
    if (kDebugMode) {
      print('[ERROR] $message');
      if (error != null) {
        print(error);
      }
      if (stackTrace != null) {
        print(stackTrace);
      }
    }
  }
}
