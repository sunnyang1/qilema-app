import 'package:qilema_app/core/models/medication_models.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

export 'package:qilema_app/core/models/medication_models.dart';

/// 用药提醒API服务
class MedicationApi {
  static const String _baseUrl = '/api/v1/medication';

  /// 获取用药提醒列表
  static Future<List<MedicationReminder>> getReminders() async {
    try {
      final response = await ApiClient().get('$_baseUrl/reminders');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => MedicationReminder.fromJson(json)).toList();
      }
      return _getMockReminders();
    } catch (e) {
      Logger.e('获取用药提醒失败', error: e);
      return _getMockReminders();
    }
  }

  /// 获取可选择的药品列表（来自健康档案）
  static Future<List<SelectableMedication>> getSelectableMedications() async {
    try {
      final response = await ApiClient().get('$_baseUrl/medications');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => SelectableMedication.fromJson(json)).toList();
      }
      return _getMockSelectableMedications();
    } catch (e) {
      Logger.e('获取药品列表失败', error: e);
      return _getMockSelectableMedications();
    }
  }

  /// 创建用药提醒
  static Future<MedicationReminder?> createReminder({
    required String medicationId,
    required String medicationName,
    String? dosage,
    String? unit,
    required List<String> reminderTimes,
    MedicationFrequency frequency = MedicationFrequency.daily,
    List<int>? weekdays,
  }) async {
    try {
      final response = await ApiClient().post(
        '$_baseUrl/reminders',
        data: {
          'medication_id': medicationId,
          'medication_name': medicationName,
          'dosage': dosage,
          'unit': unit,
          'reminder_times': reminderTimes,
          'frequency': frequency.name,
          'weekdays': weekdays,
        },
      );

      if (response.statusCode == 201) {
        return MedicationReminder.fromJson(response.data['data']);
      }
      return null;
    } catch (e) {
      Logger.e('创建用药提醒失败', error: e);
      // 模拟成功返回
      return MedicationReminder(
        id: 'reminder_${DateTime.now().millisecondsSinceEpoch}',
        medicationId: medicationId,
        medicationName: medicationName,
        dosage: dosage,
        unit: unit,
        reminderTimes: reminderTimes,
        frequency: frequency,
        weekdays: weekdays,
        createdAt: DateTime.now(),
      );
    }
  }

  /// 更新用药提醒
  static Future<MedicationReminder?> updateReminder(
    String reminderId, {
    List<String>? reminderTimes,
    MedicationFrequency? frequency,
    List<int>? weekdays,
    bool? isActive,
  }) async {
    try {
      final response = await ApiClient().put(
        '$_baseUrl/reminders/$reminderId',
        data: {
          if (reminderTimes != null) 'reminder_times': reminderTimes,
          if (frequency != null) 'frequency': frequency.name,
          if (weekdays != null) 'weekdays': weekdays,
          if (isActive != null) 'is_active': isActive,
        },
      );

      if (response.statusCode == 200) {
        return MedicationReminder.fromJson(response.data['data']);
      }
      return null;
    } catch (e) {
      Logger.e('更新用药提醒失败', error: e);
      return null;
    }
  }

  /// 删除用药提醒
  static Future<bool> deleteReminder(String reminderId) async {
    try {
      final response = await ApiClient().delete(
        '$_baseUrl/reminders/$reminderId',
      );
      return response.statusCode == 204 || response.statusCode == 200;
    } catch (e) {
      Logger.e('删除用药提醒失败', error: e);
      return true; // 模拟成功
    }
  }

  /// 记录用药
  static Future<MedicationLog?> recordTaking(
    String reminderId,
    String scheduledTime, {
    String? notes,
  }) async {
    try {
      final response = await ApiClient().post(
        '$_baseUrl/reminders/$reminderId/take',
        data: {
          'scheduled_time': scheduledTime,
          'taken_at': DateTime.now().toIso8601String(),
          'notes': notes,
        },
      );

      if (response.statusCode == 201) {
        return MedicationLog.fromJson(response.data['data']);
      }
      return _createMockLog(reminderId, scheduledTime);
    } catch (e) {
      Logger.e('记录用药失败', error: e);
      return _createMockLog(reminderId, scheduledTime);
    }
  }

  /// 获取今日用药计划
  static Future<List<MedicationReminder>> getTodayReminders() async {
    final reminders = await getReminders();
    return reminders.where((r) => r.needsToTakeToday()).toList();
  }

  /// 模拟提醒数据
  static List<MedicationReminder> _getMockReminders() {
    return [
      MedicationReminder(
        id: 'reminder_001',
        medicationId: 'med_001',
        medicationName: '阿司匹林肠溶片',
        dosage: '100',
        unit: 'mg',
        reminderTimes: ['08:00'],
        frequency: MedicationFrequency.daily,
        isActive: true,
        createdAt: DateTime.now().subtract(const Duration(days: 30)),
        logs: [
          MedicationLog(
            id: 'log_001',
            reminderId: 'reminder_001',
            scheduledTime: '08:00',
            takenAt: DateTime.now().subtract(const Duration(hours: 2)),
          ),
        ],
      ),
      MedicationReminder(
        id: 'reminder_002',
        medicationId: 'med_002',
        medicationName: '降压药（氨氯地平）',
        dosage: '5',
        unit: 'mg',
        reminderTimes: ['08:00', '20:00'],
        frequency: MedicationFrequency.daily,
        isActive: true,
        createdAt: DateTime.now().subtract(const Duration(days: 60)),
        logs: [
          MedicationLog(
            id: 'log_002',
            reminderId: 'reminder_002',
            scheduledTime: '08:00',
            takenAt: DateTime.now().subtract(const Duration(hours: 2)),
          ),
        ],
      ),
      MedicationReminder(
        id: 'reminder_003',
        medicationId: 'med_003',
        medicationName: '维生素D',
        dosage: '1',
        unit: '粒',
        reminderTimes: ['12:00'],
        frequency: MedicationFrequency.weekly,
        weekdays: [1, 3, 5], // 周一三五
        isActive: true,
        createdAt: DateTime.now().subtract(const Duration(days: 15)),
        logs: [],
      ),
      MedicationReminder(
        id: 'reminder_004',
        medicationId: 'med_004',
        medicationName: '血糖药（二甲双胍）',
        dosage: '500',
        unit: 'mg',
        reminderTimes: ['07:00', '12:00', '18:00'],
        frequency: MedicationFrequency.daily,
        isActive: false,
        createdAt: DateTime.now().subtract(const Duration(days: 90)),
        logs: [],
      ),
    ];
  }

  /// 模拟可选药品
  static List<SelectableMedication> _getMockSelectableMedications() {
    return [
      SelectableMedication(
        id: 'med_001',
        name: '阿司匹林肠溶片',
        dosage: '100',
        unit: 'mg',
        frequency: '每日一次',
      ),
      SelectableMedication(
        id: 'med_002',
        name: '降压药（氨氯地平）',
        dosage: '5',
        unit: 'mg',
        frequency: '每日两次',
      ),
      SelectableMedication(
        id: 'med_003',
        name: '维生素D',
        dosage: '1',
        unit: '粒',
        frequency: '每周三次',
      ),
      SelectableMedication(
        id: 'med_004',
        name: '血糖药（二甲双胍）',
        dosage: '500',
        unit: 'mg',
        frequency: '每日三次',
      ),
      SelectableMedication(
        id: 'med_005',
        name: '钙片',
        dosage: '600',
        unit: 'mg',
        frequency: '每日一次',
      ),
    ];
  }

  /// 创建模拟日志
  static MedicationLog _createMockLog(String reminderId, String scheduledTime) {
    return MedicationLog(
      id: 'log_${DateTime.now().millisecondsSinceEpoch}',
      reminderId: reminderId,
      scheduledTime: scheduledTime,
      takenAt: DateTime.now(),
    );
  }
}
