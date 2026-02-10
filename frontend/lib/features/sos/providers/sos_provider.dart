import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:qilema_app/features/sos/services/sos_api.dart';

/// SOS状态
enum SosStatus { initial, triggering, triggered, error }

/// SOS状态类
class SosState {
  final SosStatus status;
  final String? sosId;
  final String? errorMessage;
  final double? latitude;
  final double? longitude;
  final bool isLocating;

  const SosState({
    this.status = SosStatus.initial,
    this.sosId,
    this.errorMessage,
    this.latitude,
    this.longitude,
    this.isLocating = false,
  });

  SosState copyWith({
    SosStatus? status,
    String? sosId,
    String? errorMessage,
    double? latitude,
    double? longitude,
    bool? isLocating,
  }) {
    return SosState(
      status: status ?? this.status,
      sosId: sosId ?? this.sosId,
      errorMessage: errorMessage ?? this.errorMessage,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      isLocating: isLocating ?? this.isLocating,
    );
  }

  bool get isTriggering => status == SosStatus.triggering;
  bool get isTriggered => status == SosStatus.triggered;
  bool get hasError => status == SosStatus.error;
}

/// SOS状态管理器
class SosNotifier extends StateNotifier<SosState> {
  final SosApi _api = SosApi();

  SosNotifier() : super(const SosState());

  /// 获取当前GPS位置
  Future<bool> _getCurrentLocation() async {
    try {
      state = state.copyWith(isLocating: true);

      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        serviceEnabled = await Geolocator.openLocationSettings();
        if (!serviceEnabled) {
          throw Exception('位置服务未启用');
        }
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('位置权限被拒绝');
        }
      }

      if (permission == LocationPermission.deniedForever) {
        throw Exception('位置权限被永久拒绝');
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );

      state = state.copyWith(
        latitude: position.latitude,
        longitude: position.longitude,
        isLocating: false,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLocating: false,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  /// 触发SOS
  Future<void> triggerSOS() async {
    if (state.isTriggering) return;

    state = state.copyWith(status: SosStatus.triggering);

    // 先获取位置
    final hasLocation = await _getCurrentLocation();
    if (!hasLocation) {
      state = state.copyWith(
        status: SosStatus.error,
        errorMessage: state.errorMessage ?? '无法获取位置信息',
      );
      return;
    }

    // 触发SOS
    try {
      final data = await _api.triggerSOS(
        latitude: state.latitude!,
        longitude: state.longitude!,
      );

      state = SosState(
        status: SosStatus.triggered,
        sosId: data['sos_id'],
        latitude: data['latitude'],
        longitude: data['longitude'],
      );
    } catch (e) {
      state = state.copyWith(
        status: SosStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 重置状态
  void reset() {
    state = const SosState();
  }
}

/// SOS状态Provider
final sosProvider = StateNotifierProvider<SosNotifier, SosState>((ref) {
  return SosNotifier();
});
