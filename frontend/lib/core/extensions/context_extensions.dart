library;

import 'package:flutter/material.dart';

/// BuildContext 扩展方法
extension ContextExtensions on BuildContext {
  /// 获取主题
  ThemeData get theme => Theme.of(this);

  /// 获取颜色方案
  ColorScheme get colorScheme => Theme.of(this).colorScheme;

  /// 获取文本主题
  TextTheme get textTheme => Theme.of(this).textTheme;

  /// 获取媒体查询数据
  MediaQueryData get mediaQuery => MediaQuery.of(this);

  /// 获取屏幕宽度
  double get screenWidth => MediaQuery.of(this).size.width;

  /// 获取屏幕高度
  double get screenHeight => MediaQuery.of(this).size.height;

  /// 获取屏幕最短边
  double get shortestSide => MediaQuery.of(this).size.shortestSide;

  /// 判断是否为平板设备（最短边 >= 600）
  bool get isTablet => shortestSide >= 600;

  /// 判断是否为手机设备
  bool get isPhone => !isTablet;

  /// 获取设备像素比
  double get devicePixelRatio => MediaQuery.of(this).devicePixelRatio;

  /// 获取状态栏高度
  double get statusBarHeight => MediaQuery.of(this).padding.top;

  /// 获取底部安全区域高度
  double get bottomSafeArea => MediaQuery.of(this).padding.bottom;

  /// 显示SnackBar
  void showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? colorScheme.error : colorScheme.primary,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  /// 隐藏当前SnackBar
  void hideSnackBar() {
    ScaffoldMessenger.of(this).hideCurrentSnackBar();
  }

  /// 显示加载对话框
  void showLoadingDialog({String? message}) {
    showDialog(
      context: this,
      barrierDismissible: false,
      builder: (context) => PopScope(
        canPop: false,
        child: AlertDialog(
          content: Row(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(width: 16),
              Text(message ?? '加载中...'),
            ],
          ),
        ),
      ),
    );
  }

  /// 关闭对话框
  void closeDialog() {
    if (Navigator.canPop(this)) {
      Navigator.of(this).pop();
    }
  }
}
