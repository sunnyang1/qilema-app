import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/shared/services/auth_service.dart';

/// 认证状态
enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
}

/// 认证状态类
class AuthState {
  final AuthStatus status;
  final String? userId;

  const AuthState({
    this.status = AuthStatus.initial,
    this.userId,
  });

  AuthState copyWith({
    AuthStatus? status,
    String? userId,
  }) {
    return AuthState(
      status: status ?? this.status,
      userId: userId ?? this.userId,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isUnauthenticated => status == AuthStatus.unauthenticated;
  bool get isLoading => status == AuthStatus.loading;
}

/// 认证状态管理器
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(const AuthState()) {
    _init();
  }

  /// 初始化检查登录状态
  Future<void> _init() async {
    state = state.copyWith(status: AuthStatus.loading);
    final isLoggedIn = await AuthService.isLoggedIn();
    final userId = await AuthService.getUserId();

    if (isLoggedIn) {
      state = AuthState(
        status: AuthStatus.authenticated,
        userId: userId,
      );
    } else {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  /// 登录
  Future<void> login(String phone, String password) async {
    state = const AuthState(status: AuthStatus.loading);
    // 登录逻辑在 LoginPage 中调用 AuthApi 直接处理
    // 这里只是状态变更，实际逻辑由 UI 层调用 AuthApi 完成
  }

  /// 注册
  Future<void> register(String phone, String password, String nickname) async {
    // TODO: 实现注册逻辑
    state = const AuthState(status: AuthStatus.loading);
    // 注册成功后
    state = const AuthState(status: AuthStatus.authenticated);
  }

  /// 登出
  Future<void> logout() async {
    await AuthService.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

/// 认证状态Provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
