import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/base_state.dart';
import 'package:qilema_app/core/models/health_models.dart';
import 'package:qilema_app/core/providers/base_notifier.dart';
import 'package:qilema_app/core/constants/loading_state.dart';
import 'package:qilema_app/features/health/services/health_api.dart';

/// 健康档案状态类
base class HealthState extends BaseState {
  final HealthRecord? healthRecord;
  final List<MedicalHistory> medicalHistories;
  final List<MedicationInfo> medications;
  final List<Allergy> allergies;

  const HealthState({
    super.status = LoadingState.initial,
    this.healthRecord,
    this.medicalHistories = const [],
    this.medications = const [],
    this.allergies = const [],
    super.errorMessage,
  });

  @override
  HealthState copyWith({
    LoadingState? status,
    HealthRecord? healthRecord,
    List<MedicalHistory>? medicalHistories,
    List<MedicationInfo>? medications,
    List<Allergy>? allergies,
    String? errorMessage,
  }) {
    return HealthState(
      status: status ?? this.status,
      healthRecord: healthRecord ?? this.healthRecord,
      medicalHistories: medicalHistories ?? this.medicalHistories,
      medications: medications ?? this.medications,
      allergies: allergies ?? this.allergies,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get hasRecord => healthRecord != null;

  @override
  List<Object?> get props => [status, healthRecord, medicalHistories, medications, allergies, errorMessage];
}

/// 健康档案状态管理器
base class HealthNotifier extends Notifier<HealthState> with BaseNotifierMixin<HealthState> {
  late final HealthApi _api;

  @override
  HealthState build() {
    _api = HealthApi();
    load();
    return const HealthState();
  }

  /// 加载健康档案
  @override
  Future<void> load() async {
    state = state.copyWith(status: LoadingState.loading);
    try {
      final data = await _api.getHealthRecord();

      // 解析基本信息
      final healthRecord = HealthRecord.fromJson(data);

      // 解析病史记录
      final medicalHistories = (data['medical_histories'] as List?)
              ?.map((item) => MedicalHistory.fromJson(item))
              .toList() ??
          [];

      // 解析用药信息
      final medications = (data['medications'] as List?)
              ?.map((item) => MedicationInfo.fromJson(item))
              .toList() ??
          [];

      // 解析过敏史
      final allergies = (data['allergies'] as List?)
              ?.map((item) => Allergy.fromJson(item))
              .toList() ??
          [];

      state = HealthState(
        status: LoadingState.loaded,
        healthRecord: healthRecord,
        medicalHistories: medicalHistories,
        medications: medications,
        allergies: allergies,
      );
    } catch (e) {
      // 如果健康档案不存在，创建一个空的
      try {
        final newRecord = await _api.createHealthRecord(HealthRecord(
          id: '',
          userId: await _api.getCurrentUserId(),
        ));
        state = HealthState(
          status: LoadingState.loaded,
          healthRecord: newRecord,
        );
      } catch (createError) {
        state = state.copyWith(
          status: LoadingState.error,
          errorMessage: createError.toString(),
        );
      }
    }
  }

  /// 更新健康档案基本信息
  Future<void> updateHealthRecord(HealthRecord record) async {
    state = state.copyWith(status: LoadingState.loading);
    try {
      final updatedRecord = await _api.updateHealthRecord(record);
      state = state.copyWith(
        status: LoadingState.loaded,
        healthRecord: updatedRecord,
      );
    } catch (e) {
      state = state.copyWith(
        status: LoadingState.error,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 添加病史记录
  Future<void> addMedicalHistory(MedicalHistory history) async {
    try {
      final newHistory = await _api.addMedicalHistory(history);
      state = state.copyWith(
        medicalHistories: [...state.medicalHistories, newHistory],
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 更新病史记录
  Future<void> updateMedicalHistory(int historyId, MedicalHistory history) async {
    try {
      final updatedHistory = await _api.updateMedicalHistory(historyId, history);
      final updatedHistories = state.medicalHistories.map((h) {
        return h.id == historyId ? updatedHistory : h;
      }).toList();
      state = state.copyWith(medicalHistories: updatedHistories);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 删除病史记录
  Future<void> deleteMedicalHistory(int historyId) async {
    try {
      await _api.deleteMedicalHistory(historyId);
      final updatedHistories = state.medicalHistories.where((h) => h.id != historyId).toList();
      state = state.copyWith(medicalHistories: updatedHistories);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 添加用药信息
  Future<void> addMedication(MedicationInfo medication) async {
    try {
      final newMedication = await _api.addMedication(medication);
      state = state.copyWith(
        medications: [...state.medications, newMedication],
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 更新用药信息
  Future<void> updateMedication(int medicationId, MedicationInfo medication) async {
    try {
      final updatedMedication = await _api.updateMedication(medicationId, medication);
      final updatedMedications = state.medications.map((m) {
        return m.id == medicationId ? updatedMedication : m;
      }).toList();
      state = state.copyWith(medications: updatedMedications);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 删除用药信息
  Future<void> deleteMedication(int medicationId) async {
    try {
      await _api.deleteMedication(medicationId);
      final updatedMedications = state.medications.where((m) => m.id != medicationId).toList();
      state = state.copyWith(medications: updatedMedications);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 添加过敏史
  Future<void> addAllergy(Allergy allergy) async {
    try {
      final newAllergy = await _api.addAllergy(allergy);
      state = state.copyWith(
        allergies: [...state.allergies, newAllergy],
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 更新过敏史
  Future<void> updateAllergy(int allergyId, Allergy allergy) async {
    try {
      final updatedAllergy = await _api.updateAllergy(allergyId, allergy);
      final updatedAllergies = state.allergies.map((a) {
        return a.id == allergyId ? updatedAllergy : a;
      }).toList();
      state = state.copyWith(allergies: updatedAllergies);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 删除过敏史
  Future<void> deleteAllergy(int allergyId) async {
    try {
      await _api.deleteAllergy(allergyId);
      final updatedAllergies = state.allergies.where((a) => a.id != allergyId).toList();
      state = state.copyWith(allergies: updatedAllergies);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }
}

/// 健康档案状态Provider
final healthProvider = NotifierProvider<HealthNotifier, HealthState>(HealthNotifier.new);
