import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/features/signin/providers/signin_provider.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 签到首页
class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(signinProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('签到'),
        actions: [
          IconButton(
            icon: const Icon(Icons.devices),
            onPressed: () {
              context.go('/devices');
            },
            tooltip: '智能设备',
          ),
          IconButton(
            icon: const Icon(Icons.health_and_safety),
            onPressed: () {
              context.go('/health');
            },
            tooltip: '健康档案',
          ),
          IconButton(
            icon: const Icon(Icons.contacts),
            onPressed: () {
              context.go('/contacts');
            },
            tooltip: '紧急联系人',
          ),
          IconButton(
            icon: const Icon(Icons.emergency),
            onPressed: () {
              context.go('/sos');
            },
            tooltip: '紧急求助',
          ),
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              context.go('/history');
            },
            tooltip: '签到历史',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(signinProvider.notifier).refresh();
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: state.isLoading
              ? const CircularProgressIndicator()
              : Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo
                    const Icon(
                      Icons.health_and_safety,
                      size: 80,
                      color: Color(0xFF2196F3),
                    ),
                    const SizedBox(height: 24),

                    // 欢迎语
                    Text(
                      _getGreeting(),
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),

                    const Text(
                      '今日签到',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 48),

                    // 签到按钮
                    _SigninButton(state: state),
                    const SizedBox(height: 32),

                    // 签到统计
                    if (state.streakDays != null) ...[
                      Card(
                        margin: const EdgeInsets.symmetric(horizontal: 32),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              const Text(
                                '连续签到',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                '${state.streakDays} 天',
                                style: const TextStyle(
                                  fontSize: 32,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF2196F3),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],

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

  /// 获取欢迎语
  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 6) return '凌晨好';
    if (hour < 9) return '早安';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 17) return '下午好';
    if (hour < 19) return '傍晚好';
    return '晚上好';
  }
}

/// 签到按钮组件
class _SigninButton extends ConsumerWidget {
  final SigninState state;

  const _SigninButton({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isCheckedIn = state.isCheckedIn;
    final isLoading = state.isLoading;

    return GestureDetector(
      onTap: isCheckedIn || isLoading
          ? null
          : () async {
              try {
                await ref.read(signinProvider.notifier).checkIn();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('签到成功！')),
                  );
                }
              } catch (e) {
                Logger.e('签到失败', error: e);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('签到失败：${e.toString()}')),
                  );
                }
              }
            },
      child: Container(
        width: 200,
        height: 200,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: isCheckedIn ? Colors.grey.shade300 : const Color(0xFF2196F3),
          boxShadow: [
            BoxShadow(
              color: isCheckedIn
                  ? Colors.grey.withValues(alpha: 0.3)
                  : const Color(0xFF2196F3).withValues(alpha: 0.3),
              blurRadius: 20,
              spreadRadius: 10,
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isCheckedIn ? Icons.check_circle : Icons.wb_sunny,
              size: 80,
              color: Colors.white,
            ),
            const SizedBox(height: 16),
            Text(
              isCheckedIn ? '已签到' : '早安',
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
