import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/models/base_state.dart';
import 'package:qilema_app/core/constants/loading_state.dart';

base class TestState extends BaseState {
  final String customField;

  const TestState({
    super.status = LoadingState.initial,
    super.errorMessage,
    this.customField = 'default',
  });

  @override
  TestState copyWith({
    LoadingState? status,
    String? errorMessage,
    String? customField,
  }) {
    return TestState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
      customField: customField ?? this.customField,
    );
  }

  @override
  List<Object?> get props => [status, errorMessage, customField];
}

void main() {
  group('BaseState', () {
    test('should have initial status by default', () {
      const state = TestState();
      expect(state.status, LoadingState.initial);
      expect(state.errorMessage, null);
    });

    test('should accept custom status', () {
      const state = TestState(status: LoadingState.loading);
      expect(state.status, LoadingState.loading);
    });

    test('should accept error message', () {
      const state = TestState(errorMessage: 'Error message');
      expect(state.errorMessage, 'Error message');
    });

    test('isLoading should delegate to status', () {
      const loadingState = TestState(status: LoadingState.loading);
      const initialState = TestState(status: LoadingState.initial);

      expect(loadingState.isLoading, true);
      expect(initialState.isLoading, false);
    });

    test('isLoaded should delegate to status', () {
      const loadedState = TestState(status: LoadingState.loaded);
      const errorState = TestState(status: LoadingState.error);

      expect(loadedState.isLoaded, true);
      expect(errorState.isLoaded, false);
    });

    test('hasError should delegate to status', () {
      const errorState = TestState(status: LoadingState.error);
      const loadedState = TestState(status: LoadingState.loaded);

      expect(errorState.hasError, true);
      expect(loadedState.hasError, false);
    });

    test('isInitial should delegate to status', () {
      const initialState = TestState(status: LoadingState.initial);
      const loadingState = TestState(status: LoadingState.loading);

      expect(initialState.isInitial, true);
      expect(loadingState.isInitial, false);
    });
  });

  group('BaseState copyWith', () {
    test('should update status', () {
      const state = TestState();
      final updated = state.copyWith(status: LoadingState.loading);

      expect(updated.status, LoadingState.loading);
      expect(state.status, LoadingState.initial);
    });

    test('should update errorMessage', () {
      const state = TestState();
      final updated = state.copyWith(errorMessage: 'New error');

      expect(updated.errorMessage, 'New error');
      expect(state.errorMessage, null);
    });

    test('should update custom field', () {
      const state = TestState(customField: 'old');
      final updated = state.copyWith(customField: 'new');

      expect(updated.customField, 'new');
      expect(state.customField, 'old');
    });

    test('should preserve unchanged fields', () {
      const state = TestState(
        status: LoadingState.loading,
        errorMessage: 'Error',
        customField: 'value',
      );
      final updated = state.copyWith(status: LoadingState.loaded);

      expect(updated.status, LoadingState.loaded);
      expect(updated.errorMessage, 'Error');
      expect(updated.customField, 'value');
    });
  });

  group('BaseState immutability', () {
    test('should be immutable', () {
      const state = TestState();
      final updated = state.copyWith(status: LoadingState.loading);

      expect(identical(state, updated), false);
      expect(state.status, LoadingState.initial);
      expect(updated.status, LoadingState.loading);
    });
  });
}
