import 'package:equatable/equatable.dart';
import 'package:qilema_app/core/constants/loading_state.dart';

/// 基础状态类
/// 所有状态类都应继承此类以获得通用的状态管理功能
abstract base class BaseState extends Equatable {
  /// 加载状态
  final LoadingState status;

  /// 错误消息
  final String? errorMessage;

  const BaseState({
    this.status = LoadingState.initial,
    this.errorMessage,
  });

  /// 是否正在加载
  bool get isLoading => status.isLoading;

  /// 是否加载成功
  bool get isLoaded => status.isLoaded;

  /// 是否有错误
  bool get hasError => status.hasError;

  /// 是否为初始状态
  bool get isInitial => status.isInitial;

  /// 更新状态
  /// 子类必须实现此方法
  BaseState copyWith({
    LoadingState? status,
    String? errorMessage,
  });

  @override
  List<Object?> get props => [status, errorMessage];
}
