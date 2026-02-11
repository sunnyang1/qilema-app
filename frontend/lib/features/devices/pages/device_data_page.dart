import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/devices_models.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/features/devices/services/devices_api.dart';

/// 设备数据页面
class DeviceDataPage extends ConsumerStatefulWidget {
  final String deviceId;

  const DeviceDataPage({super.key, required this.deviceId});

  @override
  ConsumerState<DeviceDataPage> createState() => _DeviceDataPageState();
}

class _DeviceDataPageState extends ConsumerState<DeviceDataPage> {
  List<DeviceDataPoint> _dataPoints = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final api = DevicesApi();
      // 获取最近24小时的数据
      final endTime = DateTime.now().toIso8601String();
      final startTime = DateTime.now()
          .subtract(const Duration(hours: 24))
          .toIso8601String();

      final data = await api.getDeviceData(
        widget.deviceId,
        startTime: startTime,
        endTime: endTime,
      );

      setState(() {
        _dataPoints = data;
        _isLoading = false;
      });
    } catch (e) {
      // 使用模拟数据
      setState(() {
        _dataPoints = _generateMockData();
        _isLoading = false;
      });
    }
  }

  List<DeviceDataPoint> _generateMockData() {
    final now = DateTime.now();
    return List.generate(24, (index) {
      return DeviceDataPoint(
        dataType: 'heart_rate',
        value: 60 + (index % 20).toDouble(),
        unit: 'bpm',
        timestamp: now.subtract(Duration(hours: 23 - index)).toIso8601String(),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设备数据'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 当前数据卡片
                    _buildCurrentDataCard(),
                    const SizedBox(height: 24),

                    // 数据趋势
                    const Text(
                      '24小时趋势',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    _buildDataTrend(),
                    const SizedBox(height: 24),

                    // 数据统计
                    _buildStatistics(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildCurrentDataCard() {
    final latestData = _dataPoints.isNotEmpty ? _dataPoints.last : null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Icon(
              Icons.favorite,
              size: 48,
              color: AppColors.error,
            ),
            const SizedBox(height: 8),
            Text(
              latestData != null ? '${latestData.value.toInt()}' : '--',
              style: const TextStyle(
                fontSize: 48,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              latestData?.unit ?? 'bpm',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '当前心率',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            if (latestData != null) ...[
              const SizedBox(height: 4),
              Text(
                '更新时间: ${_formatTime(latestData.timestamp)}',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDataTrend() {
    if (_dataPoints.isEmpty) {
      return const Center(child: Text('暂无数据'));
    }

    return SizedBox(
      height: 200,
      child: CustomPaint(
        size: const Size(double.infinity, 200),
        painter: _LineChartPainter(_dataPoints),
      ),
    );
  }

  Widget _buildStatistics() {
    if (_dataPoints.isEmpty) {
      return const SizedBox.shrink();
    }

    final values = _dataPoints.map((d) => d.value).toList();
    final min = values.reduce((a, b) => a < b ? a : b);
    final max = values.reduce((a, b) => a > b ? a : b);
    final avg = values.reduce((a, b) => a + b) / values.length;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '数据统计',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('最低', min.toStringAsFixed(0)),
                _buildStatItem('平均', avg.toStringAsFixed(0)),
                _buildStatItem('最高', max.toStringAsFixed(0)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  String _formatTime(String timestamp) {
    final dateTime = DateTime.parse(timestamp);
    return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

/// 简单的折线图绘制器
class _LineChartPainter extends CustomPainter {
  final List<DeviceDataPoint> dataPoints;

  _LineChartPainter(this.dataPoints);

  @override
  void paint(Canvas canvas, Size size) {
    if (dataPoints.isEmpty) return;

    final paint = Paint()
      ..color = AppColors.primary
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final values = dataPoints.map((d) => d.value).toList();
    final min = values.reduce((a, b) => a < b ? a : b);
    final max = values.reduce((a, b) => a > b ? a : b);
    final range = max - min;

    final path = Path();
    final xStep = size.width / (dataPoints.length - 1);

    for (int i = 0; i < dataPoints.length; i++) {
      final x = i * xStep;
      final y = range == 0
          ? size.height / 2
          : size.height - ((dataPoints[i].value - min) / range) * size.height;

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);

    // 绘制数据点
    final pointPaint = Paint()
      ..color = AppColors.primary
      ..style = PaintingStyle.fill;

    for (int i = 0; i < dataPoints.length; i += 4) {
      final x = i * xStep;
      final y = range == 0
          ? size.height / 2
          : size.height - ((dataPoints[i].value - min) / range) * size.height;

      canvas.drawCircle(Offset(x, y), 4, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
