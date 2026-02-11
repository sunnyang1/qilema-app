library;

import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/devices_models.dart';

void main() {
  group('Device', () {
    test('should create with all fields', () {
      final device = Device(
        deviceId: '1',
        deviceName: 'Test Device',
        deviceType: 'smart_watch',
        macAddress: 'AA:BB:CC:DD:EE:FF',
        isConnected: true,
        batteryLevel: 80,
        lastSyncTime: '2024-01-01',
        settings: {'key': 'value'},
      );
      expect(device.deviceId, '1');
      expect(device.deviceName, 'Test Device');
      expect(device.deviceType, 'smart_watch');
      expect(device.macAddress, 'AA:BB:CC:DD:EE:FF');
      expect(device.isConnected, true);
      expect(device.batteryLevel, 80);
      expect(device.lastSyncTime, '2024-01-01');
      expect(device.settings, {'key': 'value'});
    });

    test('should use defaults for optional fields', () {
      final device = Device(
        deviceId: '1',
        deviceName: 'Test',
        deviceType: 'smart_watch',
      );
      expect(device.isConnected, false);
      expect(device.macAddress, null);
    });

    test('should parse from JSON', () {
      final json = {
        'device_id': '1',
        'device_name': 'Test',
        'device_type': 'smart_watch',
        'mac_address': 'AA:BB',
        'is_connected': true,
        'battery_level': 80,
      };
      final device = Device.fromJson(json);
      expect(device.deviceId, '1');
      expect(device.deviceName, 'Test');
      expect(device.deviceType, 'smart_watch');
    });

    test('should serialize to JSON', () {
      final device = Device(
        deviceId: '1',
        deviceName: 'Test',
        deviceType: 'smart_watch',
      );
      final json = device.toJson();
      expect(json['device_name'], 'Test');
      expect(json.containsKey('device_id'), false);
    });

    test('copyWith should update fields', () {
      final device = Device(deviceId: '1', deviceName: 'Test', deviceType: 'smart_watch');
      final updated = device.copyWith(deviceName: 'Updated');
      expect(updated.deviceName, 'Updated');
      expect(updated.deviceId, '1');
    });

    test('typeDisplayName should return correct name', () {
      expect(Device(deviceId: '1', deviceName: 'Test', deviceType: 'smart_watch').typeDisplayName, '智能手表');
      expect(Device(deviceId: '1', deviceName: 'Test', deviceType: 'blood_pressure_monitor').typeDisplayName, '血压计');
      expect(Device(deviceId: '1', deviceName: 'Test', deviceType: 'unknown').typeDisplayName, '智能设备');
    });

    test('iconName should return correct icon', () {
      expect(Device(deviceId: '1', deviceName: 'Test', deviceType: 'smart_watch').iconName, 'watch');
      expect(Device(deviceId: '1', deviceName: 'Test', deviceType: 'unknown').iconName, 'devices');
    });

    test('equality should work correctly', () {
      final d1 = Device(deviceId: '1', deviceName: 'Test', deviceType: 'smart_watch');
      final d2 = Device(deviceId: '1', deviceName: 'Test', deviceType: 'smart_watch');
      expect(d1, d2);
    });
  });

  group('DeviceDataPoint', () {
    test('should parse from JSON', () {
      final json = {'data_type': 'heart_rate', 'value': 72.5, 'unit': 'bpm', 'timestamp': '2024-01-01'};
      final point = DeviceDataPoint.fromJson(json);
      expect(point.dataType, 'heart_rate');
      expect(point.value, 72.5);
      expect(point.unit, 'bpm');
    });

    test('equality should work', () {
      final p1 = DeviceDataPoint(dataType: 'hr', value: 70, timestamp: 't1');
      final p2 = DeviceDataPoint(dataType: 'hr', value: 70, timestamp: 't1');
      expect(p1, p2);
    });
  });
}
