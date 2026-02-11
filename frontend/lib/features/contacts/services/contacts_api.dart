import 'package:qilema_app/core/models/contacts_models.dart';
import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 紧急联系人API服务
class ContactsApi {
  final ApiClient _apiClient = ApiClient();

  /// 获取联系人列表
  Future<List<Contact>> getContacts() async {
    try {
      final response = await _apiClient.get('/contacts');

      if (response.statusCode == 200) {
        final data = response.data['data'];
        final items = data['items'] as List?;
        return items?.map((item) => Contact.fromJson(item)).toList() ?? [];
      }

      throw Exception('获取联系人列表失败');
    } catch (e) {
      Logger.e('获取联系人列表API调用失败', error: e);
      rethrow;
    }
  }

  /// 添加联系人
  Future<Contact> addContact(Contact contact) async {
    try {
      final response = await _apiClient.post(
        '/contacts',
        data: contact.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Contact.fromJson(data);
      }

      throw Exception('添加联系人失败');
    } catch (e) {
      Logger.e('添加联系人API调用失败', error: e);
      rethrow;
    }
  }

  /// 更新联系人
  Future<Contact> updateContact(String contactId, Contact contact) async {
    try {
      final response = await _apiClient.put(
        '/contacts/$contactId',
        data: contact.toJson(),
      );

      if (response.statusCode == 200) {
        final data = response.data['data'];
        return Contact.fromJson(data);
      }

      throw Exception('更新联系人失败');
    } catch (e) {
      Logger.e('更新联系人API调用失败', error: e);
      rethrow;
    }
  }

  /// 删除联系人
  Future<bool> deleteContact(String contactId) async {
    try {
      final response = await _apiClient.delete('/contacts/$contactId');

      if (response.statusCode == 200) {
        return true;
      }

      throw Exception('删除联系人失败');
    } catch (e) {
      Logger.e('删除联系人API调用失败', error: e);
      rethrow;
    }
  }
}
