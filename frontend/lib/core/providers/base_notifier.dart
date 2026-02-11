import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/base_state.dart';

/// 基础状态通知器
/// 所有状态管理器都应继承此类以获得通用的状态管理功能
mixin BaseNotifierMixin<S extends BaseState> on Notifier<S> {
  /// 加载数据
  /// 子类必须实现此方法
  Future<void> load();

  /// 刷新数据
  /// 调用 load 方法重新加载数据
  Future<void> refresh() async {
    await load();
  }

  /// 清除错误消息
  void clearError() {
    if (state.errorMessage != null) {
      state = state.copyWith(errorMessage: null) as S;
    }
  }
}
