library;

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/exceptions/exceptions.dart';
import 'package:qilema_app/core/network/exception_converter.dart';

void main() {
  group('ExceptionConverter', () {
    group('convertDioException', () {
      test('should convert connectionTimeout to NetworkException with timeout type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.connectionTimeout,
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.timeout);
        expect(result.message, contains('网络请求超时'));
      });

      test('should convert receiveTimeout to NetworkException with timeout type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.receiveTimeout,
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.timeout);
        expect(result.message, contains('网络请求超时'));
      });

      test('should convert sendTimeout to NetworkException with timeout type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.sendTimeout,
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.timeout);
        expect(result.message, contains('网络请求超时'));
      });

      test('should convert connectionError to NetworkException with noConnection type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.connectionError,
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.noConnection);
        expect(result.message, contains('网络连接失败'));
      });

      test('should convert 502 badResponse to NetworkException with serverError type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 502,
          ),
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.serverError);
        expect(result.message, contains('服务器错误'));
      });

      test('should convert 503 badResponse to NetworkException with serverError type', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 503,
          ),
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.serverError);
        expect(result.message, contains('服务器错误'));
      });

      test('should convert 401 badResponse to ApiException', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 401,
            data: {'error': 'Unauthorized'},
          ),
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<ApiException>());
        expect((result as ApiException).statusCode, 401);
        expect(result.message, 'Unauthorized');
      });

      test('should convert 404 badResponse to ApiException', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse,
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 404,
            data: {'message': 'Not found'},
          ),
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<ApiException>());
        expect((result as ApiException).statusCode, 404);
        expect(result.message, 'Not found');
      });

      test('should convert cancel to NetworkException', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.cancel,
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.noConnection);
        expect(result.message, contains('请求已取消'));
      });

      test('should convert unknown error to NetworkException', () {
        // Given
        final dioException = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.unknown,
          message: 'Unknown error occurred',
        );

        // When
        final result = ExceptionConverter.convertDioException(dioException);

        // Then
        expect(result, isA<NetworkException>());
        expect((result as NetworkException).type, NetworkExceptionType.noConnection);
        expect(result.message, contains('Unknown error occurred'));
      });
    });

    group('extractErrorMessage', () {
      test('should extract message from map with message field', () {
        // Given
        final data = {'message': 'Error message'};

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'Error message');
      });

      test('should extract message from map with error field', () {
        // Given
        final data = {'error': 'Error message'};

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'Error message');
      });

      test('should extract message from map with detail field', () {
        // Given
        final data = {'detail': 'Error message'};

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'Error message');
      });

      test('should extract message from map with msg field', () {
        // Given
        final data = {'msg': 'Error message'};

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'Error message');
      });

      test('should return default message for null data', () {
        // When
        final result = ExceptionConverter.extractErrorMessage(null);

        // Then
        expect(result, '请求失败');
      });

      test('should return default message for empty map', () {
        // When
        final result = ExceptionConverter.extractErrorMessage({});

        // Then
        expect(result, '请求失败');
      });

      test('should return string data as is', () {
        // Given
        final data = 'String error message';

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'String error message');
      });

      test('should prefer message field over other fields', () {
        // Given
        final data = {
          'message': 'Primary message',
          'error': 'Secondary message',
        };

        // When
        final result = ExceptionConverter.extractErrorMessage(data);

        // Then
        expect(result, 'Primary message');
      });
    });
  });
}
