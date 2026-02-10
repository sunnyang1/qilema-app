import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';
import 'package:qilema_app/shared/services/auth_service.dart';

/// 设备数据模型
class Device {
  final String deviceId;
  final String deviceName;
  final String deviceType;
  final String? macAddress;
  final bool isConnected;
  final int? batteryLevel;
  final String? lastSyncTime;
  final Map<String, dynamic>? settings;

  Device({
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    this.macAddress,
    this.isConnected = false,
    this.batteryLevel,
    this.lastSyncTime,
    this.settings,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      deviceId: json['device_id'] ?? '',
      deviceName: json['device_name'] ?? '',
      deviceType: json['device_type'] ?? 'unknown',
      macAddress: json['mac_address'],
      isConnected: json['is_connected'] == 1 || json['is_connected'] == true,
      batteryLevel: json['battery_level'] as int?,
      lastSyncTime: json['last_sync_time'],
      settings: json['settings'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_name': deviceName,
      'device_type': deviceType,
      'mac_address': macAddress,
      'settings': settings,
    };
  }

  /// 获取设备类型显示名称
  String get typeDisplayName {
    switch (deviceType) {
      case 'smart_watch':
        return '智能手表';
      case 'blood_pressure_monitor':
        return '血压计';
      case 'blood_glucose_meter':
        return '血糖仪';
      case 'heart_rate_monitor':
        return '心率监测器';
      case 'sleep_tracker':
        return '睡眠追踪器';
      default:
        return '智能设备';
    }
  }

  /// 获取设备图标
  String get iconName {
    switch (deviceType) {
      case 'smart_watch':
        return 'watch';
      case 'blood_pressure_monitor':
        return 'monitor_heart';
      case 'blood_glucose_meter':
        return 'medical_services';
      case 'heart_rate_monitor':
        return 'favorite';
      case 'sleep_tracker':
        return 'bedtime';
      default:
        return 'devices';
    }
  }
}

/// 设备数据点
class DeviceDataPoint {
  final String dataType;
  final double value;
  final String? unit;
  final String timestamp;

  DeviceDataPoint({
    required this.dataType,
    required this.value,
    this.unit,
    required this.timestamp,
  });

  factory DeviceDataPoint.fromJson(Map<String, dynamic> json) {
    return DeviceDataPoint(
      dataType: json['data_type'] ?? '',
      value: (json['value'] as num).toDouble(),
      unit: json['unit'],
      timestamp: json['timestamp'] ?? '',
    );
  }
}

/// 设备API服务
class DevicesApi {
  final ApiClient _apiClient = ApiClient();

  /// 获取当前用户ID
  Future<String> _getCurrentUserId() async {
    final userId = await AuthService.getUserId();
    if (userId == null || userId.isEmpty) {
      throw Exception('用户未登录');
    }
    return userId;
  }

  /// 获取设备列表
  Future<List<Device>> getDevices() async {
    try {
      final userId = await _getCurrentUserId();
      final response = await _apiClient.get('/devices?user_id=$userId');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        final items = data['items'] as List?;
        return items?.map((item) => Device.fromJson(item)).toList() ?? [];
      }

      throw Exception('获取设备列表失败');
    } catch (e) {
      Logger.e('获取设备列表API调用失败', error: e);
      rethrow;
    }
  }

  /// 绑定新设备
  Future<Device> bindDevice(Device device) async {
    try {
      final userId = await _getCurrentUserId();
      final response = await _apiClient.post(
        '/devices',
        data: {
          ...device.toJson(),
          'user_id': userId,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Device.fromJson(data);
      }

      throw Exception('绑定设备失败');
    } catch (e) {
      Logger.e('绑定设备API调用失败', error: e);
      rethrow;
    }
  }

  /// 解绑设备
  Future<bool> unbindDevice(String deviceId) async {
    try {
      final response = await _apiClient.delete('/devices/$deviceId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('解绑设备失败');
    } catch (e) {
      Logger.e('解绑设备API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取设备数据
  Future<List<DeviceDataPoint>> getDeviceData(
    String deviceId, {
    String? dataType,
    String? startTime,
    String? endTime,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        if (dataType != null) 'data_type': dataType,
        if (startTime != null) 'start_time': startTime,
        if (endTime != null) 'end_time': endTime,
      };

      final response = await _apiClient.get(
        '/devices/$deviceId/data',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      if (response.statusCode == 200) {
        final data = response.data['data'] as List?;
        return data?.map((item) => DeviceDataPoint.fromJson(item)).toList() ?? [];
      }

      throw Exception('获取设备数据失败');
    } catch (e) {
      Logger.e('获取设备数据API调用失败', error: e);
      rethrow;
    }
  }

  /// 扫描附近的蓝牙设备（模拟）
  Future<List<Device>> scanBluetoothDevices() async {
    // 模拟蓝牙扫描延迟
    await Future.delayed(const Duration(seconds: 2));

    // 返回模拟设备列表
    return [
      Device(
        deviceId: 'mock_001',
        deviceName: '小米手环 7',
        deviceType: 'smart_watch',
        macAddress: 'AA:BB:CC:DD:EE:01',
        batteryLevel: 85,
      ),
      Device(
        deviceId: 'mock_002',
        deviceName: '华为血压计',
        deviceType: 'blood_pressure_monitor',
        macAddress: 'AA:BB:CC:DD:EE:02',
        batteryLevel: 60,
      ),
      Device(
        deviceId: 'mock_003',
        deviceName: '欧姆龙血糖仪',
        deviceType: 'blood_glucose_meter',
        macAddress: 'AA:BB:CC:DD:EE:03',
        batteryLevel: 90,
      ),
    ];
  }
}
