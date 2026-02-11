library;

import 'package:equatable/equatable.dart';

/// 用药频率
enum MedicationFrequency {
  daily,      // 每天
  weekly,     // 每周
  custom,     // 自定义
}

/// 用药记录
class MedicationLog extends Equatable {
  final String id;
  final String reminderId;
  final String scheduledTime;  // 计划时间 "08:00"
  final DateTime takenAt;      // 实际服用时间
  final bool isTaken;
  final String? notes;

  const MedicationLog({
    required this.id,
    required this.reminderId,
    required this.scheduledTime,
    required this.takenAt,
    this.isTaken = true,
    this.notes,
  });

  @override
  List<Object?> get props => [id, reminderId, scheduledTime, takenAt, isTaken, notes];

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

/// 用药提醒
class MedicationReminder extends Equatable {
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

  const MedicationReminder({
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

  @override
  List<Object?> get props => [
        id, medicationId, medicationName, dosage, unit,
        reminderTimes, frequency, weekdays, isActive,
        createdAt, updatedAt, logs,
      ];

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

/// 可选药品
class SelectableMedication extends Equatable {
  final String id;
  final String name;
  final String? dosage;
  final String? unit;
  final String? frequency;

  const SelectableMedication({
    required this.id,
    required this.name,
    this.dosage,
    this.unit,
    this.frequency,
  });

  @override
  List<Object?> get props => [id, name, dosage, unit, frequency];

  factory SelectableMedication.fromJson(Map<String, dynamic> json) {
    return SelectableMedication(
      id: json['id'] as String,
      name: json['name'] as String,
      dosage: json['dosage'] as String? ?? json['default_dosage'] as String?,
      unit: json['unit'] as String? ?? json['default_unit'] as String?,
      frequency: json['frequency'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'dosage': dosage,
      'unit': unit,
      'frequency': frequency,
    };
  }
}
