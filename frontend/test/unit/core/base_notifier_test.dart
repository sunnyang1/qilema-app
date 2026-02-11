import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/base_state.dart';
import 'package:qilema_app/core/constants/loading_state.dart';
import 'package:qilema_app/core/providers/base_notifier.dart';

base class TestState extends BaseState {
  const TestState({
    super.status = LoadingState.initial,
    super.errorMessage,
  });

  @override
  TestState copyWith({LoadingState? status, String? errorMessage}) {
    return TestState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

base class TestNotifier extends Notifier<TestState> with BaseNotifierMixin<TestState> {
  bool loadCalled = false;

  @override
  TestState build() {
    return const TestState();
  }

  @override
  Future<void> load() async {
    loadCalled = true;
  }
}

final testNotifierProvider =
    NotifierProvider<TestNotifier, TestState>(TestNotifier.new);

void main() {
  group('BaseNotifier', () {
    late ProviderContainer container;

    setUp(() {
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    test('should build with initial state', () {
      final state = container.read(testNotifierProvider);
      expect(state.status, LoadingState.initial);
      expect(state.errorMessage, null);
    });

    test('should have abstract load method', () {
      final notifier = TestNotifier();
      expect(() => notifier.load(), returnsNormally);
    });
  });
}



