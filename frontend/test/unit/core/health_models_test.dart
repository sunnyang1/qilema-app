library;

import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/health_models.dart';

void main() {
  group('Health Models', () {
    group('HealthRecord', () {
      test('should parse from JSON', () {
        final json = {'id': '1', 'user_id': '2', 'real_name': '张三', 'blood_type': 'A'};
        final record = HealthRecord.fromJson(json);
        expect(record.id, '1');
        expect(record.userId, '2');
        expect(record.realName, '张三');
        expect(record.bloodType, 'A');
      });

      test('equality should work', () {
        final r1 = HealthRecord(id: '1', userId: '2', realName: 'Test');
        final r2 = HealthRecord(id: '1', userId: '2', realName: 'Test');
        expect(r1, r2);
      });
    });

    group('MedicalHistory', () {
      test('should parse from JSON', () {
        final json = {
          'id': 1,
          'health_record_id': 2,
          'disease_name': '高血压',
          'is_chronic': true,
        };
        final history = MedicalHistory.fromJson(json);
        expect(history.id, 1);
        expect(history.diseaseName, '高血压');
        expect(history.isChronic, true);
      });
    });

    group('MedicationInfo', () {
      test('should parse from JSON', () {
        final json = {
          'id': 1,
          'health_record_id': 2,
          'drug_name': '阿司匹林',
          'is_current': true,
        };
        final med = MedicationInfo.fromJson(json);
        expect(med.drugName, '阿司匹林');
        expect(med.isCurrent, true);
      });
    });

    group('Allergy', () {
      test('should parse from JSON', () {
        final json = {
          'id': 1,
          'health_record_id': 2,
          'allergen': '花生',
          'allergic_reaction': '皮疹',
          'severity': '严重',
          'discovered_date': '2020-01-01',
        };
        final allergy = Allergy.fromJson(json);
        expect(allergy.allergen, '花生');
        expect(allergy.allergicReaction, '皮疹');
        expect(allergy.severity, '严重');
        expect(allergy.discoveredDate, '2020-01-01');
      });
    });
  });
}
