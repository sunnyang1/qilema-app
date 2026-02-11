library;

import 'package:equatable/equatable.dart';

/// 紧急联系人数据模型
class Contact extends Equatable {
  /// 联系人ID
  final String contactId;

  /// 姓名
  final String name;

  /// 电话号码
  final String phone;

  /// 关系（家人、朋友等）
  final String relationship;

  /// 优先级（1-5，1最高）
  final int priority;

  /// 通知渠道（app、sms、email等）
  final List<String> notificationChannels;

  const Contact({
    required this.contactId,
    required this.name,
    required this.phone,
    required this.relationship,
    required this.priority,
    this.notificationChannels = const ['app'],
  });

  @override
  List<Object?> get props => [
        contactId,
        name,
        phone,
        relationship,
        priority,
        notificationChannels,
      ];

  factory Contact.fromJson(Map<String, dynamic> json) {
    return Contact(
      contactId: json['contact_id'] ?? '',
      name: json['name'] ?? '',
      phone: json['phone'] ?? '',
      relationship: json['relationship'] ?? '家人',
      priority: json['priority'] ?? 1,
      notificationChannels:
          (json['notification_channels'] as List?)?.cast<String>() ?? ['app'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'phone': phone,
      'relationship': relationship,
      'priority': priority,
      'notification_channels': notificationChannels,
    };
  }

  Contact copyWith({
    String? contactId,
    String? name,
    String? phone,
    String? relationship,
    int? priority,
    List<String>? notificationChannels,
  }) {
    return Contact(
      contactId: contactId ?? this.contactId,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      relationship: relationship ?? this.relationship,
      priority: priority ?? this.priority,
      notificationChannels: notificationChannels ?? this.notificationChannels,
    );
  }
}
