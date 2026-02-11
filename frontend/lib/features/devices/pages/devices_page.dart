import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/core/models/devices_models.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/devices/providers/devices_provider.dart';

/// 设备列表页面
class DevicesPage extends ConsumerWidget {
  const DevicesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(devicesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('智能设备'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(devicesProvider.notifier).refresh();
            },
          ),
        ],
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : state.isEmpty
              ? _buildEmptyState(context, ref)
              : _buildDeviceList(context, ref, state.devices),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showBindDeviceDialog(context, ref),
        backgroundColor: AppColors.primary,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, WidgetRef ref) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.devices, size: 80, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            '暂无绑定设备',
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            '点击右下角按钮添加设备',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildDeviceList(BuildContext context, WidgetRef ref, List<Device> devices) {
    return RefreshIndicator(
      onRefresh: () => ref.read(devicesProvider.notifier).refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: devices.length,
        itemBuilder: (context, index) {
          final device = devices[index];
          return _buildDeviceCard(context, ref, device);
        },
      ),
    );
  }

  Widget _buildDeviceCard(BuildContext context, WidgetRef ref, Device device) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppColors.primary.withValues(alpha: 0.1),
          child: Icon(
            _getDeviceIcon(device.deviceType),
            color: AppColors.primary,
          ),
        ),
        title: Text(
          device.deviceName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(device.typeDisplayName),
            if (device.batteryLevel != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(
                    Icons.battery_full,
                    size: 16,
                    color: _getBatteryColor(device.batteryLevel!),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${device.batteryLevel}%',
                    style: TextStyle(
                      color: _getBatteryColor(device.batteryLevel!),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: device.isConnected ? Colors.green : Colors.grey,
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.show_chart, color: AppColors.primary),
              onPressed: () {
                context.push('/devices/${device.deviceId}/data');
              },
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: AppColors.error),
              onPressed: () => _showUnbindConfirmDialog(context, ref, device),
            ),
          ],
        ),
        onTap: () {
          context.push('/devices/${device.deviceId}/data');
        },
      ),
    );
  }

  IconData _getDeviceIcon(String deviceType) {
    switch (deviceType) {
      case 'smart_watch':
        return Icons.watch;
      case 'blood_pressure_monitor':
        return Icons.monitor_heart;
      case 'blood_glucose_meter':
        return Icons.medical_services;
      case 'heart_rate_monitor':
        return Icons.favorite;
      case 'sleep_tracker':
        return Icons.bedtime;
      default:
        return Icons.devices;
    }
  }

  Color _getBatteryColor(int level) {
    if (level > 60) return Colors.green;
    if (level > 20) return Colors.orange;
    return Colors.red;
  }

  void _showBindDeviceDialog(BuildContext context, WidgetRef ref) async {
    // 开始扫描
    await ref.read(devicesProvider.notifier).scanDevices();

    if (!context.mounted) return;

    showDialog(
      context: context,
      builder: (dialogContext) => Consumer(
        builder: (context, ref, child) {
          final state = ref.watch(devicesProvider);

          return AlertDialog(
            title: const Text('添加设备'),
            content: SizedBox(
              width: double.maxFinite,
              child: state.isScanning
                  ? const Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('正在扫描附近的设备...'),
                      ],
                    )
                  : state.scannedDevices.isEmpty
                      ? const Center(child: Text('未发现可用设备'))
                      : ListView.builder(
                          shrinkWrap: true,
                          itemCount: state.scannedDevices.length,
                          itemBuilder: (context, index) {
                            final device = state.scannedDevices[index];
                            return ListTile(
                              leading: Icon(_getDeviceIcon(device.deviceType)),
                              title: Text(device.deviceName),
                              subtitle: Text(device.macAddress ?? ''),
                              trailing: ElevatedButton(
                                onPressed: () async {
                                  try {
                                    await ref
                                        .read(devicesProvider.notifier)
                                        .bindDevice(device);
                                    if (dialogContext.mounted) {
                                      Navigator.pop(dialogContext);
if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('设备绑定成功')),
                                    );
                                  }
                                    }
                                  } catch (e) {
                                    if (context.mounted) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('绑定失败: $e')),
                                      );
                                    }
                                  }
                                },
                                child: const Text('绑定'),
                              ),
                            );
                          },
                        ),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  ref.read(devicesProvider.notifier).clearScannedDevices();
                  Navigator.pop(dialogContext);
                },
                child: const Text('取消'),
              ),
              if (state.isScanning)
                TextButton(
                  onPressed: () {
                    // 停止扫描
                  },
                  child: const Text('停止'),
                ),
            ],
          );
        },
      ),
    );
  }

  void _showUnbindConfirmDialog(BuildContext context, WidgetRef ref, Device device) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('确认解绑'),
        content: Text('确定要解绑"${device.deviceName}"吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await ref
                    .read(devicesProvider.notifier)
                    .unbindDevice(device.deviceId);
                if (dialogContext.mounted) {
                  Navigator.pop(dialogContext);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('设备已解绑')),
                  );
                }
              } catch (e) {
if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('解绑失败: $e')),
                                    );
                                  }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: const Text('解绑'),
          ),
        ],
      ),
    );
  }
}
