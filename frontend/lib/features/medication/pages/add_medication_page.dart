import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/features/medication/providers/medication_provider.dart';
import 'package:qilema_app/features/medication/services/medication_api.dart';

/// 添加用药提醒页面
class AddMedicationPage extends ConsumerStatefulWidget {
  const AddMedicationPage({super.key});

  @override
  ConsumerState<AddMedicationPage> createState() => _AddMedicationPageState();
}

class _AddMedicationPageState extends ConsumerState<AddMedicationPage> {
  final _formKey = GlobalKey<FormState>();
  
  // 表单数据
  String? _selectedMedicationId;
  String? _medicationName;
  String? _dosage;
  String? _unit;
  final List<String> _reminderTimes = ['08:00'];
  MedicationFrequency _frequency = MedicationFrequency.daily;
  final Set<int> _selectedWeekdays = <int>{};

  final List<TimeOfDay> _timeSelections = [const TimeOfDay(hour: 8, minute: 0)];

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(medicationProvider.notifier).loadAvailableMedications();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(medicationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('添加用药提醒'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.go('/medication'),
        ),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 药品选择
            _buildMedicationSelection(state),
            const SizedBox(height: 24),

            // 剂量设置
            _buildDosageSection(),
            const SizedBox(height: 24),

            // 提醒时间
            _buildReminderTimesSection(),
            const SizedBox(height: 24),

            // 频率设置
            _buildFrequencySection(),
            const SizedBox(height: 32),

            // 保存按钮
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: state.isProcessing ? null : _saveReminder,
                child: state.isProcessing
                    ? const CircularProgressIndicator()
                    : const Text('保存提醒'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 药品选择
  Widget _buildMedicationSelection(MedicationState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '选择药品',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        if (state.isLoadingMedications)
          const Center(child: CircularProgressIndicator())
        else if (state.availableMedications.isEmpty)
          TextFormField(
            decoration: const InputDecoration(
              labelText: '药品名称',
              hintText: '请输入药品名称',
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请输入药品名称';
              }
              return null;
            },
            onSaved: (value) => _medicationName = value,
          )
        else
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(
              labelText: '选择药品',
              border: OutlineInputBorder(),
            ),
            value: _selectedMedicationId,
            items: state.availableMedications.map((med) {
              return DropdownMenuItem(
                value: med.id,
                child: Text('${med.name} (${med.dosage}${med.unit})'),
              );
            }).toList(),
            onChanged: (value) {
              setState(() {
                _selectedMedicationId = value;
                if (value != null) {
                  final med = state.availableMedications.firstWhere((m) => m.id == value);
                  _medicationName = med.name;
                  _dosage = med.dosage;
                  _unit = med.unit;
                }
              });
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return '请选择药品';
              }
              return null;
            },
          ),
      ],
    );
  }

  /// 剂量设置
  Widget _buildDosageSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '剂量设置',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              flex: 2,
              child: TextFormField(
                decoration: const InputDecoration(
                  labelText: '剂量',
                  hintText: '如: 1、500',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                initialValue: _dosage,
                onChanged: (value) => _dosage = value,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              flex: 1,
              child: TextFormField(
                decoration: const InputDecoration(
                  labelText: '单位',
                  hintText: 'mg、粒',
                  border: OutlineInputBorder(),
                ),
                initialValue: _unit,
                onChanged: (value) => _unit = value,
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// 提醒时间设置
  Widget _buildReminderTimesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '提醒时间',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton.icon(
              onPressed: _addTimeSlot,
              icon: const Icon(Icons.add),
              label: const Text('添加时间'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...List.generate(_timeSelections.length, (index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _selectTime(index),
                    child: Text(
                      _timeSelections[index].format(context),
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
                if (_timeSelections.length > 1) ...[
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    onPressed: () => _removeTimeSlot(index),
                  ),
                ],
              ],
            ),
          );
        }),
      ],
    );
  }

  /// 频率设置
  Widget _buildFrequencySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '提醒频率',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        SegmentedButton<MedicationFrequency>(
          segments: const [
            ButtonSegment(
              value: MedicationFrequency.daily,
              label: Text('每天'),
            ),
            ButtonSegment(
              value: MedicationFrequency.weekly,
              label: Text('每周'),
            ),
          ],
          selected: {_frequency},
          onSelectionChanged: (Set<MedicationFrequency> newSelection) {
            setState(() {
              _frequency = newSelection.first;
            });
          },
        ),
        if (_frequency == MedicationFrequency.weekly) ...[
          const SizedBox(height: 16),
          const Text(
            '选择每周哪几天',
            style: TextStyle(fontSize: 14),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              _buildWeekdayChip(1, '周一'),
              _buildWeekdayChip(2, '周二'),
              _buildWeekdayChip(3, '周三'),
              _buildWeekdayChip(4, '周四'),
              _buildWeekdayChip(5, '周五'),
              _buildWeekdayChip(6, '周六'),
              _buildWeekdayChip(7, '周日'),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildWeekdayChip(int day, String label) {
    final isSelected = _selectedWeekdays.contains(day);
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          if (selected) {
            _selectedWeekdays.add(day);
          } else {
            _selectedWeekdays.remove(day);
          }
        });
      },
      selectedColor: Colors.blue.shade100,
    );
  }

  Future<void> _selectTime(int index) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _timeSelections[index],
    );
    if (picked != null) {
      setState(() {
        _timeSelections[index] = picked;
      });
    }
  }

  void _addTimeSlot() {
    if (_timeSelections.length < 5) {
      setState(() {
        _timeSelections.add(const TimeOfDay(hour: 12, minute: 0));
      });
    }
  }

  void _removeTimeSlot(int index) {
    setState(() {
      _timeSelections.removeAt(index);
    });
  }

  Future<void> _saveReminder() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_frequency == MedicationFrequency.weekly && _selectedWeekdays.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请至少选择一天')),
      );
      return;
    }

    _formKey.currentState!.save();

    // 转换时间为字符串
    final timeStrings = _timeSelections
        .map((t) => '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}')
        .toList();

    final success = await ref.read(medicationProvider.notifier).createReminder(
          medicationId: _selectedMedicationId ?? 'custom_${DateTime.now().millisecondsSinceEpoch}',
          medicationName: _medicationName!,
          dosage: _dosage,
          unit: _unit,
          reminderTimes: timeStrings,
          frequency: _frequency,
          weekdays: _frequency == MedicationFrequency.weekly
              ? _selectedWeekdays.toList()..sort()
              : null,
        );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('用药提醒已添加')),
      );
      context.go('/medication');
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('添加失败，请重试')),
      );
    }
  }
}
