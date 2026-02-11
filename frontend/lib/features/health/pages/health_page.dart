import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/core/models/health_models.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/health/providers/health_provider.dart';

/// 健康档案基本信息页面
class HealthPage extends ConsumerStatefulWidget {
  const HealthPage({super.key});

  @override
  ConsumerState<HealthPage> createState() => _HealthPageState();
}

class _HealthPageState extends ConsumerState<HealthPage> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _ageController;
  late TextEditingController _heightController;
  late TextEditingController _weightController;
  late TextEditingController _emergencyNameController;
  late TextEditingController _emergencyPhoneController;
  late TextEditingController _emergencyRelationController;
  String? _selectedGender;
  String? _selectedBloodType;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _ageController = TextEditingController();
    _heightController = TextEditingController();
    _weightController = TextEditingController();
    _emergencyNameController = TextEditingController();
    _emergencyPhoneController = TextEditingController();
    _emergencyRelationController = TextEditingController();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _emergencyNameController.dispose();
    _emergencyPhoneController.dispose();
    _emergencyRelationController.dispose();
    super.dispose();
  }

  void _initForm(HealthRecord record) {
    _nameController.text = record.realName ?? '';
    _ageController.text = record.age?.toString() ?? '';
    _heightController.text = record.height?.toString() ?? '';
    _weightController.text = record.weight?.toString() ?? '';
    _emergencyNameController.text = record.emergencyContactName ?? '';
    _emergencyPhoneController.text = record.emergencyContactPhone ?? '';
    _emergencyRelationController.text = record.emergencyContactRelation ?? '';
    _selectedGender = record.gender;
    _selectedBloodType = record.bloodType;
  }

  Future<void> _saveForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    try {
      final healthState = ref.read(healthProvider);
      final record = HealthRecord(
        id: healthState.healthRecord?.id ?? '',
        userId: healthState.healthRecord?.userId ?? '',
        realName: _nameController.text.trim(),
        gender: _selectedGender,
        bloodType: _selectedBloodType,
        height: double.tryParse(_heightController.text.trim()),
        weight: double.tryParse(_weightController.text.trim()),
        age: int.tryParse(_ageController.text.trim()),
        emergencyContactName: _emergencyNameController.text.trim(),
        emergencyContactPhone: _emergencyPhoneController.text.trim(),
        emergencyContactRelation: _emergencyRelationController.text.trim(),
      );

      await ref.read(healthProvider.notifier).updateHealthRecord(record);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('健康档案保存成功')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final healthState = ref.watch(healthProvider);

    // 当健康档案加载完成后，初始化表单
    if (healthState.healthRecord != null && _nameController.text.isEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _initForm(healthState.healthRecord!);
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('健康档案'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(healthProvider.notifier).refresh();
            },
          ),
        ],
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : healthState.hasError
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text('加载失败'),
                      ElevatedButton(
                        onPressed: () {
                          ref.read(healthProvider.notifier).refresh();
                        },
                        child: const Text('重试'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 基本信息
                        _buildSection(
                          '基本信息',
                          [
                            _buildTextField(
                              _nameController,
                              '真实姓名',
                              Icons.person,
                              validator: (value) {
                                if (value == null || value.trim().isEmpty) {
                                  return '请输入真实姓名';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            _buildDropdown(
                              '性别',
                              ['男', '女', '其他'],
                              _selectedGender,
                              (value) {
                                setState(() {
                                  _selectedGender = value;
                                });
                              },
                              Icons.wc,
                            ),
                            const SizedBox(height: 16),
                            _buildTextField(
                              _ageController,
                              '年龄',
                              Icons.cake,
                              keyboardType: TextInputType.number,
                              validator: (value) {
                                if (value == null || value.trim().isEmpty) {
                                  return '请输入年龄';
                                }
                                final age = int.tryParse(value.trim());
                                if (age == null || age < 0 || age > 150) {
                                  return '请输入有效的年龄';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            _buildDropdown(
                              '血型',
                              ['A', 'B', 'O', 'AB', '其他'],
                              _selectedBloodType,
                              (value) {
                                setState(() {
                                  _selectedBloodType = value;
                                });
                              },
                              Icons.bloodtype,
                            ),
                            const SizedBox(height: 16),
                            Row(
                              children: [
                                Expanded(
                                  child: _buildTextField(
                                    _heightController,
                                    '身高 (cm)',
                                    Icons.height,
                                    keyboardType: TextInputType.number,
                                    validator: (value) {
                                      if (value != null && value.trim().isNotEmpty) {
                                        final height = double.tryParse(value.trim());
                                        if (height == null || height <= 0 || height > 300) {
                                          return '请输入有效的身高';
                                        }
                                      }
                                      return null;
                                    },
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: _buildTextField(
                                    _weightController,
                                    '体重 (kg)',
                                    Icons.monitor_weight,
                                    keyboardType: TextInputType.number,
                                    validator: (value) {
                                      if (value != null && value.trim().isNotEmpty) {
                                        final weight = double.tryParse(value.trim());
                                        if (weight == null || weight <= 0 || weight > 500) {
                                          return '请输入有效的体重';
                                        }
                                      }
                                      return null;
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),

                        const SizedBox(height: 24),

                        // 紧急联系人
                        _buildSection(
                          '紧急医疗联系人',
                          [
                            _buildTextField(
                              _emergencyNameController,
                              '联系人姓名',
                              Icons.contact_phone,
                            ),
                            const SizedBox(height: 16),
                            _buildTextField(
                              _emergencyPhoneController,
                              '联系人电话',
                              Icons.phone,
                              keyboardType: TextInputType.phone,
                            ),
                            const SizedBox(height: 16),
                            _buildTextField(
                              _emergencyRelationController,
                              '与患者关系',
                              Icons.family_restroom,
                            ),
                          ],
                        ),

                        const SizedBox(height: 24),

                        // 快速操作
                        _buildQuickActions(),

                        const SizedBox(height: 32),

                        // 保存按钮
                        SizedBox(
                          width: double.infinity,
                          height: 50,
                          child: ElevatedButton(
                            onPressed: _saveForm,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primary,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('保存', style: TextStyle(fontSize: 16)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 16),
        ...children,
      ],
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label,
    IconData icon, {
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        filled: true,
        fillColor: Colors.grey[50],
      ),
      keyboardType: keyboardType,
      validator: validator,
    );
  }

  Widget _buildDropdown(
    String label,
    List<String> items,
    String? value,
    Function(String?) onChanged,
    IconData icon,
  ) {
    return DropdownButtonFormField<String>(
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        filled: true,
        fillColor: Colors.grey[50],
      ),
      initialValue: value,
      items: items
          .map((item) => DropdownMenuItem<String>(
                value: item,
                child: Text(item),
              ))
          .toList(),
      onChanged: onChanged,
    );
  }

  Widget _buildQuickActions() {
    return Card(
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.history, color: AppColors.primary),
            title: const Text('病史记录'),
            subtitle: Text('${ref.watch(healthProvider).medicalHistories.length} 条记录'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              context.push('/medical-histories');
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.medication, color: AppColors.primary),
            title: const Text('用药信息'),
            subtitle: Text('${ref.watch(healthProvider).medications.length} 条记录'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              context.push('/medications');
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.warning, color: AppColors.error),
            title: const Text('过敏史'),
            subtitle: Text('${ref.watch(healthProvider).allergies.length} 条记录'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              context.push('/allergies');
            },
          ),
        ],
      ),
    );
  }
}
