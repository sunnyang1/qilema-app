import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/sos/providers/sos_provider.dart';

/// SOS触发页面
class SosPage extends ConsumerStatefulWidget {
  const SosPage({super.key});

  @override
  ConsumerState<SosPage> createState() => _SosPageState();
}

class _SosPageState extends ConsumerState<SosPage> {
  Timer? _holdTimer;
  int _holdDuration = 0; // 毫秒
  static const _requiredDuration = 3000; // 3秒

  @override
  void dispose() {
    _holdTimer?.cancel();
    super.dispose();
  }

  void _onLongPressStart() {
    setState(() {
      _holdDuration = 0;
    });

    _holdTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      setState(() {
        _holdDuration += 100;
      });

      if (_holdDuration >= _requiredDuration) {
        timer.cancel();
        _triggerSOS();
      }
    });
  }

  void _onLongPressEnd() {
    _holdTimer?.cancel();

    if (_holdDuration < _requiredDuration) {
      setState(() {
        _holdDuration = 0;
      });
    }
  }

  void _triggerSOS() async {
    await ref.read(sosProvider.notifier).triggerSOS();

    if (mounted && ref.read(sosProvider).isTriggered) {
      Navigator.of(context).pushNamed('/sos/status');
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sosProvider);
    final progress = (_holdDuration / _requiredDuration).clamp(0.0, 1.0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('紧急求助'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        elevation: 0,
      ),
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 警告图标
              const Icon(
                Icons.warning_amber_rounded,
                size: 100,
                color: Color(0xFFF44336),
              ),
              const SizedBox(height: 24),

              // 标题
              const Text(
                '长按下方按钮触发SOS',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '长按3秒以确认，防止误触',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 48),

              // SOS按钮
              GestureDetector(
                onLongPressStart: (_) => _onLongPressStart(),
                onLongPressEnd: (_) => _onLongPressEnd(),
                onLongPress: _triggerSOS,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // 进度圆环
                    SizedBox(
                      width: 250,
                      height: 250,
                      child: CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 8,
                        backgroundColor: Colors.grey[300],
                        valueColor: AlwaysStoppedAnimation<Color>(
                          const Color(0xFFF44336),
                        ),
                      ),
                    ),
                    // SOS按钮
                    Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFFF44336),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFFF44336).withValues(alpha: 0.3),
                            blurRadius: 20,
                            spreadRadius: 10,
                          ),
                        ],
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.sos,
                            size: 80,
                            color: Colors.white,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            progress >= 1.0 ? '松开' : 'SOS',
                            style: const TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 48),

              // 位置信息
              if (state.latitude != null && state.longitude != null)
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 32),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.location_on,
                        color: Colors.green.shade700,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '已获取位置：${state.latitude!.toStringAsFixed(6)}, ${state.longitude!.toStringAsFixed(6)}',
                          style: TextStyle(
                            color: Colors.green.shade700,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

              // 错误提示
              if (state.errorMessage != null) ...[
                const SizedBox(height: 16),
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 32),
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
    );
  }
}
