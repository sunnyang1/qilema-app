import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/base_state.dart';
import 'package:qilema_app/core/providers/base_notifier.dart';
import 'package:qilema_app/core/constants/loading_state.dart';
import 'package:qilema_app/features/contacts/services/contacts_api.dart';

/// 联系人状态类
base class ContactsState extends BaseState {
  final List<Contact> contacts;

  const ContactsState({
    super.status = LoadingState.initial,
    this.contacts = const [],
    super.errorMessage,
  });

  @override
  ContactsState copyWith({
    LoadingState? status,
    List<Contact>? contacts,
    String? errorMessage,
  }) {
    return ContactsState(
      status: status ?? this.status,
      contacts: contacts ?? this.contacts,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isEmpty => contacts.isEmpty;

  @override
  List<Object?> get props => [status, contacts, errorMessage];
}

/// 联系人状态管理器
base class ContactsNotifier extends Notifier<ContactsState> with BaseNotifierMixin<ContactsState> {
  late final ContactsApi _api;

  @override
  ContactsState build() {
    _api = ContactsApi();
    load();
    return const ContactsState();
  }

  /// 加载联系人列表
  @override
  Future<void> load() async {
    state = state.copyWith(status: LoadingState.loading);
    try {
      final contacts = await _api.getContacts();
      // 按优先级排序
      contacts.sort((a, b) => a.priority.compareTo(b.priority));
      state = ContactsState(
        status: LoadingState.loaded,
        contacts: contacts,
      );
    } catch (e) {
      state = state.copyWith(
        status: LoadingState.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 添加联系人
  Future<void> addContact(Contact contact) async {
    try {
      final newContact = await _api.addContact(contact);
      state = state.copyWith(
        contacts: [...state.contacts, newContact]..sort((a, b) => a.priority.compareTo(b.priority)),
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 更新联系人
  Future<void> updateContact(String contactId, Contact contact) async {
    try {
      final updatedContact = await _api.updateContact(contactId, contact);
      final updatedContacts = state.contacts.map((c) {
        return c.contactId == contactId ? updatedContact : c;
      }).toList();
      updatedContacts.sort((a, b) => a.priority.compareTo(b.priority));
      state = state.copyWith(contacts: updatedContacts);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 删除联系人
  Future<void> deleteContact(String contactId) async {
    try {
      await _api.deleteContact(contactId);
      final updatedContacts = state.contacts.where((c) => c.contactId != contactId).toList();
      state = state.copyWith(contacts: updatedContacts);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }
}

/// 联系人状态Provider
final contactsProvider = NotifierProvider<ContactsNotifier, ContactsState>(ContactsNotifier.new);
