import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/auth/services/auth_api.dart';
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
class AuthNotifier extends Notifier<AuthState> {
  late final AuthApi _authApi;

  @override
  AuthState build() {
    _authApi = AuthApi();
    _init();
    return const AuthState();
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
    state = const AuthState(status: AuthStatus.loading);
    try {
      // 1. 调用注册 API
      final registerData = await _authApi.register(phone, password, nickname);
      final userId = registerData['user_id'] as String;

      // 2. 注册成功后自动登录
      final loginData = await _authApi.login(phone, password);
      final accessToken = loginData['access_token'] as String;
      final refreshToken = loginData['refresh_token'] as String;

      // 3. 保存登录信息
      await AuthService.saveAuthData(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userId: userId,
      );

      // 4. 更新状态
      state = AuthState(
        status: AuthStatus.authenticated,
        userId: userId,
      );
    } catch (e) {
      state = const AuthState(status: AuthStatus.unauthenticated);
      rethrow;
    }
  }

  /// 登出
  Future<void> logout() async {
    await AuthService.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

/// 认证状态Provider
final authProvider = NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);
