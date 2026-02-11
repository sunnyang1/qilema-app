import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/constants/loading_state.dart';

void main() {
  group('LoadingState', () {
    test('should have four values', () {
      expect(LoadingState.values.length, 4);
    });

    test('should have initial value', () {
      expect(LoadingState.initial, isNotNull);
    });

    test('should have loading value', () {
      expect(LoadingState.loading, isNotNull);
    });

    test('should have loaded value', () {
      expect(LoadingState.loaded, isNotNull);
    });

    test('should have error value', () {
      expect(LoadingState.error, isNotNull);
    });
  });

  group('LoadingState extensions', () {
    test('isLoading should return true for loading state', () {
      expect(LoadingState.loading.isLoading, true);
      expect(LoadingState.initial.isLoading, false);
      expect(LoadingState.loaded.isLoading, false);
      expect(LoadingState.error.isLoading, false);
    });

    test('isLoaded should return true for loaded state', () {
      expect(LoadingState.loaded.isLoaded, true);
      expect(LoadingState.initial.isLoaded, false);
      expect(LoadingState.loading.isLoaded, false);
      expect(LoadingState.error.isLoaded, false);
    });

    test('hasError should return true for error state', () {
      expect(LoadingState.error.hasError, true);
      expect(LoadingState.initial.hasError, false);
      expect(LoadingState.loading.hasError, false);
      expect(LoadingState.loaded.hasError, false);
    });

    test('isInitial should return true for initial state', () {
      expect(LoadingState.initial.isInitial, true);
      expect(LoadingState.loading.isInitial, false);
      expect(LoadingState.loaded.isInitial, false);
      expect(LoadingState.error.isInitial, false);
    });
  });
}
