import 'package:dio/dio.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 认证API服务
class AuthApi {
  final ApiClient _apiClient = ApiClient();

  /// 用户登录
  /// 返回访问令牌和刷新令牌
  Future<Map<String, dynamic>> login(String phone, String password) async {
    try {
      final response = await _apiClient.post(
        '/auth/login',
        data: {
          'username': phone,
          'password': password,
        },
        options: Options(
          contentType: Headers.formUrlEncodedContentType,
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'access_token': data['access_token'],
          'refresh_token': data['refresh_token'] ?? data['access_token'],
          'user_id': data['user_id'],
        };
      }

      throw Exception('登录失败');
    } catch (e) {
      Logger.e('登录API调用失败', error: e);
      rethrow;
    }
  }

  /// 用户注册
  Future<Map<String, dynamic>> register(
    String phone,
    String password,
    String nickname,
  ) async {
    try {
      final response = await _apiClient.post(
        '/auth/register',
        data: {
          'phone': phone,
          'password': password,
          'nickname': nickname,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'user_id': data['user_id'],
          'phone': data['phone'],
          'nickname': data['nickname'],
        };
      }

      throw Exception('注册失败');
    } catch (e) {
      Logger.e('注册API调用失败', error: e);
      rethrow;
    }
  }
}
