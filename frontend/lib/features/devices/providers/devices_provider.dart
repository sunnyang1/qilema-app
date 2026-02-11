import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/core/models/base_state.dart';
import 'package:qilema_app/core/providers/base_notifier.dart';
import 'package:qilema_app/core/constants/loading_state.dart';
import 'package:qilema_app/features/devices/services/devices_api.dart';

/// 设备状态类
base class DevicesState extends BaseState {
  final List<Device> devices;
  final List<Device> scannedDevices;

  const DevicesState({
    super.status = LoadingState.initial,
    this.devices = const [],
    this.scannedDevices = const [],
    super.errorMessage,
  });

  @override
  DevicesState copyWith({
    LoadingState? status,
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

  bool get isScanning => scannedDevices.isNotEmpty;
  bool get isEmpty => devices.isEmpty;

  @override
  List<Object?> get props => [status, devices, scannedDevices, errorMessage];
}

/// 设备状态管理器
base class DevicesNotifier extends Notifier<DevicesState> with BaseNotifierMixin<DevicesState> {
  late final DevicesApi _api;

  @override
  DevicesState build() {
    _api = DevicesApi();
    load();
    return const DevicesState();
  }

  /// 加载设备列表
  @override
  Future<void> load() async {
    state = state.copyWith(status: LoadingState.loading);
    try {
      final devices = await _api.getDevices();
      state = DevicesState(
        status: LoadingState.loaded,
        devices: devices,
      );
    } catch (e) {
      state = state.copyWith(
        status: LoadingState.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 扫描蓝牙设备
  Future<void> scanDevices() async {
    state = state.copyWith(status: LoadingState.loading);
    try {
      final scannedDevices = await _api.scanBluetoothDevices();
      state = state.copyWith(
        status: LoadingState.loaded,
        scannedDevices: scannedDevices,
      );
    } catch (e) {
      state = state.copyWith(
        status: LoadingState.error,
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
