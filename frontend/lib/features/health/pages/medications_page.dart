import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/health/providers/health_provider.dart';
import 'package:qilema_app/features/health/services/health_api.dart';

/// 用药信息管理页面
class MedicationsPage extends ConsumerWidget {
  const MedicationsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('用药信息'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : healthState.medications.isEmpty
              ? _buildEmptyState(context)
              : _buildMedicationList(healthState.medications),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddEditDialog(context, ref),
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.medication, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            '暂无用药记录',
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

  Widget _buildMedicationList(List<Medication> medications) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: medications.length,
      itemBuilder: (context, index) {
        final medication = medications[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: medication.isCurrent
                  ? AppColors.primary.withValues(alpha: 0.1)
                  : Colors.grey.withValues(alpha: 0.1),
              child: Icon(
                Icons.medication,
                color: medication.isCurrent ? AppColors.primary : Colors.grey,
              ),
            ),
            title: Text(
              medication.drugName,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (medication.dosage != null) Text('剂量: ${medication.dosage}'),
                if (medication.frequency != null) Text('频率: ${medication.frequency}'),
                if (medication.startDate != null) ...[
                  Text('开始日期: ${medication.startDate}'),
                ],
              ],
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (medication.isCurrent)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      '正在使用',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                  ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () => _showAddEditDialog(context, null, medication),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: AppColors.error),
                  onPressed: () => _showDeleteConfirmDialog(context, ref, medication),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showAddEditDialog(
    BuildContext context,
    WidgetRef? ref, [
    Medication? medication,
  ]) async {
    final formKey = GlobalKey<FormState>();
    final drugNameController = TextEditingController(text: medication?.drugName ?? '');
    final dosageController = TextEditingController(text: medication?.dosage ?? '');
    final frequencyController = TextEditingController(text: medication?.frequency ?? '');
    final startDateController = TextEditingController(text: medication?.startDate ?? '');
    final endDateController = TextEditingController(text: medication?.endDate ?? '');
    final notesController = TextEditingController(text: medication?.notes ?? '');
    bool isCurrent = medication?.isCurrent ?? false;

    await showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(medication == null ? '添加用药信息' : '编辑用药信息'),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: drugNameController,
                    decoration: const InputDecoration(
                      labelText: '药品名称 *',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请输入药品名称';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: dosageController,
                    decoration: const InputDecoration(
                      labelText: '剂量',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: frequencyController,
                    decoration: const InputDecoration(
                      labelText: '用药频率',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: startDateController,
                    decoration: const InputDecoration(
                      labelText: '开始用药日期',
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    onTap: () async {
                      final date = await showDatePicker(
                        context: context,
                        initialDate: DateTime.now(),
                        firstDate: DateTime(2000),
                        lastDate: DateTime.now().add(const Duration(days: 365 * 5)),
                      );
                      if (date != null) {
                        startDateController.text = date.toIso8601String().split('T')[0];
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: endDateController,
                    decoration: const InputDecoration(
                      labelText: '结束用药日期',
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    onTap: () async {
                      final date = await showDatePicker(
                        context: context,
                        initialDate: DateTime.now(),
                        firstDate: DateTime(2000),
                        lastDate: DateTime.now().add(const Duration(days: 365 * 10)),
                      );
                      if (date != null) {
                        endDateController.text = date.toIso8601String().split('T')[0];
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
                  CheckboxListTile(
                    title: const Text('正在使用'),
                    value: isCurrent,
                    onChanged: (value) {
                      setState(() {
                        isCurrent = value ?? false;
                      });
                    },
                    contentPadding: EdgeInsets.zero,
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

                final newMedication = Medication(
                  id: medication?.id ?? 0,
                  healthRecordId: medication?.healthRecordId ?? 0,
                  drugName: drugNameController.text.trim(),
                  dosage: dosageController.text.trim().isEmpty
                      ? null
                      : dosageController.text.trim(),
                  frequency: frequencyController.text.trim().isEmpty
                      ? null
                      : frequencyController.text.trim(),
                  startDate: startDateController.text.trim().isEmpty
                      ? null
                      : startDateController.text.trim(),
                  endDate: endDateController.text.trim().isEmpty
                      ? null
                      : endDateController.text.trim(),
                  isCurrent: isCurrent,
                  notes: notesController.text.trim().isEmpty
                      ? null
                      : notesController.text.trim(),
                );

                try {
                  if (medication == null) {
                    await ref!.read(healthProvider.notifier).addMedication(newMedication);
                  } else {
                    await ref!.read(healthProvider.notifier)
                        .updateMedication(medication.id, newMedication);
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

  void _showDeleteConfirmDialog(BuildContext context, WidgetRef ref, Medication medication) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除"${medication.drugName}"这条用药记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await ref.read(healthProvider.notifier)
                    .deleteMedication(medication.id);
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
