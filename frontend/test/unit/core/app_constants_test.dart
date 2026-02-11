import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/core/constants/app_constants.dart';

void main() {
  group('AppConstants', () {
    test('has correct app name', () {
      expect(AppConstants.appName, equals('起了吗'));
    });

    test('has correct app name in English', () {
      expect(AppConstants.appNameEn, equals('QiLeMa'));
    });

    test('has correct app version', () {
      expect(AppConstants.appVersion, equals('1.0.0'));
    });

    test('has correct build number', () {
      expect(AppConstants.buildNumber, equals('1'));
    });

    test('has correct copyright', () {
      expect(AppConstants.copyright, contains('QiLeMa'));
    });

    test('has correct URLs', () {
      expect(AppConstants.privacyPolicyUrl, contains('qilema.com'));
      expect(AppConstants.termsOfServiceUrl, contains('qilema.com'));
      expect(AppConstants.helpCenterUrl, contains('qilema.com'));
    });
  });

  group('ApiConstants', () {
    test('has correct timeout values', () {
      expect(ApiConstants.defaultConnectTimeout, equals(10000));
      expect(ApiConstants.defaultReceiveTimeout, equals(10000));
      expect(ApiConstants.defaultSendTimeout, equals(10000));
    });

    test('has correct retry settings', () {
      expect(ApiConstants.maxRetries, equals(3));
      expect(ApiConstants.retryDelay, equals(1000));
    });

    test('has correct pagination settings', () {
      expect(ApiConstants.defaultPageSize, equals(20));
      expect(ApiConstants.maxPageSize, equals(100));
    });
  });

  group('UIConstants', () {
    test('spacing values are in ascending order', () {
      expect(UIConstants.spacingXSmall, lessThan(UIConstants.spacingSmall));
      expect(UIConstants.spacingSmall, lessThan(UIConstants.spacingMedium));
      expect(UIConstants.spacingMedium, lessThan(UIConstants.spacingLarge));
      expect(UIConstants.spacingLarge, lessThan(UIConstants.spacingXLarge));
    });

    test('radius values are in ascending order', () {
      expect(UIConstants.radiusSmall, lessThan(UIConstants.radiusMedium));
      expect(UIConstants.radiusMedium, lessThan(UIConstants.radiusLarge));
      expect(UIConstants.radiusLarge, lessThan(UIConstants.radiusXLarge));
    });

    test('font size values are in ascending order', () {
      expect(UIConstants.fontSizeXSmall, lessThan(UIConstants.fontSizeSmall));
      expect(UIConstants.fontSizeSmall, lessThan(UIConstants.fontSizeMedium));
      expect(UIConstants.fontSizeMedium, lessThan(UIConstants.fontSizeLarge));
      expect(UIConstants.fontSizeLarge, lessThan(UIConstants.fontSizeXLarge));
      expect(UIConstants.fontSizeXLarge, lessThan(UIConstants.fontSizeTitle));
      expect(UIConstants.fontSizeTitle, lessThan(UIConstants.fontSizeHeadline));
      expect(UIConstants.fontSizeHeadline, lessThan(UIConstants.fontSizeDisplay));
    });

    test('icon size values are in ascending order', () {
      expect(UIConstants.iconSizeSmall, lessThan(UIConstants.iconSizeMedium));
      expect(UIConstants.iconSizeMedium, lessThan(UIConstants.iconSizeLarge));
      expect(UIConstants.iconSizeLarge, lessThan(UIConstants.iconSizeXLarge));
    });

    test('button constants are positive', () {
      expect(UIConstants.buttonMinHeight, greaterThan(0));
      expect(UIConstants.buttonHorizontalPadding, greaterThan(0));
    });

    test('card constants are positive', () {
      expect(UIConstants.cardPadding, greaterThan(0));
      expect(UIConstants.cardElevation, greaterThanOrEqualTo(0));
    });

    test('input field constants are positive', () {
      expect(UIConstants.inputFieldHeight, greaterThan(0));
      expect(UIConstants.inputFieldPadding, greaterThan(0));
    });

    test('animation durations are positive', () {
      expect(UIConstants.animationShort.inMilliseconds, greaterThan(0));
      expect(UIConstants.animationMedium.inMilliseconds, greaterThan(0));
      expect(UIConstants.animationLong.inMilliseconds, greaterThan(0));
    });

    test('animation durations are in ascending order', () {
      expect(
        UIConstants.animationShort.inMilliseconds,
        lessThan(UIConstants.animationMedium.inMilliseconds),
      );
      expect(
        UIConstants.animationMedium.inMilliseconds,
        lessThan(UIConstants.animationLong.inMilliseconds),
      );
    });
  });

  group('StorageConstants', () {
    test('storage keys are not empty', () {
      expect(StorageConstants.keyAuthToken, isNotEmpty);
      expect(StorageConstants.keyRefreshToken, isNotEmpty);
      expect(StorageConstants.keyUserInfo, isNotEmpty);
      expect(StorageConstants.keyFirstLaunch, isNotEmpty);
      expect(StorageConstants.keyThemeMode, isNotEmpty);
      expect(StorageConstants.keyLocale, isNotEmpty);
      expect(StorageConstants.keyLastLoginTime, isNotEmpty);
      expect(StorageConstants.keyNotificationSettings, isNotEmpty);
    });

    test('storage keys are unique', () {
      final keys = [
        StorageConstants.keyAuthToken,
        StorageConstants.keyRefreshToken,
        StorageConstants.keyUserInfo,
        StorageConstants.keyFirstLaunch,
        StorageConstants.keyThemeMode,
        StorageConstants.keyLocale,
        StorageConstants.keyLastLoginTime,
        StorageConstants.keyNotificationSettings,
      ];
      expect(keys.toSet().length, equals(keys.length));
    });
  });

  group('ErrorMessages', () {
    test('error messages are not empty', () {
      expect(ErrorMessages.genericError, isNotEmpty);
      expect(ErrorMessages.networkError, isNotEmpty);
      expect(ErrorMessages.timeoutError, isNotEmpty);
      expect(ErrorMessages.serverError, isNotEmpty);
      expect(ErrorMessages.unauthorizedError, isNotEmpty);
      expect(ErrorMessages.notFoundError, isNotEmpty);
      expect(ErrorMessages.validationError, isNotEmpty);
      expect(ErrorMessages.emptyDataError, isNotEmpty);
      expect(ErrorMessages.loadFailed, isNotEmpty);
      expect(ErrorMessages.saveFailed, isNotEmpty);
      expect(ErrorMessages.deleteFailed, isNotEmpty);
    });
  });

  group('ValidationConstants', () {
    test('phone regex matches valid phone numbers', () {
      expect(ValidationConstants.phoneRegExp.hasMatch('13800138000'), isTrue);
      expect(ValidationConstants.phoneRegExp.hasMatch('13912345678'), isTrue);
      expect(ValidationConstants.phoneRegExp.hasMatch('15012345678'), isTrue);
    });

    test('phone regex does not match invalid phone numbers', () {
      expect(ValidationConstants.phoneRegExp.hasMatch('1380013800'), isFalse);
      expect(ValidationConstants.phoneRegExp.hasMatch('138001380000'), isFalse);
      expect(ValidationConstants.phoneRegExp.hasMatch('23800138000'), isFalse);
      expect(ValidationConstants.phoneRegExp.hasMatch('1380013800a'), isFalse);
      expect(ValidationConstants.phoneRegExp.hasMatch(''), isFalse);
    });

    test('email regex matches valid emails', () {
      expect(ValidationConstants.emailRegExp.hasMatch('test@example.com'), isTrue);
      expect(ValidationConstants.emailRegExp.hasMatch('user.name@domain.co'), isTrue);
      expect(ValidationConstants.emailRegExp.hasMatch('user+tag@example.com'), isTrue);
    });

    test('email regex does not match invalid emails', () {
      expect(ValidationConstants.emailRegExp.hasMatch('test@'), isFalse);
      expect(ValidationConstants.emailRegExp.hasMatch('@example.com'), isFalse);
      expect(ValidationConstants.emailRegExp.hasMatch('test.example.com'), isFalse);
      expect(ValidationConstants.emailRegExp.hasMatch(''), isFalse);
    });

    test('password length constants are valid', () {
      expect(ValidationConstants.passwordMinLength, greaterThan(0));
      expect(ValidationConstants.passwordMaxLength, greaterThan(ValidationConstants.passwordMinLength));
    });

    test('nickname length constants are valid', () {
      expect(ValidationConstants.nicknameMinLength, greaterThan(0));
      expect(ValidationConstants.nicknameMaxLength, greaterThan(ValidationConstants.nicknameMinLength));
    });

    test('verification code length is positive', () {
      expect(ValidationConstants.verificationCodeLength, greaterThan(0));
    });
  });

  group('FeatureConstants', () {
    test('SOS constants are positive', () {
      expect(FeatureConstants.sosLongPressDuration, greaterThan(0));
    });

    test('location constants are positive', () {
      expect(FeatureConstants.locationUpdateInterval, greaterThan(0));
    });

    test('streak constants are positive', () {
      expect(FeatureConstants.maxStreakDays, greaterThan(0));
    });

    test('medication constants are positive', () {
      expect(FeatureConstants.maxMedicationReminderAdvance, greaterThan(0));
    });

    test('bluetooth constants are positive', () {
      expect(FeatureConstants.bluetoothScanTimeout, greaterThan(0));
    });

    test('contact constants are positive', () {
      expect(FeatureConstants.maxEmergencyContacts, greaterThan(0));
    });

    test('search radius constants are positive', () {
      expect(FeatureConstants.defaultHospitalSearchRadius, greaterThan(0));
      expect(FeatureConstants.defaultAedSearchRadius, greaterThan(0));
    });
  });
}
