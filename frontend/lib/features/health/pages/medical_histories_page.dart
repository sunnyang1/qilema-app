import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/health/providers/health_provider.dart';
import 'package:qilema_app/features/health/services/health_api.dart';

/// 病史管理页面
class MedicalHistoriesPage extends ConsumerWidget {
  const MedicalHistoriesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('病史记录'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : healthState.medicalHistories.isEmpty
              ? _buildEmptyState(context)
              : _buildHistoryList(healthState.medicalHistories),
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
          Icon(Icons.history, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            '暂无病史记录',
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

  Widget _buildHistoryList(List<MedicalHistory> histories) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: histories.length,
      itemBuilder: (context, index) {
        final history = histories[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: AppColors.primary.withValues(alpha: 0.1),
              child: Icon(Icons.history, color: AppColors.primary),
            ),
            title: Text(
              history.diseaseName,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (history.diagnosisDate != null) ...[
                  Text('诊断日期: ${history.diagnosisDate}'),
                ],
                if (history.isChronic)
                  const Text(
                    '慢性病',
                    style: TextStyle(color: AppColors.warning, fontWeight: FontWeight.w500),
                  ),
              ],
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (history.severity != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getSeverityColor(history.severity!),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      history.severity!,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                  ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: () => _showAddEditDialog(context, null, history),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: AppColors.error),
                  onPressed: () => _showDeleteConfirmDialog(context, ref, history),
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
        return Colors.green;
      case '中等':
        return Colors.orange;
      case '严重':
        return AppColors.error;
      default:
        return Colors.grey;
    }
  }

  void _showAddEditDialog(
    BuildContext context,
    WidgetRef? ref, [
    MedicalHistory? history,
  ]) async {
    final formKey = GlobalKey<FormState>();
    final diseaseNameController = TextEditingController(text: history?.diseaseName ?? '');
    final diagnosisDateController = TextEditingController(text: history?.diagnosisDate ?? '');
    final descriptionController = TextEditingController(text: history?.description ?? '');
    String? selectedSeverity = history?.severity;
    bool isChronic = history?.isChronic ?? false;

    await showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(history == null ? '添加病史记录' : '编辑病史记录'),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: diseaseNameController,
                    decoration: const InputDecoration(
                      labelText: '疾病名称 *',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请输入疾病名称';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: diagnosisDateController,
                    decoration: const InputDecoration(
                      labelText: '诊断日期',
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
                        diagnosisDateController.text = date.toIso8601String().split('T')[0];
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: descriptionController,
                    decoration: const InputDecoration(
                      labelText: '详细描述',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 3,
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
                  const SizedBox(height: 16),
                  CheckboxListTile(
                    title: const Text('慢性病'),
                    value: isChronic,
                    onChanged: (value) {
                      setState(() {
                        isChronic = value ?? false;
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

                final newHistory = MedicalHistory(
                  id: history?.id ?? 0,
                  healthRecordId: history?.healthRecordId ?? 0,
                  diseaseName: diseaseNameController.text.trim(),
                  diagnosisDate: diagnosisDateController.text.trim().isEmpty
                      ? null
                      : diagnosisDateController.text.trim(),
                  description: descriptionController.text.trim().isEmpty
                      ? null
                      : descriptionController.text.trim(),
                  severity: selectedSeverity,
                  isChronic: isChronic,
                );

                try {
                  if (history == null) {
                    await ref!.read(healthProvider.notifier).addMedicalHistory(newHistory);
                  } else {
                    await ref!.read(healthProvider.notifier)
                        .updateMedicalHistory(history.id, newHistory);
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

  void _showDeleteConfirmDialog(BuildContext context, WidgetRef ref, MedicalHistory history) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除"${history.diseaseName}"这条病史记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await ref.read(healthProvider.notifier)
                    .deleteMedicalHistory(history.id);
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
