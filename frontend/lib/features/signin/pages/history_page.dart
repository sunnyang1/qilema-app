import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:qilema_app/features/signin/providers/signin_provider.dart';

/// 签到历史页面
class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key});

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage> {
  final ScrollController _scrollController = ScrollController();
  int _selectedFilter = 0; // 0: 全部, 1: 7天, 2: 30天

  @override
  void initState() {
    super.initState();
    _loadInitialHistory();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _loadInitialHistory() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(signinProvider.notifier).loadHistory(refresh: true);
    });
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent * 0.8) {
      ref.read(signinProvider.notifier).loadHistory();
    }
  }

  Future<void> _onRefresh() async {
    await ref.read(signinProvider.notifier).refreshHistory();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(signinProvider);
    final historyItems = _filterHistoryItems(state.historyItems);

    return Scaffold(
      appBar: AppBar(
        title: const Text('签到历史'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        elevation: 0,
      ),
      body: Column(
        children: [
          // 过滤器
          _buildFilterChips(),
          const SizedBox(height: 8),
          // 历史列表
          Expanded(
            child: _buildHistoryList(state, historyItems),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          _buildFilterChip('全部', 0),
          const SizedBox(width: 8),
          _buildFilterChip('最近7天', 1),
          const SizedBox(width: 8),
          _buildFilterChip('最近30天', 2),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, int value) {
    final isSelected = _selectedFilter == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() {
            _selectedFilter = value;
          });
        }
      },
      selectedColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
      checkmarkColor: Theme.of(context).colorScheme.primary,
    );
  }

  List<SigninHistoryItem> _filterHistoryItems(List<SigninHistoryItem> items) {
    if (_selectedFilter == 0) return items;

    final now = DateTime.now();
    final cutoffDate = _selectedFilter == 1
        ? now.subtract(const Duration(days: 7))
        : now.subtract(const Duration(days: 30));

    return items.where((item) => item.checkinTime.isAfter(cutoffDate)).toList();
  }

  Widget _buildHistoryList(SigninState state, List<SigninHistoryItem> historyItems) {
    if (state.isLoading && historyItems.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (historyItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.calendar_today_outlined,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              '暂无签到记录',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '每日签到记录你的生活',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[400],
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _onRefresh,
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: historyItems.length + (state.isLoadingHistory ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == historyItems.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ),
            );
          }

          final item = historyItems[index];
          return _buildHistoryItem(item);
        },
      ),
    );
  }

  Widget _buildHistoryItem(SigninHistoryItem item) {
    final dateFormat = DateFormat('yyyy年MM月dd日');
    final timeFormat = DateFormat('HH:mm');
    final isToday = item.checkinTime.day == DateTime.now().day &&
        item.checkinTime.month == DateTime.now().month &&
        item.checkinTime.year == DateTime.now().year;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.1),
          child: Icon(
            Icons.check_circle,
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
        title: Text(
          isToday ? '今日签到' : dateFormat.format(item.checkinTime),
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: isToday ? Theme.of(context).colorScheme.primary : null,
          ),
        ),
        subtitle: Text(timeFormat.format(item.checkinTime)),
        trailing: Text(
          _getStatusText(item.status),
          style: TextStyle(
            fontSize: 12,
            color: _getStatusColor(item.status),
          ),
        ),
      ),
    );
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'pending':
        return '待处理';
      default:
        return status;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'completed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}
