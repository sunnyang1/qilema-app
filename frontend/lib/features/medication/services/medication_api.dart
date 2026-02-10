import 'dart:convert';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 用药频率
enum MedicationFrequency {
  daily,      // 每天
  weekly,     // 每周
  custom,     // 自定义
}

/// 用药提醒
class MedicationReminder {
  final String id;
  final String medicationId;
  final String medicationName;
  final String? dosage;           // 剂量
  final String? unit;             // 单位
  final List<String> reminderTimes;  // 提醒时间 ["08:00", "12:00"]
  final MedicationFrequency frequency;
  final List<int>? weekdays;      // 每周几 [1,3,5] 周一三五
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<MedicationLog> logs; // 服用记录

  MedicationReminder({
    required this.id,
    required this.medicationId,
    required this.medicationName,
    this.dosage,
    this.unit,
    required this.reminderTimes,
    this.frequency = MedicationFrequency.daily,
    this.weekdays,
    this.isActive = true,
    required this.createdAt,
    this.updatedAt,
    this.logs = const [],
  });

  factory MedicationReminder.fromJson(Map<String, dynamic> json) {
    return MedicationReminder(
      id: json['id'] as String,
      medicationId: json['medication_id'] as String,
      medicationName: json['medication_name'] as String,
      dosage: json['dosage'] as String?,
      unit: json['unit'] as String?,
      reminderTimes: (json['reminder_times'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      frequency: MedicationFrequency.values.firstWhere(
        (e) => e.name == json['frequency'],
        orElse: () => MedicationFrequency.daily,
      ),
      weekdays: (json['weekdays'] as List<dynamic>?)
          ?.map((e) => e as int)
          .toList(),
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      logs: (json['logs'] as List<dynamic>?)
              ?.map((e) => MedicationLog.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'medication_id': medicationId,
      'medication_name': medicationName,
      'dosage': dosage,
      'unit': unit,
      'reminder_times': reminderTimes,
      'frequency': frequency.name,
      'weekdays': weekdays,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  /// 检查今天是否需要服用
  bool needsToTakeToday() {
    if (!isActive) return false;
    if (frequency == MedicationFrequency.daily) return true;
    if (frequency == MedicationFrequency.weekly && weekdays != null) {
      final today = DateTime.now().weekday;
      return weekdays!.contains(today);
    }
    return true;
  }

  /// 获取今天的服用记录
  List<MedicationLog> getTodayLogs() {
    final today = DateTime.now();
    return logs.where((log) {
      return log.takenAt.year == today.year &&
          log.takenAt.month == today.month &&
          log.takenAt.day == today.day;
    }).toList();
  }

  /// 检查某个时间点是否已服用
  bool isTimeTaken(String time) {
    final todayLogs = getTodayLogs();
    return todayLogs.any((log) => log.scheduledTime == time);
  }
}

/// 用药记录
class MedicationLog {
  final String id;
  final String reminderId;
  final String scheduledTime;  // 计划时间 "08:00"
  final DateTime takenAt;      // 实际服用时间
  final bool isTaken;
  final String? notes;

  MedicationLog({
    required this.id,
    required this.reminderId,
    required this.scheduledTime,
    required this.takenAt,
    this.isTaken = true,
    this.notes,
  });

  factory MedicationLog.fromJson(Map<String, dynamic> json) {
    return MedicationLog(
      id: json['id'] as String,
      reminderId: json['reminder_id'] as String,
      scheduledTime: json['scheduled_time'] as String,
      takenAt: DateTime.parse(json['taken_at'] as String),
      isTaken: json['is_taken'] as bool? ?? true,
      notes: json['notes'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'reminder_id': reminderId,
      'scheduled_time': scheduledTime,
      'taken_at': takenAt.toIso8601String(),
      'is_taken': isTaken,
      'notes': notes,
    };
  }
}

/// 可选择的药品（来自健康档案）
class SelectableMedication {
  final String id;
  final String name;
  final String? dosage;
  final String? unit;
  final String? frequency;

  SelectableMedication({
    required this.id,
    required this.name,
    this.dosage,
    this.unit,
    this.frequency,
  });

  factory SelectableMedication.fromJson(Map<String, dynamic> json) {
    return SelectableMedication(
      id: json['id'] as String,
      name: json['name'] as String,
      dosage: json['dosage'] as String?,
      unit: json['unit'] as String?,
      frequency: json['frequency'] as String?,
    );
  }
}

/// 用药提醒API服务
class MedicationApi {
  static const String _baseUrl = '/api/v1/medication';

  /// 获取用药提醒列表
  static Future<List<MedicationReminder>> getReminders() async {
    try {
      final response = await ApiClient.instance.get('$_baseUrl/reminders');

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
      final response = await ApiClient.instance.get('$_baseUrl/medications');

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
      final response = await ApiClient.instance.post(
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
      final response = await ApiClient.instance.put(
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
      final response = await ApiClient.instance.delete(
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
      final response = await ApiClient.instance.post(
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
