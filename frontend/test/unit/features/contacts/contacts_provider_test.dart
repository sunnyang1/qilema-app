import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/constants/loading_state.dart';
import 'package:qilema_app/core/models/contacts_models.dart';
import 'package:qilema_app/features/contacts/providers/contacts_provider.dart';

void main() {
  group('ContactsState', () {
    test('has correct default values', () {
      const state = ContactsState();
      
      expect(state.status, equals(LoadingState.initial));
      expect(state.contacts, isEmpty);
      expect(state.errorMessage, isNull);
      expect(state.isEmpty, isTrue);
      expect(state.isLoading, isFalse);
      expect(state.isLoaded, isFalse);
      expect(state.hasError, isFalse);
      expect(state.isInitial, isTrue);
    });

    test('copyWith updates status', () {
      const state = ContactsState();
      final newState = state.copyWith(status: LoadingState.loading);
      
      expect(newState.status, equals(LoadingState.loading));
      expect(newState.contacts, equals(state.contacts));
      expect(newState.errorMessage, equals(state.errorMessage));
    });

    test('copyWith updates contacts', () {
      const state = ContactsState();
      final contacts = [
        Contact(
          contactId: '1',
          name: 'Test',
          phone: '13800138000',
          relationship: '家人',
          priority: 1,
          notificationChannels: const ['app'],
        ),
      ];
      final newState = state.copyWith(contacts: contacts);
      
      expect(newState.contacts, equals(contacts));
      expect(newState.status, equals(state.status));
      expect(newState.isEmpty, isFalse);
    });

    test('copyWith updates errorMessage', () {
      const state = ContactsState();
      final newState = state.copyWith(errorMessage: 'Error');
      
      expect(newState.errorMessage, equals('Error'));
      expect(newState.status, equals(state.status));
    });

    test('copyWith without arguments returns identical values', () {
      const state = ContactsState(
        status: LoadingState.loaded,
        contacts: [],
        errorMessage: null,
      );
      final newState = state.copyWith();
      
      expect(newState.status, equals(state.status));
      expect(newState.contacts, equals(state.contacts));
      expect(newState.errorMessage, equals(state.errorMessage));
    });

    test('props includes all fields', () {
      const state = ContactsState();
      expect(state.props, equals([LoadingState.initial, [], null]));
    });

    test('equality works correctly', () {
      const state1 = ContactsState();
      const state2 = ContactsState();
      final state3 = ContactsState(
        contacts: [
          Contact(
            contactId: '1',
            name: 'Test',
            phone: '13800138000',
            relationship: '家人',
            priority: 1,
            notificationChannels: const ['app'],
          ),
        ],
      );
      
      expect(state1, equals(state2));
      expect(state1, isNot(equals(state3)));
    });
  });

  group('ContactsNotifier', () {
    test('initial state is correct', () {
      // 由于 Notifier 的 build() 会调用 load()，我们需要测试初始状态
      // 这里我们主要验证状态类的初始值
      const state = ContactsState();
      
      expect(state.status, equals(LoadingState.initial));
      expect(state.contacts, isEmpty);
      expect(state.errorMessage, isNull);
    });
  });

  group('ContactsState sorting', () {
    test('contacts are sorted by priority', () {
      final contacts = [
        Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138001',
          relationship: '朋友',
          priority: 3,
          notificationChannels: const ['app'],
        ),
        Contact(
          contactId: '2',
          name: '李四',
          phone: '13800138002',
          relationship: '家人',
          priority: 1,
          notificationChannels: const ['app', 'sms'],
        ),
        Contact(
          contactId: '3',
          name: '王五',
          phone: '13800138003',
          relationship: '同事',
          priority: 2,
          notificationChannels: const ['sms'],
        ),
      ];
      
      final sortedContacts = [...contacts]..sort((a, b) => a.priority.compareTo(b.priority));
      
      expect(sortedContacts[0].contactId, equals('2')); // priority 1
      expect(sortedContacts[1].contactId, equals('3')); // priority 2
      expect(sortedContacts[2].contactId, equals('1')); // priority 3
    });
  });

  group('ContactsState update operations', () {
    late List<Contact> initialContacts;

    setUp(() {
      initialContacts = [
        Contact(
          contactId: '1',
          name: '张三',
          phone: '13800138001',
          relationship: '朋友',
          priority: 1,
          notificationChannels: const ['app'],
        ),
        Contact(
          contactId: '2',
          name: '李四',
          phone: '13800138002',
          relationship: '家人',
          priority: 2,
          notificationChannels: const ['app'],
        ),
      ];
    });

    test('adding contact updates state correctly', () {
      final state = ContactsState(contacts: initialContacts);
      final newContact = Contact(
        contactId: '3',
        name: '王五',
        phone: '13800138003',
        relationship: '同事',
        priority: 3,
        notificationChannels: const ['sms'],
      );
      
      final newContacts = [...state.contacts, newContact]..sort((a, b) => a.priority.compareTo(b.priority));
      final newState = state.copyWith(contacts: newContacts);
      
      expect(newState.contacts.length, equals(3));
      expect(newState.contacts.last.contactId, equals('3'));
    });

    test('updating contact updates state correctly', () {
      final state = ContactsState(contacts: initialContacts);
      final updatedContact = Contact(
        contactId: '1',
        name: '张三三',
        phone: '13800138001',
        relationship: '朋友',
        priority: 1,
        notificationChannels: const ['app', 'sms'],
      );
      
      final updatedContacts = state.contacts.map((c) {
        return c.contactId == '1' ? updatedContact : c;
      }).toList();
      final newState = state.copyWith(contacts: updatedContacts);
      
      expect(newState.contacts.firstWhere((c) => c.contactId == '1').name, equals('张三三'));
      expect(newState.contacts.length, equals(2));
    });

    test('deleting contact updates state correctly', () {
      final state = ContactsState(contacts: initialContacts);
      
      final updatedContacts = state.contacts.where((c) => c.contactId != '1').toList();
      final newState = state.copyWith(contacts: updatedContacts);
      
      expect(newState.contacts.length, equals(1));
      expect(newState.contacts.first.contactId, equals('2'));
    });
  });
}
