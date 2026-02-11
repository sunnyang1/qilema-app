library;

import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/contacts_models.dart';

void main() {
  group('Contact', () {
    group('Constructor', () {
      test('should create Contact with all fields', () {
        // When
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app', 'sms'],
        );

        // Then
        expect(contact.contactId, '1');
        expect(contact.name, '张三');
        expect(contact.phone, '13800138000');
        expect(contact.relationship, '家人');
        expect(contact.priority, 1);
        expect(contact.notificationChannels, ['app', 'sms']);
      });

      test('should use default notificationChannels if not provided', () {
        // When
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // Then
        expect(contact.notificationChannels, ['app']);
      });
    });

    group('fromJson', () {
      test('should parse JSON with all fields', () {
        // Given
        final json = {
          'contact_id': '1',
          'name': '张三',
          'phone': '13800138000',
          'relationship': '家人',
          'priority': 1,
          'notification_channels': ['app', 'sms'],
        };

        // When
        final contact = Contact.fromJson(json);

        // Then
        expect(contact.contactId, '1');
        expect(contact.name, '张三');
        expect(contact.phone, '13800138000');
        expect(contact.relationship, '家人');
        expect(contact.priority, 1);
        expect(contact.notificationChannels, ['app', 'sms']);
      });

      test('should use defaults when fields are missing', () {
        // Given
        final json = {
          'contact_id': '1',
          'name': '张三',
          'phone': '13800138000',
        };

        // When
        final contact = Contact.fromJson(json);

        // Then
        expect(contact.relationship, '家人');
        expect(contact.priority, 1);
        expect(contact.notificationChannels, ['app']);
      });

      test('should handle null values in JSON', () {
        // Given
        final json = {
          'contact_id': null,
          'name': null,
          'phone': null,
        };

        // When
        final contact = Contact.fromJson(json);

        // Then
        expect(contact.contactId, '');
        expect(contact.name, '');
        expect(contact.phone, '');
      });

      test('should handle null notification_channels', () {
        // Given
        final json = {
          'contact_id': '1',
          'name': '张三',
          'phone': '13800138000',
          'notification_channels': null,
        };

        // When
        final contact = Contact.fromJson(json);

        // Then
        expect(contact.notificationChannels, ['app']);
      });
    });

    group('toJson', () {
      test('should serialize all fields except contactId', () {
        // Given
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app', 'sms'],
        );

        // When
        final json = contact.toJson();

        // Then
        expect(json['name'], '张三');
        expect(json['phone'], '13800138000');
        expect(json['relationship'], '家人');
        expect(json['priority'], 1);
        expect(json['notification_channels'], ['app', 'sms']);
      });

      test('should not include contactId in JSON', () {
        // Given
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // When
        final json = contact.toJson();

        // Then
        expect(json.containsKey('contact_id'), false);
      });
    });

    group('copyWith', () {
      test('should create new Contact with updated values', () {
        // Given
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // When
        final updated = contact.copyWith(
          name: '李四',
          priority: 2,
        );

        // Then
        expect(updated.contactId, '1');
        expect(updated.name, '李四');
        expect(updated.phone, '13800138000');
        expect(updated.relationship, '家人');
        expect(updated.priority, 2);
      });

      test('should copy all fields when all provided', () {
        // Given
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app'],
        );

        // When
        final updated = contact.copyWith(
          contactId: '2',
          name: '李四',
          phone: '13900139000',
          relationship: '朋友',
          priority: 2,
          notificationChannels: ['app', 'sms'],
        );

        // Then
        expect(updated.contactId, '2');
        expect(updated.name, '李四');
        expect(updated.phone, '13900139000');
        expect(updated.relationship, '朋友');
        expect(updated.priority, 2);
        expect(updated.notificationChannels, ['app', 'sms']);
      });

      test('should keep original values when null provided', () {
        // Given
        final contact = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // When
        final updated = contact.copyWith();

        // Then
        expect(updated.contactId, '1');
        expect(updated.name, '张三');
        expect(updated.phone, '13800138000');
        expect(updated.relationship, '家人');
        expect(updated.priority, 1);
      });
    });

    group('Equality', () {
      test('should be equal when all fields match', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app'],
        );
        final contact2 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app'],
        );

        // Then
        expect(contact1, equals(contact2));
        expect(contact1.hashCode, equals(contact2.hashCode));
      });

      test('should not be equal when contactId differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );
        final contact2 = Contact(
          contactId: '2',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });

      test('should not be equal when name differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );
        final contact2 = Contact(
          contactId: '1',
          name: '李四',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });

      test('should not be equal when phone differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );
        final contact2 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13900139000',
          relationship: '家人',
          priority: 1,
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });

      test('should not be equal when relationship differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );
        final contact2 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '朋友',
          priority: 1,
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });

      test('should not be equal when priority differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
        );
        final contact2 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 2,
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });

      test('should not be equal when notificationChannels differs', () {
        // Given
        final contact1 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['app'],
        );
        final contact2 = Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: ['sms'],
        );

        // Then
        expect(contact1, isNot(equals(contact2)));
      });
    });
  });
}
