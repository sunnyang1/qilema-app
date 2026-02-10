import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:qilema_app/features/sos/providers/sos_provider.dart';
import 'package:url_launcher/url_launcher.dart';

/// SOS状态页面
class SosStatusPage extends ConsumerStatefulWidget {
  const SosStatusPage({super.key});

  @override
  ConsumerState<SosStatusPage> createState() => _SosStatusPageState();
}

class _SosStatusPageState extends ConsumerState<SosStatusPage> {
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sosProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('SOS状态'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        elevation: 0,
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 状态图标
                _buildStatusIcon(),
                const SizedBox(height: 24),

                // 状态文本
                Text(
                  _getStatusText(),
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: _getStatusColor(),
                  ),
                ),
                const SizedBox(height: 8),

                // 状态描述
                Text(
                  _getStatusDescription(),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 32),

                // 触发时间
                if (state.sosId != null) ...[
                  _buildInfoCard(
                    icon: Icons.access_time,
                    title: '触发时间',
                    content: _formatTime(DateTime.now()),
                  ),
                  const SizedBox(height: 16),
                ],

                // 位置信息
                if (state.latitude != null && state.longitude != null) ...[
                  _buildInfoCard(
                    icon: Icons.location_on,
                    title: '位置信息',
                    content:
                        '${state.latitude!.toStringAsFixed(6)}, ${state.longitude!.toStringAsFixed(6)}',
                  ),
                  const SizedBox(height: 32),
                ],

                // 操作按钮
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 拨打120按钮
                    _buildEmergencyButton(),
                    const SizedBox(width: 16),
                    // 取消SOS按钮
                    _buildCancelButton(),
                  ],
                ),

                // 错误提示
                if (state.errorMessage != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Text(
                      state.errorMessage!,
                      style: TextStyle(color: Colors.red.shade700),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusIcon() {
    final state = ref.read(sosProvider);

    switch (state.status) {
      case SosStatus.triggered:
        return Container(
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.orange.withValues(alpha: 0.1),
          ),
          child: const Icon(
            Icons.emergency,
            size: 64,
            color: Colors.orange,
          ),
        );
      default:
        return Container(
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.grey.withValues(alpha: 0.1),
          ),
          child: Icon(
            Icons.help_outline,
            size: 64,
            color: Colors.grey[400],
          ),
        );
    }
  }

  String _getStatusText() {
    final state = ref.read(sosProvider);

    switch (state.status) {
      case SosStatus.triggered:
        return '求助已发送';
      default:
        return '等待求助';
    }
  }

  String _getStatusDescription() {
    final state = ref.read(sosProvider);

    switch (state.status) {
      case SosStatus.triggered:
        return '紧急联系人已收到通知，救援人员正在前往';
      default:
        return '长按SOS按钮触发紧急求助';
    }
  }

  Color _getStatusColor() {
    final state = ref.read(sosProvider);

    switch (state.status) {
      case SosStatus.triggered:
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String _formatTime(DateTime dateTime) {
    final dateFormat = DateFormat('yyyy年MM月dd日 HH:mm');
    return dateFormat.format(dateTime);
  }

  Widget _buildInfoCard({
    required IconData icon,
    required String title,
    required String content,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: Theme.of(context).colorScheme.primary,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  content,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyButton() {
    return ElevatedButton.icon(
      onPressed: _callEmergency,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFFF44336),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      icon: const Icon(Icons.phone),
      label: const Text('拨打120'),
    );
  }

  Widget _buildCancelButton() {
    final state = ref.read(sosProvider);

    return OutlinedButton.icon(
      onPressed: state.isTriggered ? _cancelSOS : null,
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.grey[700],
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      icon: const Icon(Icons.cancel),
      label: const Text('取消SOS'),
    );
  }

  Future<void> _callEmergency() async {
    final Uri phoneUri = Uri(scheme: 'tel', path: '120');
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    }
  }

  Future<void> _cancelSOS() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认取消'),
        content: const Text('确定要取消SOS求助吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      ref.read(sosProvider.notifier).reset();
      if (mounted) {
        Navigator.of(context).pop();
      }
    }
  }
}
