library;

import 'package:qilema_app/core/models/health_models.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';
import 'package:qilema_app/shared/services/auth_service.dart';

/// 健康档案API服务
class HealthApi {
  final ApiClient _apiClient = ApiClient();

  /// 获取当前用户ID
  Future<String> getCurrentUserId() async {
    final userId = await AuthService.getUserId();
    if (userId == null || userId.isEmpty) {
      throw Exception('用户未登录');
    }
    return userId;
  }

  /// 获取健康档案
  Future<Map<String, dynamic>> getHealthRecord() async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.get('/health-records/$userId');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return data;
      }

      throw Exception('获取健康档案失败');
    } catch (e) {
      Logger.e('获取健康档案API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新健康档案基本信息
  Future<HealthRecord> updateHealthRecord(HealthRecord record) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.put(
        '/health-records/$userId',
        data: record.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return HealthRecord.fromJson(data);
      }

      throw Exception('更新健康档案失败');
    } catch (e) {
      Logger.e('更新健康档案API调用失败', error: e);
      rethrow;
    }
  }

  /// 创建健康档案
  Future<HealthRecord> createHealthRecord(HealthRecord record) async {
    try {
      final response = await _apiClient.post(
        '/health-records/',
        data: record.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return HealthRecord.fromJson(data);
      }

      throw Exception('创建健康档案失败');
    } catch (e) {
      Logger.e('创建健康档案API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取病史记录列表
  Future<List<MedicalHistory>> getMedicalHistories() async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.get('/health-records/$userId/medical-histories');

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((item) => MedicalHistory.fromJson(item)).toList();
      }

      throw Exception('获取病史记录失败');
    } catch (e) {
      Logger.e('获取病史记录API调用失败', error: e);
      rethrow;
    }
  }

  /// 添加病史记录
  Future<MedicalHistory> addMedicalHistory(MedicalHistory history) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.post(
        '/health-records/$userId/medical-histories',
        data: history.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return MedicalHistory.fromJson(data);
      }

      throw Exception('添加病史记录失败');
    } catch (e) {
      Logger.e('添加病史记录API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新病史记录
  Future<MedicalHistory> updateMedicalHistory(int historyId, MedicalHistory history) async {
    try {
      final response = await _apiClient.put(
        '/health-records/medical-histories/$historyId',
        data: history.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return MedicalHistory.fromJson(data);
      }

      throw Exception('更新病史记录失败');
    } catch (e) {
      Logger.e('更新病史记录API调用失败', error: e);
      rethrow;
    }
  }

  /// 删除病史记录
  Future<bool> deleteMedicalHistory(int historyId) async {
    try {
      final response = await _apiClient.delete('/health-records/medical-histories/$historyId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('删除病史记录失败');
    } catch (e) {
      Logger.e('删除病史记录API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取用药信息列表
  Future<List<MedicationInfo>> getMedications({bool currentOnly = false}) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.get(
        '/health-records/$userId/medications',
        queryParameters: {'current_only': currentOnly},
      );

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((item) => MedicationInfo.fromJson(item)).toList();
      }

      throw Exception('获取用药信息失败');
    } catch (e) {
      Logger.e('获取用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 添加用药信息
  Future<MedicationInfo> addMedication(MedicationInfo medication) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.post(
        '/health-records/$userId/medications',
        data: medication.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return MedicationInfo.fromJson(data);
      }

      throw Exception('添加用药信息失败');
    } catch (e) {
      Logger.e('添加用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新用药信息
  Future<MedicationInfo> updateMedication(int medicationId, MedicationInfo medication) async {
    try {
      final response = await _apiClient.put(
        '/health-records/medications/$medicationId',
        data: medication.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return MedicationInfo.fromJson(data);
      }

      throw Exception('更新用药信息失败');
    } catch (e) {
      Logger.e('更新用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 删除用药信息
  Future<bool> deleteMedication(int medicationId) async {
    try {
      final response = await _apiClient.delete('/health-records/medications/$medicationId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('删除用药信息失败');
    } catch (e) {
      Logger.e('删除用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 获取过敏史列表
  Future<List<Allergy>> getAllergies() async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.get('/health-records/$userId/allergies');

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((item) => Allergy.fromJson(item)).toList();
      }

      throw Exception('获取过敏史失败');
    } catch (e) {
      Logger.e('获取过敏史API调用失败', error: e);
      rethrow;
    }
  }

  /// 添加过敏史
  Future<Allergy> addAllergy(Allergy allergy) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.post(
        '/health-records/$userId/allergies',
        data: allergy.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Allergy.fromJson(data);
      }

      throw Exception('添加过敏史失败');
    } catch (e) {
      Logger.e('添加过敏史API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新过敏史
  Future<Allergy> updateAllergy(int allergyId, Allergy allergy) async {
    try {
      final response = await _apiClient.put(
        '/health-records/allergies/$allergyId',
        data: allergy.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Allergy.fromJson(data);
      }

      throw Exception('更新过敏史失败');
    } catch (e) {
      Logger.e('更新过敏史API调用失败', error: e);
      rethrow;
    }
  }

  /// 删除过敏史
  Future<bool> deleteAllergy(int allergyId) async {
    try {
      final response = await _apiClient.delete('/health-records/allergies/$allergyId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('删除过敏史失败');
    } catch (e) {
      Logger.e('删除过敏史API调用失败', error: e);
      rethrow;
    }
  }
}
