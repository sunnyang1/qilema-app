import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/medication/services/medication_api.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 加载状态
enum LoadingState { initial, loading, success, error }

/// 用药提醒状态
class MedicationState {
  final LoadingState remindersState;
  final LoadingState medicationsState;
  final LoadingState actionState;
  final List<MedicationReminder> reminders;
  final List<SelectableMedication> availableMedications;
  final String? errorMessage;

  const MedicationState({
    this.remindersState = LoadingState.initial,
    this.medicationsState = LoadingState.initial,
    this.actionState = LoadingState.initial,
    this.reminders = const [],
    this.availableMedications = const [],
    this.errorMessage,
  });

  MedicationState copyWith({
    LoadingState? remindersState,
    LoadingState? medicationsState,
    LoadingState? actionState,
    List<MedicationReminder>? reminders,
    List<SelectableMedication>? availableMedications,
    String? errorMessage,
  }) {
    return MedicationState(
      remindersState: remindersState ?? this.remindersState,
      medicationsState: medicationsState ?? this.medicationsState,
      actionState: actionState ?? this.actionState,
      reminders: reminders ?? this.reminders,
      availableMedications: availableMedications ?? this.availableMedications,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isLoadingReminders => remindersState == LoadingState.loading;
  bool get isLoadingMedications => medicationsState == LoadingState.loading;
  bool get isProcessing => actionState == LoadingState.loading;
  bool get hasError => remindersState == LoadingState.error || 
                       medicationsState == LoadingState.error ||
                       actionState == LoadingState.error;

  /// 获取今日需要服用的提醒
  List<MedicationReminder> get todayReminders {
    return reminders.where((r) => r.needsToTakeToday()).toList();
  }

  /// 获取所有提醒（包括不活跃的）
  List<MedicationReminder> get allReminders => reminders;

  /// 获取活跃提醒数量
  int get activeReminderCount {
    return reminders.where((r) => r.isActive).length;
  }

  /// 获取今日待服用次数
  int get todayPendingCount {
    int count = 0;
    for (final reminder in todayReminders) {
      if (reminder.isActive) {
        for (final time in reminder.reminderTimes) {
          if (!reminder.isTimeTaken(time)) {
            count++;
          }
        }
      }
    }
    return count;
  }

  /// 获取今日已服用次数
  int get todayTakenCount {
    int count = 0;
    for (final reminder in todayReminders) {
      count += reminder.getTodayLogs().length;
    }
    return count;
  }
}

/// 用药提醒状态管理
class MedicationNotifier extends Notifier<MedicationState> {
  @override
  MedicationState build() => const MedicationState();

  /// 加载用药提醒列表
  Future<void> loadReminders() async {
    state = state.copyWith(remindersState: LoadingState.loading);

    try {
      final reminders = await MedicationApi.getReminders();
      state = state.copyWith(
        remindersState: LoadingState.success,
        reminders: reminders,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载用药提醒失败', error: e);
      state = state.copyWith(
        remindersState: LoadingState.error,
        errorMessage: '加载用药提醒失败: ${e.toString()}',
      );
    }
  }

  /// 加载可选药品列表
  Future<void> loadAvailableMedications() async {
    state = state.copyWith(medicationsState: LoadingState.loading);

    try {
      final medications = await MedicationApi.getSelectableMedications();
      state = state.copyWith(
        medicationsState: LoadingState.success,
        availableMedications: medications,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载药品列表失败', error: e);
      state = state.copyWith(
        medicationsState: LoadingState.error,
        errorMessage: '加载药品列表失败: ${e.toString()}',
      );
    }
  }

  /// 创建用药提醒
  Future<bool> createReminder({
    required String medicationId,
    required String medicationName,
    String? dosage,
    String? unit,
    required List<String> reminderTimes,
    MedicationFrequency frequency = MedicationFrequency.daily,
    List<int>? weekdays,
  }) async {
    state = state.copyWith(actionState: LoadingState.loading);

    try {
      final reminder = await MedicationApi.createReminder(
        medicationId: medicationId,
        medicationName: medicationName,
        dosage: dosage,
        unit: unit,
        reminderTimes: reminderTimes,
        frequency: frequency,
        weekdays: weekdays,
      );

      if (reminder != null) {
        final updatedReminders = [...state.reminders, reminder];
        state = state.copyWith(
          actionState: LoadingState.success,
          reminders: updatedReminders,
          errorMessage: null,
        );
        return true;
      } else {
        state = state.copyWith(
          actionState: LoadingState.error,
          errorMessage: '创建失败',
        );
        return false;
      }
    } catch (e) {
      Logger.e('创建用药提醒失败', error: e);
      state = state.copyWith(
        actionState: LoadingState.error,
        errorMessage: '创建失败: ${e.toString()}',
      );
      return false;
    }
  }

  /// 记录用药
  Future<bool> recordTaking(String reminderId, String scheduledTime) async {
    try {
      final log = await MedicationApi.recordTaking(reminderId, scheduledTime);

      if (log != null) {
        // 更新本地状态
        final updatedReminders = state.reminders.map((reminder) {
          if (reminder.id == reminderId) {
            final updatedLogs = [...reminder.logs, log];
            return MedicationReminder(
              id: reminder.id,
              medicationId: reminder.medicationId,
              medicationName: reminder.medicationName,
              dosage: reminder.dosage,
              unit: reminder.unit,
              reminderTimes: reminder.reminderTimes,
              frequency: reminder.frequency,
              weekdays: reminder.weekdays,
              isActive: reminder.isActive,
              createdAt: reminder.createdAt,
              updatedAt: reminder.updatedAt,
              logs: updatedLogs,
            );
          }
          return reminder;
        }).toList();

        state = state.copyWith(reminders: updatedReminders);
        return true;
      }
      return false;
    } catch (e) {
      Logger.e('记录用药失败', error: e);
      return false;
    }
  }

  /// 切换提醒开关
  Future<bool> toggleReminder(String reminderId, bool isActive) async {
    try {
      final updated = await MedicationApi.updateReminder(
        reminderId,
        isActive: isActive,
      );

      if (updated != null) {
        final updatedReminders = state.reminders.map((reminder) {
          if (reminder.id == reminderId) {
            return MedicationReminder(
              id: reminder.id,
              medicationId: reminder.medicationId,
              medicationName: reminder.medicationName,
              dosage: reminder.dosage,
              unit: reminder.unit,
              reminderTimes: reminder.reminderTimes,
              frequency: reminder.frequency,
              weekdays: reminder.weekdays,
              isActive: isActive,
              createdAt: reminder.createdAt,
              updatedAt: DateTime.now(),
              logs: reminder.logs,
            );
          }
          return reminder;
        }).toList();

        state = state.copyWith(reminders: updatedReminders);
        return true;
      }
      return false;
    } catch (e) {
      Logger.e('切换提醒失败', error: e);
      return false;
    }
  }

  /// 删除提醒
  Future<bool> deleteReminder(String reminderId) async {
    try {
      final success = await MedicationApi.deleteReminder(reminderId);

      if (success) {
        final updatedReminders = state.reminders
            .where((r) => r.id != reminderId)
            .toList();
        state = state.copyWith(reminders: updatedReminders);
        return true;
      }
      return false;
    } catch (e) {
      Logger.e('删除提醒失败', error: e);
      return false;
    }
  }

  /// 刷新
  Future<void> refresh() async {
    await loadReminders();
  }

  /// 清除错误
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}

/// 用药提醒Provider
final medicationProvider = NotifierProvider<MedicationNotifier, MedicationState>(MedicationNotifier.new);
