import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/contacts_models.dart';
import 'package:qilema_app/features/contacts/providers/contacts_provider.dart';

/// 添加/编辑联系人页面
class ContactEditPage extends ConsumerStatefulWidget {
  const ContactEditPage({super.key});

  @override
  ConsumerState<ContactEditPage> createState() => _ContactEditPageState();
}

class _ContactEditPageState extends ConsumerState<ContactEditPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  int _relationship = 0;
  int _priority = 1;
  List<String> _notificationChannels = ['app'];
  Contact? _editingContact;

  final List<String> _relationships = [
    '家人',
    '配偶',
    '父母',
    '子女',
    '朋友',
    '同事',
    '其他',
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // 检查是否是编辑模式
    final state = ModalRoute.of(context)?.settings.arguments as Contact?;
    if (state != null && _editingContact == null) {
      _editingContact = state;
      _nameController.text = state.name;
      _phoneController.text = state.phone;
      _relationship = _relationships.indexOf(state.relationship);
      _priority = state.priority;
      _notificationChannels = List.from(state.notificationChannels);
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _saveContact() async {
    if (_formKey.currentState?.validate() != true) {
      return;
    }

    final contact = Contact(
      contactId: _editingContact?.contactId ?? '',
      name: _nameController.text.trim(),
      phone: _phoneController.text.trim(),
      relationship: _relationships[_relationship],
      priority: _priority,
      notificationChannels: _notificationChannels,
    );

    try {
      if (_editingContact != null) {
        // 更新联系人
        await ref.read(contactsProvider.notifier).updateContact(
          _editingContact!.contactId,
          contact,
        );
      } else {
        // 添加联系人
        await ref.read(contactsProvider.notifier).addContact(contact);
      }

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_editingContact != null ? '联系人已更新' : '联系人已添加')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('操作失败：${e.toString()}')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_editingContact != null ? '编辑联系人' : '添加联系人'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        elevation: 0,
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              // 姓名
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: '姓名',
                  prefixIcon: Icon(Icons.person),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return '请输入姓名';
                  }
                  if (value.trim().length < 2) {
                    return '姓名至少2个字符';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // 手机号
              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: '手机号',
                  prefixIcon: Icon(Icons.phone),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return '请输入手机号';
                  }
                  final phoneRegex = RegExp(r'^1[3-9]\d{9}$');
                  if (!phoneRegex.hasMatch(value.trim())) {
                    return '请输入有效的手机号';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // 关系
              DropdownButtonFormField<int>(
                initialValue: _relationship,
                decoration: const InputDecoration(
                  labelText: '关系',
                  prefixIcon: Icon(Icons.family_restroom),
                  border: OutlineInputBorder(),
                ),
                items: _relationships
                    .asMap()
                    .entries
                    .map((entry) => DropdownMenuItem(
                          value: entry.key,
                          child: Text(entry.value),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _relationship = value!;
                  });
                },
              ),
              const SizedBox(height: 24),

              // 优先级
              const Text(
                '优先级',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              ToggleButtons(
                direction: Axis.horizontal,
                onPressed: (int index) {
                  setState(() {
                    _priority = index + 1;
                  });
                },
                borderRadius: const BorderRadius.all(Radius.circular(8)),
                selectedBorderColor: Theme.of(context).colorScheme.primary,
                selectedColor: Colors.white,
                fillColor: Theme.of(context).colorScheme.primary,
                color: Theme.of(context).colorScheme.onSurface,
                constraints: const BoxConstraints(
                  minHeight: 40.0,
                  minWidth: 60.0,
                ),
                isSelected: [1, 2, 3, 4, 5].map((priority) => _priority == priority).toList(),
                children: [1, 2, 3, 4, 5].map((priority) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0),
                    child: Text('$priority'),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // 通知渠道
              const Text(
                '通知渠道',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              CheckboxListTile(
                title: const Text('App推送'),
                value: _notificationChannels.contains('app'),
                onChanged: (value) {
                  setState(() {
                    if (value!) {
                      _notificationChannels.add('app');
                    } else {
                      _notificationChannels.remove('app');
                    }
                  });
                },
              ),
              CheckboxListTile(
                title: const Text('短信'),
                value: _notificationChannels.contains('sms'),
                onChanged: (value) {
                  setState(() {
                    if (value!) {
                      _notificationChannels.add('sms');
                    } else {
                      _notificationChannels.remove('sms');
                    }
                  });
                },
              ),
              CheckboxListTile(
                title: const Text('电话'),
                value: _notificationChannels.contains('phone'),
                onChanged: (value) {
                  setState(() {
                    if (value!) {
                      _notificationChannels.add('phone');
                    } else {
                      _notificationChannels.remove('phone');
                    }
                  });
                },
              ),
              const SizedBox(height: 32),

              // 保存按钮
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _saveContact,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    '保存',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
