import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 签到API服务
class SigninApi {
  final ApiClient _apiClient = ApiClient();

  /// 每日签到
  Future<Map<String, dynamic>> checkIn() async {
    try {
      final response = await _apiClient.post('/checkin');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'checkin_id': data['checkin_id'],
          'check_in_time': data['check_in_time'],
          'status': data['status'],
          'streak_days': data['streak_days'],
        };
      }

      throw Exception('签到失败');
    } catch (e) {
      Logger.e('签到API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取签到状态
  Future<Map<String, dynamic>> getStatus() async {
    try {
      final response = await _apiClient.get('/checkin/status');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'today_checked_in': data['today_checked_in'],
          'last_checkin_time': data['last_checkin_time'],
          'streak_days': data['streak_days'],
          'next_checkin_deadline': data['next_checkin_deadline'],
        };
      }

      throw Exception('获取签到状态失败');
    } catch (e) {
      Logger.e('获取签到状态API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取签到历史
  Future<Map<String, dynamic>> getHistory({
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiClient.get(
        '/checkin/history',
        queryParameters: {'page': page, 'limit': limit},
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'total': data['total'],
          'page': data['page'],
          'limit': data['limit'],
          'items': data['items'],
        };
      }

      throw Exception('获取签到历史失败');
    } catch (e) {
      Logger.e('获取签到历史API调用失败', error: e);
      rethrow;
    }
  }
}
