library;

import 'package:qilema_app/core/models/emergency_models.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

export 'package:qilema_app/core/models/emergency_models.dart';

/// 急救资源API服务
class EmergencyApi {
  static final ApiClient _apiClient = ApiClient();

  /// 获取附近的AED设备
  static Future<List<AedDevice>> getNearbyAeds({
    required double latitude,
    required double longitude,
    double radius = 5000, // 默认5公里
  }) async {
    try {
      final response = await _apiClient.get(
        '/emergency/aeds',
        queryParameters: {
          'latitude': latitude,
          'longitude': longitude,
          'radius': radius,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((json) => AedDevice.fromJson(json)).toList();
      }
      return _getMockAeds(latitude, longitude);
    } catch (e) {
      Logger.e('获取AED设备失败', error: e);
      return _getMockAeds(latitude, longitude);
    }
  }

  /// 获取附近的医院
  static Future<List<Hospital>> getNearbyHospitals({
    required double latitude,
    required double longitude,
    double radius = 10000, // 默认10公里
    String? level, // 医院等级筛选
    bool hasEmergencyOnly = false,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        if (level != null) 'level': level,
        if (hasEmergencyOnly) 'has_emergency': true,
      };

      final response = await _apiClient.get(
        '/emergency/hospitals',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((json) => Hospital.fromJson(json)).toList();
      }
      return _getMockHospitals(latitude, longitude);
    } catch (e) {
      Logger.e('获取医院列表失败', error: e);
      return _getMockHospitals(latitude, longitude);
    }
  }

  /// 模拟AED数据
  static List<AedDevice> _getMockAeds(double userLat, double userLng) {
    return [
      AedDevice(
        id: 'aed_001',
        name: '某大厦AED',
        address: '某路1号大厦1楼大厅',
        latitude: userLat + 0.001,
        longitude: userLng + 0.001,
        distance: 150,
        phone: '021-12345678',
        isAvailable: true,
        operatingHours: '24小时',
      ),
      AedDevice(
        id: 'aed_002',
        name: '某商场AED',
        address: '某路2号商场服务台',
        latitude: userLat - 0.002,
        longitude: userLng + 0.0015,
        distance: 350,
        phone: '021-87654321',
        isAvailable: true,
        operatingHours: '10:00-22:00',
      ),
    ];
  }

  /// 模拟医院数据
  static List<Hospital> _getMockHospitals(double userLat, double userLng) {
    return [
      Hospital(
        id: 'hospital_001',
        name: '某三甲医院',
        address: '某路100号',
        latitude: userLat + 0.005,
        longitude: userLng + 0.003,
        distance: 1200,
        phone: '021-11111111',
        level: '3A',
        hasEmergency: true,
        departments: ['急诊科', '心内科', '神经内科', '外科'],
      ),
      Hospital(
        id: 'hospital_002',
        name: '某二甲医院',
        address: '某路200号',
        latitude: userLat - 0.004,
        longitude: userLng + 0.002,
        distance: 2100,
        phone: '021-22222222',
        level: '2A',
        hasEmergency: true,
        departments: ['急诊科', '内科', '外科'],
      ),
    ];
  }
}
