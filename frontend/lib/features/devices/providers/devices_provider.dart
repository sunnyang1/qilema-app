import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/devices/services/devices_api.dart';

/// 设备状态
enum DevicesStatus { initial, loading, loaded, error, scanning }

/// 设备状态类
class DevicesState {
  final DevicesStatus status;
  final List<Device> devices;
  final List<Device> scannedDevices;
  final String? errorMessage;

  const DevicesState({
    this.status = DevicesStatus.initial,
    this.devices = const [],
    this.scannedDevices = const [],
    this.errorMessage,
  });

  DevicesState copyWith({
    DevicesStatus? status,
    List<Device>? devices,
    List<Device>? scannedDevices,
    String? errorMessage,
  }) {
    return DevicesState(
      status: status ?? this.status,
      devices: devices ?? this.devices,
      scannedDevices: scannedDevices ?? this.scannedDevices,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isLoading => status == DevicesStatus.loading;
  bool get isScanning => status == DevicesStatus.scanning;
  bool get isLoaded => status == DevicesStatus.loaded;
  bool get hasError => status == DevicesStatus.error;
  bool get isEmpty => devices.isEmpty;
}

/// 设备状态管理器
class DevicesNotifier extends Notifier<DevicesState> {
  late final DevicesApi _api;

  @override
  DevicesState build() {
    _api = DevicesApi();
    _loadDevices();
    return const DevicesState();
  }

  /// 加载设备列表
  Future<void> _loadDevices() async {
    state = state.copyWith(status: DevicesStatus.loading);
    try {
      final devices = await _api.getDevices();
      state = DevicesState(
        status: DevicesStatus.loaded,
        devices: devices,
      );
    } catch (e) {
      state = state.copyWith(
        status: DevicesStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 刷新设备列表
  Future<void> refresh() async {
    await _loadDevices();
  }

  /// 扫描蓝牙设备
  Future<void> scanDevices() async {
    state = state.copyWith(status: DevicesStatus.scanning);
    try {
      final scannedDevices = await _api.scanBluetoothDevices();
      state = state.copyWith(
        status: DevicesStatus.loaded,
        scannedDevices: scannedDevices,
      );
    } catch (e) {
      state = state.copyWith(
        status: DevicesStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 绑定设备
  Future<void> bindDevice(Device device) async {
    try {
      final newDevice = await _api.bindDevice(device);
      state = state.copyWith(
        devices: [...state.devices, newDevice],
        scannedDevices: state.scannedDevices
            .where((d) => d.deviceId != device.deviceId)
            .toList(),
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 解绑设备
  Future<void> unbindDevice(String deviceId) async {
    try {
      await _api.unbindDevice(deviceId);
      final updatedDevices = state.devices.where((d) => d.deviceId != deviceId).toList();
      state = state.copyWith(devices: updatedDevices);
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// 清除扫描结果
  void clearScannedDevices() {
    state = state.copyWith(scannedDevices: []);
  }
}

/// 设备状态Provider
final devicesProvider = NotifierProvider<DevicesNotifier, DevicesState>(DevicesNotifier.new);
