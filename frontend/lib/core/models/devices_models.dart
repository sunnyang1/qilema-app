library;

import 'package:equatable/equatable.dart';

/// 设备数据模型
class Device extends Equatable {
  final String deviceId;
  final String deviceName;
  final String deviceType;
  final String? macAddress;
  final bool isConnected;
  final int? batteryLevel;
  final String? lastSyncTime;
  final Map<String, dynamic>? settings;

  const Device({
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    this.macAddress,
    this.isConnected = false,
    this.batteryLevel,
    this.lastSyncTime,
    this.settings,
  });

  @override
  List<Object?> get props => [
        deviceId,
        deviceName,
        deviceType,
        macAddress,
        isConnected,
        batteryLevel,
        lastSyncTime,
        settings,
      ];

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

  Device copyWith({
    String? deviceId,
    String? deviceName,
    String? deviceType,
    String? macAddress,
    bool? isConnected,
    int? batteryLevel,
    String? lastSyncTime,
    Map<String, dynamic>? settings,
  }) {
    return Device(
      deviceId: deviceId ?? this.deviceId,
      deviceName: deviceName ?? this.deviceName,
      deviceType: deviceType ?? this.deviceType,
      macAddress: macAddress ?? this.macAddress,
      isConnected: isConnected ?? this.isConnected,
      batteryLevel: batteryLevel ?? this.batteryLevel,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      settings: settings ?? this.settings,
    );
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
class DeviceDataPoint extends Equatable {
  final String dataType;
  final double value;
  final String? unit;
  final String timestamp;

  const DeviceDataPoint({
    required this.dataType,
    required this.value,
    this.unit,
    required this.timestamp,
  });

  @override
  List<Object?> get props => [dataType, value, unit, timestamp];

  factory DeviceDataPoint.fromJson(Map<String, dynamic> json) {
    return DeviceDataPoint(
      dataType: json['data_type'] ?? '',
      value: (json['value'] as num).toDouble(),
      unit: json['unit'],
      timestamp: json['timestamp'] ?? '',
    );
  }
}
