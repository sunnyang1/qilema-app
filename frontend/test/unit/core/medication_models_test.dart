library;

import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/medication_models.dart';

void main() {
  group('Medication Models', () {
    group('MedicationLog', () {
      test('should parse from JSON', () {
        final json = {
          'id': '1',
          'reminder_id': '2',
          'scheduled_time': '08:00',
          'taken_at': '2024-01-01T08:00:00Z',
          'is_taken': true,
        };
        final log = MedicationLog.fromJson(json);
        expect(log.id, '1');
        expect(log.scheduledTime, '08:00');
        expect(log.isTaken, true);
      });
    });

    group('MedicationReminder', () {
      test('should parse from JSON', () {
        final json = {
          'id': '1',
          'medication_id': '2',
          'medication_name': '维生素',
          'reminder_times': ['08:00', '20:00'],
          'frequency': 'daily',
          'is_active': true,
          'created_at': '2024-01-01T00:00:00Z',
        };
        final reminder = MedicationReminder.fromJson(json);
        expect(reminder.medicationName, '维生素');
        expect(reminder.reminderTimes, ['08:00', '20:00']);
        expect(reminder.frequency, MedicationFrequency.daily);
        expect(reminder.needsToTakeToday(), true);
      });

      test('isTimeTaken should work', () {
        final reminder = MedicationReminder(
          id: '1',
          medicationId: '2',
          medicationName: 'Test',
          reminderTimes: ['08:00'],
          createdAt: DateTime.now(),
          logs: [],
        );
        expect(reminder.isTimeTaken('08:00'), false);
      });
    });

    group('SelectableMedication', () {
      test('should parse from JSON', () {
        final json = {'id': '1', 'name': '阿司匹林', 'dosage': '100mg', 'unit': 'mg'};
        final med = SelectableMedication.fromJson(json);
        expect(med.name, '阿司匹林');
        expect(med.dosage, '100mg');
        expect(med.unit, 'mg');
      });
    });
  });
}
