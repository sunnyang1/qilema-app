import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/exceptions/exceptions.dart';

void main() {
  group('AppException', () {
    test('should create with code and message', () {
      // When
      final exception = AppException(code: 'TEST_ERROR', message: 'Test message');

      // Then
      expect(exception.code, 'TEST_ERROR');
      expect(exception.message, 'Test message');
      expect(exception.details, isNull);
    });

    test('should create with code, message and details', () {
      // When
      final exception = AppException(
        code: 'TEST_ERROR',
        message: 'Test message',
        details: {'key': 'value'},
      );

      // Then
      expect(exception.code, 'TEST_ERROR');
      expect(exception.message, 'Test message');
      expect(exception.details, {'key': 'value'});
    });

    test('toString should return formatted string', () {
      // Given
      final exception = AppException(code: 'TEST_ERROR', message: 'Test message');

      // When
      final result = exception.toString();

      // Then
      expect(result, contains('TEST_ERROR'));
      expect(result, contains('Test message'));
    });

    test('toString should include details when present', () {
      // Given
      final exception = AppException(
        code: 'TEST_ERROR',
        message: 'Test message',
        details: {'key': 'value'},
      );

      // When
      final result = exception.toString();

      // Then
      expect(result, contains('key: value'));
    });
  });

  group('ApiException', () {
    test('should create AppException subclass', () {
      // When
      final exception = ApiException(
        code: 'API_ERROR',
        message: 'API failed',
        statusCode: 404,
      );

      // Then
      expect(exception, isA<AppException>());
      expect(exception.code, 'API_ERROR');
      expect(exception.message, 'API failed');
      expect(exception.statusCode, 404);
    });

    test('toString should include statusCode', () {
      // Given
      final exception = ApiException(
        code: 'API_ERROR',
        message: 'API failed',
        statusCode: 404,
      );

      // When
      final result = exception.toString();

      // Then
      expect(result, contains('404'));
    });
  });

  group('NetworkException', () {
    test('should create AppException subclass', () {
      // When
      final exception = NetworkException(
        code: 'NETWORK_ERROR',
        message: 'Network failed',
        type: NetworkExceptionType.timeout,
      );

      // Then
      expect(exception, isA<AppException>());
      expect(exception.code, 'NETWORK_ERROR');
      expect(exception.message, 'Network failed');
      expect(exception.type, NetworkExceptionType.timeout);
    });

    test('toString should include type', () {
      // Given
      final exception = NetworkException(
        code: 'NETWORK_ERROR',
        message: 'Network failed',
        type: NetworkExceptionType.noConnection,
      );

      // When
      final result = exception.toString();

      // Then
      expect(result, contains('noConnection'));
    });

    test('all NetworkExceptionType values should be accessible', () {
      // Then
      expect(NetworkExceptionType.values, containsAll([
        NetworkExceptionType.noConnection,
        NetworkExceptionType.timeout,
        NetworkExceptionType.serverError,
      ]));
    });
  });

  group('ValidationException', () {
    test('should create AppException subclass', () {
      // When
      final exception = ValidationException(
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        field: 'email',
      );

      // Then
      expect(exception, isA<AppException>());
      expect(exception.code, 'VALIDATION_ERROR');
      expect(exception.message, 'Invalid input');
      expect(exception.field, 'email');
    });

    test('toString should include field', () {
      // Given
      final exception = ValidationException(
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        field: 'password',
      );

      // When
      final result = exception.toString();

      // Then
      expect(result, contains('field: password'));
    });
  });

  group('Exception hierarchy', () {
    test('all exceptions should be AppException instances', () {
      // Given
      final exceptions = [
        ApiException(code: 'API', message: 'msg', statusCode: 200),
        NetworkException(code: 'NET', message: 'msg', type: NetworkExceptionType.timeout),
        ValidationException(code: 'VAL', message: 'msg', field: 'field'),
      ];

      // Then
      for (final exception in exceptions) {
        expect(exception, isA<AppException>());
      }
    });
  });
}
