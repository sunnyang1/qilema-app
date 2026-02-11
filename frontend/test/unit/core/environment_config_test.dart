import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/config/environment_config.dart';

void main() {
  group('Environment', () {
    test('dev enum value has correct name', () {
      expect(Environment.dev.name, equals('development'));
      expect(Environment.dev.isDevelopment, isTrue);
      expect(Environment.dev.isStaging, isFalse);
      expect(Environment.dev.isProduction, isFalse);
    });

    test('staging enum value has correct name', () {
      expect(Environment.staging.name, equals('staging'));
      expect(Environment.staging.isDevelopment, isFalse);
      expect(Environment.staging.isStaging, isTrue);
      expect(Environment.staging.isProduction, isFalse);
    });

    test('prod enum value has correct name', () {
      expect(Environment.prod.name, equals('production'));
      expect(Environment.prod.isDevelopment, isFalse);
      expect(Environment.prod.isStaging, isFalse);
      expect(Environment.prod.isProduction, isTrue);
    });
  });

  group('EnvironmentConfig.dev', () {
    test('has correct default values', () {
      const config = EnvironmentConfig.dev;
      
      expect(config.environment, equals(Environment.dev));
      expect(config.baseUrl, equals('http://localhost:8000/api/v1'));
      expect(config.connectTimeout, equals(10000));
      expect(config.receiveTimeout, equals(10000));
      expect(config.sendTimeout, equals(10000));
      expect(config.enableDebugLogs, isTrue);
      expect(config.appVersion, equals('1.0.0-dev'));
      expect(config.enableErrorReporting, isFalse);
    });

    test('passes validation', () {
      const config = EnvironmentConfig.dev;
      expect(config.isValid, isTrue);
      expect(config.validate(), isEmpty);
    });
  });

  group('EnvironmentConfig.staging', () {
    test('has correct default values', () {
      const config = EnvironmentConfig.staging;
      
      expect(config.environment, equals(Environment.staging));
      expect(config.baseUrl, equals('https://staging.qilema.com/api/v1'));
      expect(config.connectTimeout, equals(15000));
      expect(config.receiveTimeout, equals(15000));
      expect(config.sendTimeout, equals(15000));
      expect(config.enableDebugLogs, isTrue);
      expect(config.appVersion, equals('1.0.0-staging'));
      expect(config.enableErrorReporting, isTrue);
    });

    test('passes validation', () {
      const config = EnvironmentConfig.staging;
      expect(config.isValid, isTrue);
      expect(config.validate(), isEmpty);
    });
  });

  group('EnvironmentConfig.prod', () {
    test('has correct default values', () {
      const config = EnvironmentConfig.prod;
      
      expect(config.environment, equals(Environment.prod));
      expect(config.baseUrl, equals('https://api.qilema.com/api/v1'));
      expect(config.connectTimeout, equals(15000));
      expect(config.receiveTimeout, equals(15000));
      expect(config.sendTimeout, equals(15000));
      expect(config.enableDebugLogs, isFalse);
      expect(config.appVersion, equals('1.0.0'));
      expect(config.enableErrorReporting, isTrue);
    });

    test('passes validation', () {
      const config = EnvironmentConfig.prod;
      expect(config.isValid, isTrue);
      expect(config.validate(), isEmpty);
    });
  });

  group('EnvironmentConfig.fromString', () {
    test('returns dev config for "dev"', () {
      expect(EnvironmentConfig.fromString('dev'), equals(EnvironmentConfig.dev));
    });

    test('returns dev config for "development"', () {
      expect(EnvironmentConfig.fromString('development'), equals(EnvironmentConfig.dev));
    });

    test('returns staging config for "staging"', () {
      expect(EnvironmentConfig.fromString('staging'), equals(EnvironmentConfig.staging));
    });

    test('returns staging config for "test"', () {
      expect(EnvironmentConfig.fromString('test'), equals(EnvironmentConfig.staging));
    });

    test('returns prod config for "prod"', () {
      expect(EnvironmentConfig.fromString('prod'), equals(EnvironmentConfig.prod));
    });

    test('returns prod config for "production"', () {
      expect(EnvironmentConfig.fromString('production'), equals(EnvironmentConfig.prod));
    });

    test('returns dev config for unknown values', () {
      expect(EnvironmentConfig.fromString('unknown'), equals(EnvironmentConfig.dev));
    });

    test('is case insensitive', () {
      expect(EnvironmentConfig.fromString('DEV'), equals(EnvironmentConfig.dev));
      expect(EnvironmentConfig.fromString('Dev'), equals(EnvironmentConfig.dev));
      expect(EnvironmentConfig.fromString('PROD'), equals(EnvironmentConfig.prod));
    });
  });

  group('EnvironmentConfig.validate', () {
    test('returns error for empty baseUrl', () {
      final config = EnvironmentConfig.dev.copyWith(baseUrl: '');
      final errors = config.validate();
      
      expect(errors, contains('baseUrl cannot be empty'));
      expect(config.isValid, isFalse);
    });

    test('returns error for invalid URL scheme', () {
      final config = EnvironmentConfig.dev.copyWith(baseUrl: 'ftp://invalid.com');
      final errors = config.validate();
      
      expect(errors, contains('baseUrl must use http or https scheme'));
      expect(config.isValid, isFalse);
    });

    test('returns error for zero connectTimeout', () {
      final config = EnvironmentConfig.dev.copyWith(connectTimeout: 0);
      final errors = config.validate();
      
      expect(errors, contains('connectTimeout must be greater than 0'));
      expect(config.isValid, isFalse);
    });

    test('returns error for negative connectTimeout', () {
      final config = EnvironmentConfig.dev.copyWith(connectTimeout: -1);
      final errors = config.validate();
      
      expect(errors, contains('connectTimeout must be greater than 0'));
      expect(config.isValid, isFalse);
    });

    test('returns error for zero receiveTimeout', () {
      final config = EnvironmentConfig.dev.copyWith(receiveTimeout: 0);
      final errors = config.validate();
      
      expect(errors, contains('receiveTimeout must be greater than 0'));
      expect(config.isValid, isFalse);
    });

    test('returns error for zero sendTimeout', () {
      final config = EnvironmentConfig.dev.copyWith(sendTimeout: 0);
      final errors = config.validate();
      
      expect(errors, contains('sendTimeout must be greater than 0'));
      expect(config.isValid, isFalse);
    });

    test('returns error for empty appVersion', () {
      final config = EnvironmentConfig.dev.copyWith(appVersion: '');
      final errors = config.validate();
      
      expect(errors, contains('appVersion cannot be empty'));
      expect(config.isValid, isFalse);
    });

    test('returns multiple errors for invalid config', () {
      final config = EnvironmentConfig.dev.copyWith(
        baseUrl: '',
        connectTimeout: 0,
        appVersion: '',
      );
      final errors = config.validate();
      
      expect(errors.length, greaterThanOrEqualTo(3));
      expect(config.isValid, isFalse);
    });
  });

  group('EnvironmentConfig.copyWith', () {
    test('creates a copy with updated baseUrl', () {
      const original = EnvironmentConfig.dev;
      final copy = original.copyWith(baseUrl: 'http://custom.com');
      
      expect(copy.baseUrl, equals('http://custom.com'));
      expect(copy.environment, equals(original.environment));
      expect(copy.connectTimeout, equals(original.connectTimeout));
    });

    test('creates a copy with updated timeout values', () {
      const original = EnvironmentConfig.dev;
      final copy = original.copyWith(
        connectTimeout: 20000,
        receiveTimeout: 25000,
        sendTimeout: 30000,
      );
      
      expect(copy.connectTimeout, equals(20000));
      expect(copy.receiveTimeout, equals(25000));
      expect(copy.sendTimeout, equals(30000));
    });

    test('creates a copy with updated flags', () {
      const original = EnvironmentConfig.dev;
      final copy = original.copyWith(
        enableDebugLogs: false,
        enableErrorReporting: true,
      );
      
      expect(copy.enableDebugLogs, isFalse);
      expect(copy.enableErrorReporting, isTrue);
    });

    test('creates an identical copy when no values provided', () {
      const original = EnvironmentConfig.dev;
      final copy = original.copyWith();
      
      expect(copy, equals(original));
    });
  });

  group('EnvironmentConfig equality', () {
    test('identical configs are equal', () {
      expect(EnvironmentConfig.dev, equals(EnvironmentConfig.dev));
    });

    test('same environment configs are equal', () {
      const config1 = EnvironmentConfig.dev;
      const config2 = EnvironmentConfig.dev;
      expect(config1, equals(config2));
    });

    test('different environment configs are not equal', () {
      expect(EnvironmentConfig.dev, isNot(equals(EnvironmentConfig.prod)));
    });

    test('configs with different values are not equal', () {
      final config1 = EnvironmentConfig.dev;
      final config2 = EnvironmentConfig.dev.copyWith(baseUrl: 'http://different.com');
      expect(config1, isNot(equals(config2)));
    });
  });

  group('EnvironmentConfig.toString', () {
    test('contains environment name', () {
      const config = EnvironmentConfig.dev;
      expect(config.toString(), contains('development'));
    });

    test('contains baseUrl', () {
      const config = EnvironmentConfig.dev;
      expect(config.toString(), contains(config.baseUrl));
    });

    test('contains timeout values', () {
      const config = EnvironmentConfig.dev;
      expect(config.toString(), contains('connectTimeout'));
      expect(config.toString(), contains('receiveTimeout'));
    });
  });
}
