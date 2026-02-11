library;

import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/emergency_models.dart';

void main() {
  group('Emergency Models', () {
    group('AedDevice', () {
      test('should parse from JSON', () {
        final json = {
          'id': '1',
          'name': 'AED设备',
          'address': '某大厦1楼',
          'latitude': 31.0,
          'longitude': 121.0,
          'distance': 500.0,
          'is_available': true,
        };
        final aed = AedDevice.fromJson(json);
        expect(aed.name, 'AED设备');
        expect(aed.isAvailable, true);
        expect(aed.latitude, 31.0);
      });
    });

    group('Hospital', () {
      test('should parse from JSON', () {
        final json = {
          'id': '1',
          'name': '某医院',
          'address': '某路1号',
          'latitude': 31.0,
          'longitude': 121.0,
          'distance': 1000.0,
          'level': '3A',
          'has_emergency': true,
          'departments': ['内科', '外科'],
        };
        final hospital = Hospital.fromJson(json);
        expect(hospital.name, '某医院');
        expect(hospital.level, '3A');
        expect(hospital.levelDisplayName, '三级甲等');
        expect(hospital.departments, ['内科', '外科']);
      });

      test('levelDisplayName for 2A', () {
        final hospital = Hospital(
          id: '1',
          name: 'Test',
          address: 'Addr',
          latitude: 0,
          longitude: 0,
          distance: 0,
          level: '2A',
        );
        expect(hospital.levelDisplayName, '二级甲等');
      });
    });
  });
}
