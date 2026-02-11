library;

import 'package:equatable/equatable.dart';

/// AED设备信息
class AedDevice extends Equatable {
  final String id;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final double distance;
  final String? phone;
  final bool isAvailable;
  final String? operatingHours;

  const AedDevice({
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

  @override
  List<Object?> get props => [
        id, name, address, latitude, longitude,
        distance, phone, isAvailable, operatingHours,
      ];

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
class Hospital extends Equatable {
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

  const Hospital({
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

  @override
  List<Object?> get props => [
        id, name, address, latitude, longitude,
        distance, phone, level, hasEmergency, departments,
      ];

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

  /// 获取等级显示名称
  String get levelDisplayName {
    switch (level) {
      case '3A':
        return '三级甲等';
      case '2A':
        return '二级甲等';
      case '1A':
        return '一级甲等';
      default:
        return '综合医院';
    }
  }
}
