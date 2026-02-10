import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// SOS API服务
class SosApi {
  final ApiClient _apiClient = ApiClient();

  /// 触发SOS求助
  Future<Map<String, dynamic>> triggerSOS({
    required double latitude,
    required double longitude,
  }) async {
    try {
      final response = await _apiClient.post('/sos', data: {
        'latitude': latitude,
        'longitude': longitude,
        'location_accuracy': 0.0,
      });

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'sos_id': data['sos_id'],
          'trigger_time': data['trigger_time'],
          'status': data['status'],
          'latitude': data['latitude'],
          'longitude': data['longitude'],
        };
      }

      throw Exception('触发SOS失败');
    } catch (e) {
      Logger.e('触发SOS API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取SOS状态
  Future<Map<String, dynamic>> getSOSStatus(String sosId) async {
    try {
      final response = await _apiClient.get('/sos/$sosId');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return {
          'sos_id': data['sos_id'],
          'status': data['status'],
          'trigger_time': data['trigger_time'],
          'latitude': data['latitude'],
          'longitude': data['longitude'],
          'rescue_time': data['rescue_time'],
          'cancel_time': data['cancel_time'],
        };
      }

      throw Exception('获取SOS状态失败');
    } catch (e) {
      Logger.e('获取SOS状态API调用失败', error: e);
      rethrow;
    }
  }

  /// 取消SOS
  Future<bool> cancelSOS(String sosId) async {
    try {
      final response = await _apiClient.delete('/sos/$sosId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('取消SOS失败');
    } catch (e) {
      Logger.e('取消SOS API调用失败', error: e);
      rethrow;
    }
  }
}
