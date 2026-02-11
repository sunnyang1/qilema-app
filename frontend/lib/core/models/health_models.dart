library;

import 'package:equatable/equatable.dart';

/// 健康档案基本信息
class HealthRecord extends Equatable {
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

  const HealthRecord({
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

  @override
  List<Object?> get props => [
        id, userId, realName, gender, bloodType,
        height, weight, age,
        emergencyContactName, emergencyContactPhone, emergencyContactRelation,
      ];

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
class MedicalHistory extends Equatable {
  final int id;
  final int healthRecordId;
  final String diseaseName;
  final String? diagnosisDate;
  final String? description;
  final String? severity;
  final bool isChronic;

  const MedicalHistory({
    required this.id,
    required this.healthRecordId,
    required this.diseaseName,
    this.diagnosisDate,
    this.description,
    this.severity,
    this.isChronic = false,
  });

  @override
  List<Object?> get props => [id, healthRecordId, diseaseName, diagnosisDate, description, severity, isChronic];

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
class MedicationInfo extends Equatable {
  final int id;
  final int healthRecordId;
  final String drugName;
  final String? dosage;
  final String? frequency;
  final String? startDate;
  final String? endDate;
  final bool isCurrent;
  final String? notes;

  const MedicationInfo({
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

  @override
  List<Object?> get props => [id, healthRecordId, drugName, dosage, frequency, startDate, endDate, isCurrent, notes];

  factory MedicationInfo.fromJson(Map<String, dynamic> json) {
    return MedicationInfo(
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
class Allergy extends Equatable {
  final int id;
  final int healthRecordId;
  final String allergen;
  final String? allergicReaction;
  final String? severity;
  final String? discoveredDate;
  final String? notes;

  const Allergy({
    required this.id,
    required this.healthRecordId,
    required this.allergen,
    this.allergicReaction,
    this.severity,
    this.discoveredDate,
    this.notes,
  });

  @override
  List<Object?> get props => [id, healthRecordId, allergen, allergicReaction, severity, discoveredDate, notes];

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
