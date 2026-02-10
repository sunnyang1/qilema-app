import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:geolocator/geolocator.dart';
import 'package:qilema_app/features/emergency/providers/emergency_provider.dart';
import 'package:qilema_app/features/emergency/services/emergency_api.dart';
import 'package:qilema_app/core/utils/logger.dart';
import 'package:url_launcher/url_launcher.dart';

/// AED地图页面
class AedMapPage extends ConsumerStatefulWidget {
  const AedMapPage({super.key});

  @override
  ConsumerState<AedMapPage> createState() => _AedMapPageState();
}

class _AedMapPageState extends ConsumerState<AedMapPage> {
  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  /// 获取当前位置
  Future<void> _getCurrentLocation() async {
    try {
      // 检查位置服务是否启用
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('请开启位置服务')),
          );
        }
        return;
      }

      // 检查权限
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('需要位置权限才能使用此功能')),
            );
          }
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('位置权限被永久拒绝，请在设置中开启')),
          );
        }
        return;
      }

      // 获取当前位置
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );

      ref.read(emergencyProvider.notifier).setLocation(
            position.latitude,
            position.longitude,
          );

      // 加载附近的AED
      await ref.read(emergencyProvider.notifier).loadNearbyAeds();
    } catch (e) {
      Logger.e('获取位置失败', error: e);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('获取位置失败: ${e.toString()}')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(emergencyProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('附近AED'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(emergencyProvider.notifier).loadNearbyAeds(),
          ),
          TextButton(
            onPressed: () => context.go('/hospitals'),
            child: const Text(
              '医院',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(emergencyProvider.notifier).loadNearbyAeds(),
        child: _buildBody(state),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _getCurrentLocation,
        child: const Icon(Icons.my_location),
      ),
    );
  }

  Widget _buildBody(EmergencyState state) {
    if (state.isLoading && state.aedDevices.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.hasError && state.aedDevices.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              state.errorMessage ?? '加载失败',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(emergencyProvider.notifier).loadNearbyAeds(),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state.aedDevices.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.location_off,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '附近暂无AED设备',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '尝试扩大搜索范围或刷新页面',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade500,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: state.aedDevices.length,
      itemBuilder: (context, index) {
        final device = state.aedDevices[index];
        return _AedDeviceCard(device: device);
      },
    );
  }
}

/// AED设备卡片
class _AedDeviceCard extends StatelessWidget {
  final AedDevice device;

  const _AedDeviceCard({required this.device});

  @override
  Widget build(BuildContext context) {
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
                    color: device.isAvailable
                        ? Colors.green.shade100
                        : Colors.red.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.electric_bolt,
                    color: device.isAvailable
                        ? Colors.green.shade700
                        : Colors.red.shade700,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        device.name,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: device.isAvailable
                                  ? Colors.green.shade50
                                  : Colors.red.shade50,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              device.isAvailable ? '可用' : '不可用',
                              style: TextStyle(
                                fontSize: 12,
                                color: device.isAvailable
                                    ? Colors.green.shade700
                                    : Colors.red.shade700,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Icon(
                            Icons.location_on,
                            size: 14,
                            color: Colors.grey.shade600,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            '${device.distance.toInt()}m',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.place,
                  size: 16,
                  color: Colors.grey.shade600,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    device.address,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                    ),
                  ),
                ),
              ],
            ),
            if (device.operatingHours != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: Colors.grey.shade600,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '营业时间: ${device.operatingHours}',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: device.phone != null
                        ? () => _makePhoneCall(device.phone!)
                        : null,
                    icon: const Icon(Icons.phone, size: 18),
                    label: const Text('电话'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _openNavigation(device),
                    icon: const Icon(Icons.navigation, size: 18),
                    label: const Text('导航'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 拨打电话
  Future<void> _makePhoneCall(String phone) async {
    final uri = Uri.parse('tel:$phone');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  /// 打开导航
  Future<void> _openNavigation(AedDevice device) async {
    // 使用高德地图或系统地图进行导航
    final uri = Uri.parse(
      'https://uri.amap.com/navigation?to=${device.longitude},${device.latitude},${device.name}&mode=car&coordinate=gaode',
    );
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      // 备选：使用苹果地图或谷歌地图
      final fallbackUri = Uri.parse(
        'https://maps.apple.com/?daddr=${device.latitude},${device.longitude}',
      );
      if (await canLaunchUrl(fallbackUri)) {
        await launchUrl(fallbackUri, mode: LaunchMode.externalApplication);
      }
    }
  }
}
