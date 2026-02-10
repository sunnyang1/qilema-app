import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/contacts/services/contacts_api.dart';

/// 联系人状态
enum ContactsStatus { initial, loading, loaded, error }

/// 联系人状态类
class ContactsState {
  final ContactsStatus status;
  final List<Contact> contacts;
  final String? errorMessage;

  const ContactsState({
    this.status = ContactsStatus.initial,
    this.contacts = const [],
    this.errorMessage,
  });

  ContactsState copyWith({
    ContactsStatus? status,
    List<Contact>? contacts,
    String? errorMessage,
  }) {
    return ContactsState(
      status: status ?? this.status,
      contacts: contacts ?? this.contacts,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isLoading => status == ContactsStatus.loading;
  bool get isLoaded => status == ContactsStatus.loaded;
  bool get hasError => status == ContactsStatus.error;
  bool get isEmpty => contacts.isEmpty;
}

/// 联系人状态管理器
class ContactsNotifier extends StateNotifier<ContactsState> {
  final ContactsApi _api = ContactsApi();

  ContactsNotifier() : super(const ContactsState()) {
    _loadContacts();
  }

  /// 加载联系人列表
  Future<void> _loadContacts() async {
    state = state.copyWith(status: ContactsStatus.loading);
    try {
      final contacts = await _api.getContacts();
      // 按优先级排序
      contacts.sort((a, b) => a.priority.compareTo(b.priority));
      state = ContactsState(
        status: ContactsStatus.loaded,
        contacts: contacts,
      );
    } catch (e) {
      state = state.copyWith(
        status: ContactsStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 刷新联系人列表
  Future<void> refresh() async {
    await _loadContacts();
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
final contactsProvider = StateNotifierProvider<ContactsNotifier, ContactsState>((ref) {
  return ContactsNotifier();
});
