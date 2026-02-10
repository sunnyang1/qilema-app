import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 认证服务
class AuthService {
  static const String _tokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userIdKey = 'user_id';

  /// 保存访问令牌
  static Future<void> saveAccessToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    Logger.i('访问令牌已保存');
  }

  /// 获取访问令牌
  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// 保存刷新令牌
  static Future<void> saveRefreshToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_refreshTokenKey, token);
  }

  /// 获取刷新令牌
  static Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_refreshTokenKey);
  }

  /// 保存用户ID
  static Future<void> saveUserId(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userIdKey, userId);
  }

  /// 获取用户ID
  static Future<String?> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_userIdKey);
  }

  /// 清除所有认证信息
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_userIdKey);
    Logger.i('已清除所有认证信息');
  }

  /// 刷新Token
  static Future<bool> refreshToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) {
        Logger.w('刷新令牌不存在');
        return false;
      }

      final dio = Dio(BaseOptions(
        baseUrl: 'http://localhost:8000/api/v1',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Bearer $refreshToken',
        },
      ));

      final response = await dio.post('/auth/refresh');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        await saveAccessToken(data['access_token']);
        await saveRefreshToken(data['refresh_token']);
        Logger.i('Token刷新成功');
        return true;
      }

      return false;
    } catch (e) {
      Logger.e('Token刷新失败', error: e);
      return false;
    }
  }

  /// 检查是否已登录
  static Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  /// 保存完整的认证数据
  static Future<void> saveAuthData({
    required String accessToken,
    required String refreshToken,
    required String userId,
  }) async {
    await saveAccessToken(accessToken);
    await saveRefreshToken(refreshToken);
    await saveUserId(userId);
    Logger.i('认证数据已保存');
  }
}
