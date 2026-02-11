import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/emergency/services/emergency_api.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 资源类型
enum ResourceType { aed, hospital }

/// 加载状态
enum LoadingState { initial, loading, success, error }

/// 急救资源状态
class EmergencyState {
  final LoadingState state;
  final List<AedDevice> aedDevices;
  final List<Hospital> hospitals;
  final double? currentLat;
  final double? currentLng;
  final String? errorMessage;
  final ResourceType selectedType;

  const EmergencyState({
    this.state = LoadingState.initial,
    this.aedDevices = const [],
    this.hospitals = const [],
    this.currentLat,
    this.currentLng,
    this.errorMessage,
    this.selectedType = ResourceType.aed,
  });

  EmergencyState copyWith({
    LoadingState? state,
    List<AedDevice>? aedDevices,
    List<Hospital>? hospitals,
    double? currentLat,
    double? currentLng,
    String? errorMessage,
    ResourceType? selectedType,
  }) {
    return EmergencyState(
      state: state ?? this.state,
      aedDevices: aedDevices ?? this.aedDevices,
      hospitals: hospitals ?? this.hospitals,
      currentLat: currentLat ?? this.currentLat,
      currentLng: currentLng ?? this.currentLng,
      errorMessage: errorMessage ?? this.errorMessage,
      selectedType: selectedType ?? this.selectedType,
    );
  }

  bool get isLoading => state == LoadingState.loading;
  bool get hasError => state == LoadingState.error;
  bool get hasData => aedDevices.isNotEmpty || hospitals.isNotEmpty;
  bool get hasLocation => currentLat != null && currentLng != null;
}

/// 急救资源状态管理
class EmergencyNotifier extends Notifier<EmergencyState> {
  @override
  EmergencyState build() => const EmergencyState();

  /// 设置当前位置
  void setLocation(double lat, double lng) {
    state = state.copyWith(
      currentLat: lat,
      currentLng: lng,
    );
  }

  /// 切换资源类型
  void switchResourceType(ResourceType type) {
    state = state.copyWith(selectedType: type);
  }

  /// 加载附近的AED设备
  Future<void> loadNearbyAeds() async {
    if (state.currentLat == null || state.currentLng == null) {
      state = state.copyWith(
        state: LoadingState.error,
        errorMessage: '请先获取当前位置',
      );
      return;
    }

    state = state.copyWith(state: LoadingState.loading);

    try {
      final devices = await EmergencyApi.getNearbyAeds(
        latitude: state.currentLat!,
        longitude: state.currentLng!,
      );

      state = state.copyWith(
        state: LoadingState.success,
        aedDevices: devices,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载AED设备失败', error: e);
      state = state.copyWith(
        state: LoadingState.error,
        errorMessage: '加载AED设备失败: ${e.toString()}',
      );
    }
  }

  /// 加载附近的医院
  Future<void> loadNearbyHospitals() async {
    if (state.currentLat == null || state.currentLng == null) {
      state = state.copyWith(
        state: LoadingState.error,
        errorMessage: '请先获取当前位置',
      );
      return;
    }

    state = state.copyWith(state: LoadingState.loading);

    try {
      final hospitals = await EmergencyApi.getNearbyHospitals(
        latitude: state.currentLat!,
        longitude: state.currentLng!,
      );

      state = state.copyWith(
        state: LoadingState.success,
        hospitals: hospitals,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载医院失败', error: e);
      state = state.copyWith(
        state: LoadingState.error,
        errorMessage: '加载医院失败: ${e.toString()}',
      );
    }
  }

  /// 刷新当前选中的资源
  Future<void> refresh() async {
    if (state.selectedType == ResourceType.aed) {
      await loadNearbyAeds();
    } else {
      await loadNearbyHospitals();
    }
  }

  /// 清除错误
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}

/// 急救资源Provider
final emergencyProvider = NotifierProvider<EmergencyNotifier, EmergencyState>(EmergencyNotifier.new);
