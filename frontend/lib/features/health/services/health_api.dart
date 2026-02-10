import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 健康档案基本信息
class HealthRecord {
  final String id;
  final String userId;
  final String? realName;
  final String? gender;
  final String? bloodType;
  final double? height;
  final double? weight;
  final int? age;
  final String? emergencyContactName;
  final String? emergencyContactPhone;
  final String? emergencyContactRelation;

  HealthRecord({
    required this.id,
    required this.userId,
    this.realName,
    this.gender,
    this.bloodType,
    this.height,
    this.weight,
    this.age,
    this.emergencyContactName,
    this.emergencyContactPhone,
    this.emergencyContactRelation,
  });

  factory HealthRecord.fromJson(Map<String, dynamic> json) {
    return HealthRecord(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      realName: json['real_name'],
      gender: json['gender'],
      bloodType: json['blood_type'],
      height: (json['height'] as num?)?.toDouble(),
      weight: (json['weight'] as num?)?.toDouble(),
      age: json['age'] as int?,
      emergencyContactName: json['emergency_contact_name'],
      emergencyContactPhone: json['emergency_contact_phone'],
      emergencyContactRelation: json['emergency_contact_relation'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'real_name': realName,
      'gender': gender,
      'blood_type': bloodType,
      'height': height,
      'weight': weight,
      'age': age,
      'emergency_contact_name': emergencyContactName,
      'emergency_contact_phone': emergencyContactPhone,
      'emergency_contact_relation': emergencyContactRelation,
    };
  }
}

/// 病史记录
class MedicalHistory {
  final int id;
  final int healthRecordId;
  final String diseaseName;
  final String? diagnosisDate;
  final String? description;
  final String? severity;
  final bool isChronic;

  MedicalHistory({
    required this.id,
    required this.healthRecordId,
    required this.diseaseName,
    this.diagnosisDate,
    this.description,
    this.severity,
    this.isChronic = false,
  });

  factory MedicalHistory.fromJson(Map<String, dynamic> json) {
    return MedicalHistory(
      id: json['id'] ?? 0,
      healthRecordId: json['health_record_id'] ?? 0,
      diseaseName: json['disease_name'] ?? '',
      diagnosisDate: json['diagnosis_date'],
      description: json['description'],
      severity: json['severity'],
      isChronic: json['is_chronic'] == 1 || json['is_chronic'] == true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'disease_name': diseaseName,
      'diagnosis_date': diagnosisDate,
      'description': description,
      'severity': severity,
      'is_chronic': isChronic,
    };
  }
}

/// 用药信息
class Medication {
  final int id;
  final int healthRecordId;
  final String drugName;
  final String? dosage;
  final String? frequency;
  final String? startDate;
  final String? endDate;
  final bool isCurrent;
  final String? notes;

  Medication({
    required this.id,
    required this.healthRecordId,
    required this.drugName,
    this.dosage,
    this.frequency,
    this.startDate,
    this.endDate,
    this.isCurrent = false,
    this.notes,
  });

  factory Medication.fromJson(Map<String, dynamic> json) {
    return Medication(
      id: json['id'] ?? 0,
      healthRecordId: json['health_record_id'] ?? 0,
      drugName: json['drug_name'] ?? '',
      dosage: json['dosage'],
      frequency: json['frequency'],
      startDate: json['start_date'],
      endDate: json['end_date'],
      isCurrent: json['is_current'] == 1 || json['is_current'] == true,
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'drug_name': drugName,
      'dosage': dosage,
      'frequency': frequency,
      'start_date': startDate,
      'end_date': endDate,
      'is_current': isCurrent,
      'notes': notes,
    };
  }
}

/// 过敏史
class Allergy {
  final int id;
  final int healthRecordId;
  final String allergen;
  final String? allergicReaction;
  final String? severity;
  final String? discoveredDate;
  final String? notes;

  Allergy({
    required this.id,
    required this.healthRecordId,
    required this.allergen,
    this.allergicReaction,
    this.severity,
    this.discoveredDate,
    this.notes,
  });

  factory Allergy.fromJson(Map<String, dynamic> json) {
    return Allergy(
      id: json['id'] ?? 0,
      healthRecordId: json['health_record_id'] ?? 0,
      allergen: json['allergen'] ?? '',
      allergicReaction: json['allergic_reaction'],
      severity: json['severity'],
      discoveredDate: json['discovered_date'],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'allergen': allergen,
      'allergic_reaction': allergicReaction,
      'severity': severity,
      'discovered_date': discoveredDate,
      'notes': notes,
    };
  }
}

/// 健康档案API服务
class HealthApi {
  final ApiClient _apiClient = ApiClient();

  /// 获取当前用户ID（这里简化处理，实际应该从认证状态获取）
  Future<String> getCurrentUserId() async {
    // TODO: 从全局认证状态获取当前用户ID
    return 'current_user_id';
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
  Future<List<Medication>> getMedications({bool currentOnly = false}) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.get(
        '/health-records/$userId/medications',
        queryParameters: {'current_only': currentOnly},
      );

      if (response.statusCode == 200) {
        final data = response.data['data'] as List;
        return data.map((item) => Medication.fromJson(item)).toList();
      }

      throw Exception('获取用药信息失败');
    } catch (e) {
      Logger.e('获取用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 添加用药信息
  Future<Medication> addMedication(Medication medication) async {
    try {
      final userId = await getCurrentUserId();
      final response = await _apiClient.post(
        '/health-records/$userId/medications',
        data: medication.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Medication.fromJson(data);
      }

      throw Exception('添加用药信息失败');
    } catch (e) {
      Logger.e('添加用药信息API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新用药信息
  Future<Medication> updateMedication(int medicationId, Medication medication) async {
    try {
      final response = await _apiClient.put(
        '/health-records/medications/$medicationId',
        data: medication.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Medication.fromJson(data);
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
