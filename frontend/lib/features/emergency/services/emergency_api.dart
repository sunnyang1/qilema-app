import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// AED设备信息
class AedDevice {
  final String id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final double distance;
  final String? phone;
  final bool isAvailable;
  final String? operatingHours;

  AedDevice({
    required this.id,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.distance,
    this.phone,
    this.isAvailable = true,
    this.operatingHours,
  });

  factory AedDevice.fromJson(Map<String, dynamic> json) {
    return AedDevice(
      id: json['id'] as String,
      name: json['name'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      distance: (json['distance'] as num).toDouble(),
      phone: json['phone'] as String?,
      isAvailable: json['is_available'] as bool? ?? true,
      operatingHours: json['operating_hours'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'distance': distance,
      'phone': phone,
      'is_available': isAvailable,
      'operating_hours': operatingHours,
    };
  }
}

/// 医院信息
class Hospital {
  final String id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final double distance;
  final String? phone;
  final String level;
  final bool hasEmergency;
  final List<String> departments;

  Hospital({
    required this.id,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.distance,
    this.phone,
    required this.level,
    this.hasEmergency = true,
    this.departments = const [],
  });

  factory Hospital.fromJson(Map<String, dynamic> json) {
    return Hospital(
      id: json['id'] as String,
      name: json['name'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      distance: (json['distance'] as num).toDouble(),
      phone: json['phone'] as String?,
      level: json['level'] as String,
      hasEmergency: json['has_emergency'] as bool? ?? true,
      departments: (json['departments'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'distance': distance,
      'phone': phone,
      'level': level,
      'has_emergency': hasEmergency,
      'departments': departments,
    };
  }
}

/// 急救资源API服务
class EmergencyApi {
  static const String _baseUrl = '/api/v1/emergency';

  /// 获取附近的AED设备
  static Future<List<AedDevice>> getNearbyAeds({
    required double latitude,
    required double longitude,
    double radius = 5000, // 默认5公里
  }) async {
    try {
      final response = await ApiClient().get(
        '$_baseUrl/aeds',
        queryParameters: {
          'lat': latitude,
          'lng': longitude,
          'radius': radius,
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => AedDevice.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      Logger.e('获取附近AED失败', error: e);
      return _getMockAeds(latitude, longitude);
    }
  }

  /// 获取附近的医院
  static Future<List<Hospital>> getNearbyHospitals({
    required double latitude,
    required double longitude,
    double radius = 10000, // 默认10公里
  }) async {
    try {
      final response = await ApiClient().get(
        '$_baseUrl/hospitals',
        queryParameters: {
          'lat': latitude,
          'lng': longitude,
          'radius': radius,
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => Hospital.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      Logger.e('获取附近医院失败', error: e);
      return _getMockHospitals(latitude, longitude);
    }
  }

  /// 获取AED详情
  static Future<AedDevice?> getAedDetail(String aedId) async {
    try {
      final response = await ApiClient().get('$_baseUrl/aeds/$aedId');

      if (response.statusCode == 200) {
        return AedDevice.fromJson(response.data['data']);
      }
      return null;
    } catch (e) {
      Logger.e('获取AED详情失败', error: e);
      return null;
    }
  }

  /// 获取医院详情
  static Future<Hospital?> getHospitalDetail(String hospitalId) async {
    try {
      final response = await ApiClient().get('$_baseUrl/hospitals/$hospitalId');

      if (response.statusCode == 200) {
        return Hospital.fromJson(response.data['data']);
      }
      return null;
    } catch (e) {
      Logger.e('获取医院详情失败', error: e);
      return null;
    }
  }

  /// 模拟AED数据
  static List<AedDevice> _getMockAeds(double lat, double lng) {
    return [
      AedDevice(
        id: 'aed_001',
        name: '市民中心AED',
        address: '市民中心一楼大厅服务台旁',
        latitude: lat + 0.001,
        longitude: lng + 0.001,
        distance: 150,
        phone: '010-12345678',
        isAvailable: true,
        operatingHours: '08:00-18:00',
      ),
      AedDevice(
        id: 'aed_002',
        name: '购物中心AED',
        address: '购物中心B1层服务台',
        latitude: lat + 0.002,
        longitude: lng - 0.001,
        distance: 320,
        phone: '010-87654321',
        isAvailable: true,
        operatingHours: '10:00-22:00',
      ),
      AedDevice(
        id: 'aed_003',
        name: '社区医院AED',
        address: '社区卫生服务中心急诊室',
        latitude: lat - 0.001,
        longitude: lng + 0.002,
        distance: 480,
        phone: '010-11112222',
        isAvailable: true,
        operatingHours: '24小时',
      ),
      AedDevice(
        id: 'aed_004',
        name: '体育馆AED',
        address: '市体育馆主入口旁',
        latitude: lat - 0.002,
        longitude: lng - 0.001,
        distance: 620,
        phone: '010-33334444',
        isAvailable: false,
        operatingHours: '06:00-22:00',
      ),
      AedDevice(
        id: 'aed_005',
        name: '地铁站AED',
        address: '地铁1号线人民广场站站台',
        latitude: lat + 0.003,
        longitude: lng + 0.002,
        distance: 890,
        isAvailable: true,
        operatingHours: '05:30-23:30',
      ),
    ];
  }

  /// 模拟医院数据
  static List<Hospital> _getMockHospitals(double lat, double lng) {
    return [
      Hospital(
        id: 'hosp_001',
        name: '市第一人民医院',
        address: '中山路123号',
        latitude: lat + 0.003,
        longitude: lng + 0.002,
        distance: 1200,
        phone: '010-66668888',
        level: '三级甲等',
        hasEmergency: true,
        departments: ['急诊科', '心内科', '神经内科', '骨科'],
      ),
      Hospital(
        id: 'hosp_002',
        name: '市中心医院',
        address: '解放路456号',
        latitude: lat - 0.002,
        longitude: lng + 0.003,
        distance: 2100,
        phone: '010-99990000',
        level: '三级乙等',
        hasEmergency: true,
        departments: ['急诊科', '普外科', '妇产科'],
      ),
      Hospital(
        id: 'hosp_003',
        name: '区人民医院',
        address: '建设路789号',
        latitude: lat + 0.004,
        longitude: lng - 0.002,
        distance: 3500,
        phone: '010-77775555',
        level: '二级甲等',
        hasEmergency: true,
        departments: ['急诊科', '内科', '儿科'],
      ),
      Hospital(
        id: 'hosp_004',
        name: '市中医院',
        address: '文化路321号',
        latitude: lat - 0.003,
        longitude: lng - 0.003,
        distance: 4200,
        phone: '010-44446666',
        level: '三级甲等',
        hasEmergency: true,
        departments: ['急诊科', '中医科', '针灸科'],
      ),
      Hospital(
        id: 'hosp_005',
        name: '社区卫生服务中心',
        address: '健康街100号',
        latitude: lat + 0.001,
        longitude: lng - 0.004,
        distance: 2800,
        phone: '010-22223333',
        level: '一级',
        hasEmergency: false,
        departments: ['全科', '预防保健科'],
      ),
    ];
  }
}
