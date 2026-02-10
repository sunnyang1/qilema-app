import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/features/medication/providers/medication_provider.dart';
import 'package:qilema_app/features/medication/services/medication_api.dart';

/// 用药提醒列表页面
class MedicationRemindersPage extends ConsumerStatefulWidget {
  const MedicationRemindersPage({super.key});

  @override
  ConsumerState<MedicationRemindersPage> createState() => _MedicationRemindersPageState();
}

class _MedicationRemindersPageState extends ConsumerState<MedicationRemindersPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    Future.microtask(() {
      ref.read(medicationProvider.notifier).loadReminders();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(medicationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('用药提醒'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '今日用药'),
            Tab(text: '全部计划'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTodayView(state),
          _buildAllRemindersView(state),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/medication/add'),
        icon: const Icon(Icons.add),
        label: const Text('添加提醒'),
      ),
    );
  }

  /// 今日用药视图
  Widget _buildTodayView(MedicationState state) {
    if (state.isLoadingReminders && state.reminders.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.remindersState == LoadingState.error && state.reminders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(state.errorMessage ?? '加载失败'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(medicationProvider.notifier).loadReminders(),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final todayReminders = state.todayReminders.where((r) => r.isActive).toList();

    if (todayReminders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.medication_outlined, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              '今日暂无用药计划',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go('/medication/add'),
              child: const Text('添加提醒'),
            ),
          ],
        ),
      );
    }

    // 构建今日用药时间表
    final scheduleItems = _buildTodaySchedule(todayReminders);

    return RefreshIndicator(
      onRefresh: () => ref.read(medicationProvider.notifier).loadReminders(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: scheduleItems.length,
        itemBuilder: (context, index) {
          final item = scheduleItems[index];
          if (item.isHeader) {
            return _buildTimeHeader(item.time);
          }
          return _MedicationScheduleCard(
            reminder: item.reminder!,
            scheduledTime: item.time,
          );
        },
      ),
    );
  }

  /// 构建今日用药时间表
  List<_ScheduleItem> _buildTodaySchedule(List<MedicationReminder> reminders) {
    final items = <_ScheduleItem>[];
    
    // 按时间分组
    final timeMap = <String, List<MedicationReminder>>{};
    
    for (final reminder in reminders) {
      for (final time in reminder.reminderTimes) {
        timeMap.putIfAbsent(time, () => []).add(reminder);
      }
    }
    
    // 按时间排序
    final sortedTimes = timeMap.keys.toList()..sort();
    
    for (final time in sortedTimes) {
      items.add(_ScheduleItem.header(time));
      for (final reminder in timeMap[time]!) {
        items.add(_ScheduleItem.medication(time, reminder));
      }
    }
    
    return items;
  }

  Widget _buildTimeHeader(String time) {
    final hour = int.parse(time.split(':')[0]);
    String greeting;
    if (hour < 12) {
      greeting = '上午';
    } else if (hour < 18) {
      greeting = '下午';
    } else {
      greeting = '晚上';
    }

    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              '$time $greeting',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 全部提醒视图
  Widget _buildAllRemindersView(MedicationState state) {
    if (state.isLoadingReminders && state.reminders.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.reminders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.medication_outlined, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              '暂无用药提醒',
              style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(medicationProvider.notifier).loadReminders(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: state.reminders.length,
        itemBuilder: (context, index) {
          final reminder = state.reminders[index];
          return _ReminderCard(reminder: reminder);
        },
      ),
    );
  }
}

/// 时间表项
class _ScheduleItem {
  final String time;
  final MedicationReminder? reminder;
  final bool isHeader;

  _ScheduleItem.header(this.time)
      : isHeader = true,
        reminder = null;

  _ScheduleItem.medication(this.time, this.reminder) : isHeader = false;
}

/// 用药计划卡片（用于今日用药）
class _MedicationScheduleCard extends ConsumerWidget {
  final MedicationReminder reminder;
  final String scheduledTime;

  const _MedicationScheduleCard({
    required this.reminder,
    required this.scheduledTime,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isTaken = reminder.isTimeTaken(scheduledTime);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: isTaken ? Colors.green.shade100 : Colors.orange.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            isTaken ? Icons.check_circle : Icons.medication,
            color: isTaken ? Colors.green.shade700 : Colors.orange.shade700,
          ),
        ),
        title: Text(
          reminder.medicationName,
          style: TextStyle(
            decoration: isTaken ? TextDecoration.lineThrough : null,
            color: isTaken ? Colors.grey : Colors.black,
          ),
        ),
        subtitle: Text(
          '${reminder.dosage ?? ''} ${reminder.unit ?? ''}',
          style: TextStyle(
            color: isTaken ? Colors.grey.shade500 : Colors.grey.shade700,
          ),
        ),
        trailing: isTaken
            ? Chip(
                label: const Text('已服用'),
                backgroundColor: Colors.green.shade50,
                labelStyle: TextStyle(
                  color: Colors.green.shade700,
                  fontSize: 12,
                ),
              )
            : ElevatedButton(
                onPressed: () => _recordTaking(context, ref),
                child: const Text('服用'),
              ),
      ),
    );
  }

  Future<void> _recordTaking(BuildContext context, WidgetRef ref) async {
    final success = await ref.read(medicationProvider.notifier).recordTaking(
          reminder.id,
          scheduledTime,
        );

    if (success && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('已记录服用')),
      );
    }
  }
}

/// 提醒卡片（用于全部计划）
class _ReminderCard extends ConsumerWidget {
  final MedicationReminder reminder;

  const _ReminderCard({required this.reminder});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: reminder.isActive
                        ? Colors.blue.shade100
                        : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.medication,
                    color: reminder.isActive
                        ? Colors.blue.shade700
                        : Colors.grey.shade600,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        reminder.medicationName,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: reminder.isActive ? Colors.black : Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${reminder.dosage ?? ''} ${reminder.unit ?? ''}',
                        style: TextStyle(
                          color: reminder.isActive
                              ? Colors.grey.shade700
                              : Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
                Switch(
                  value: reminder.isActive,
                  onChanged: (value) => ref
                      .read(medicationProvider.notifier)
                      .toggleReminder(reminder.id, value),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.access_time, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  reminder.reminderTimes.join('、'),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(width: 16),
                Icon(Icons.repeat, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  _getFrequencyText(reminder),
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                  ),
                ),
              ],
            ),
            if (!reminder.isActive) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '已暂停',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _getFrequencyText(MedicationReminder reminder) {
    switch (reminder.frequency) {
      case MedicationFrequency.daily:
        return '每天';
      case MedicationFrequency.weekly:
        if (reminder.weekdays != null && reminder.weekdays!.isNotEmpty) {
          final days = reminder.weekdays!.map((d) {
            const dayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
            return dayNames[d];
          }).join('、');
          return '每周$days';
        }
        return '每周';
      case MedicationFrequency.custom:
        return '自定义';
    }
  }
}
