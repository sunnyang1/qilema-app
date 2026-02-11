import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/health_models.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/health/providers/health_provider.dart';
import 'package:qilema_app/features/health/services/health_api.dart';

/// 过敏史管理页面
class AllergiesPage extends ConsumerWidget {
  const AllergiesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('过敏史'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : healthState.allergies.isEmpty
              ? _buildEmptyState(context)
              : _buildAllergyList(context, healthState.allergies, ref),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddEditDialog(context, ref),
        backgroundColor: AppColors.error,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.warning, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            '暂无过敏记录',
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            '点击右下角按钮添加',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildAllergyList(BuildContext context, List<Allergy> allergies, WidgetRef ref) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: allergies.length,
      itemBuilder: (context, index) {
        final allergy = allergies[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: _getSeverityBackgroundColor(allergy.severity),
              child: Icon(
                Icons.warning,
                color: _getSeverityIconColor(allergy.severity),
              ),
            ),
            title: Text(
              allergy.allergen,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (allergy.allergicReaction != null) ...[
                  Text('过敏反应: ${allergy.allergicReaction}'),
                ],
                if (allergy.discoveredDate != null) ...[
                  Text('发现日期: ${allergy.discoveredDate}'),
                ],
              ],
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (allergy.severity != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getSeverityColor(allergy.severity!),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      allergy.severity!,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                  ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () => _showAddEditDialog(context, null, allergy),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: AppColors.error),
                  onPressed: () => _showDeleteConfirmDialog(context, ref, allergy),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity) {
      case '轻微':
        return Colors.orange;
      case '中等':
        return Colors.deepOrange;
      case '严重':
        return AppColors.error;
      default:
        return Colors.grey;
    }
  }

  Color _getSeverityBackgroundColor(String? severity) {
    switch (severity) {
      case '轻微':
        return Colors.orange.withValues(alpha: 0.1);
      case '中等':
        return Colors.deepOrange.withValues(alpha: 0.1);
      case '严重':
        return AppColors.error.withValues(alpha: 0.1);
      default:
        return Colors.grey.withValues(alpha: 0.1);
    }
  }

  Color _getSeverityIconColor(String? severity) {
    switch (severity) {
      case '轻微':
        return Colors.orange;
      case '中等':
        return Colors.deepOrange;
      case '严重':
        return AppColors.error;
      default:
        return Colors.grey;
    }
  }

  void _showAddEditDialog(
    BuildContext context,
    WidgetRef? ref, [
    Allergy? allergy,
  ]) async {
    final formKey = GlobalKey<FormState>();
    final allergenController = TextEditingController(text: allergy?.allergen ?? '');
    final reactionController = TextEditingController(text: allergy?.allergicReaction ?? '');
    final discoveredDateController = TextEditingController(text: allergy?.discoveredDate ?? '');
    final notesController = TextEditingController(text: allergy?.notes ?? '');
    String? selectedSeverity = allergy?.severity;

    await showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(allergy == null ? '添加过敏史' : '编辑过敏史'),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: allergenController,
                    decoration: const InputDecoration(
                      labelText: '过敏原 *',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请输入过敏原';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: reactionController,
                    decoration: const InputDecoration(
                      labelText: '过敏反应',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: discoveredDateController,
                    decoration: const InputDecoration(
                      labelText: '发现日期',
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    onTap: () async {
                      final date = await showDatePicker(
                        context: context,
                        initialDate: DateTime.now(),
                        firstDate: DateTime(1900),
                        lastDate: DateTime.now(),
                      );
                      if (date != null) {
                        discoveredDateController.text = date.toIso8601String().split('T')[0];
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: notesController,
                    decoration: const InputDecoration(
                      labelText: '备注',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: '严重程度',
                      border: OutlineInputBorder(),
                    ),
                    value: selectedSeverity,
                    items: const ['轻微', '中等', '严重']
                        .map((severity) => DropdownMenuItem<String>(
                              value: severity,
                              child: Text(severity),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedSeverity = value;
                      });
                    },
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;

                final newAllergy = Allergy(
                  id: allergy?.id ?? 0,
                  healthRecordId: allergy?.healthRecordId ?? 0,
                  allergen: allergenController.text.trim(),
                  allergicReaction: reactionController.text.trim().isEmpty
                      ? null
                      : reactionController.text.trim(),
                  discoveredDate: discoveredDateController.text.trim().isEmpty
                      ? null
                      : discoveredDateController.text.trim(),
                  notes: notesController.text.trim().isEmpty
                      ? null
                      : notesController.text.trim(),
                  severity: selectedSeverity,
                );

                try {
                  if (allergy == null) {
                    await ref!.read(healthProvider.notifier).addAllergy(newAllergy);
                  } else {
                    await ref!.read(healthProvider.notifier)
                        .updateAllergy(allergy.id, newAllergy);
                  }
                  if (dialogContext.mounted) {
                    Navigator.pop(dialogContext);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('保存成功')),
                    );
                  }
                } catch (e) {
                  if (dialogContext.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('保存失败: $e')),
                    );
                  }
                }
              },
              child: const Text('保存'),
            ),
          ],
        ),
      ),
    );
  }

  void _showDeleteConfirmDialog(BuildContext context, WidgetRef ref, Allergy allergy) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除"${allergy.allergen}"这条过敏记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await ref.read(healthProvider.notifier)
                    .deleteAllergy(allergy.id);
                if (dialogContext.mounted) {
                  Navigator.pop(dialogContext);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('删除成功')),
                  );
                }
              } catch (e) {
                if (dialogContext.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('删除失败: $e')),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }
}
