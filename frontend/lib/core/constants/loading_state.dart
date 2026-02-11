/// 加载状态枚举
enum LoadingState {
  /// 初始状态
  initial,

  /// 加载中
  loading,

  /// 加载成功
  loaded,

  /// 加载失败
  error;

  /// 是否正在加载
  bool get isLoading => this == LoadingState.loading;

  /// 是否加载成功
  bool get isLoaded => this == LoadingState.loaded;

  /// 是否有错误
  bool get hasError => this == LoadingState.error;

  /// 是否为初始状态
  bool get isInitial => this == LoadingState.initial;
}
