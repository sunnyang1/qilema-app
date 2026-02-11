import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/signin/services/signin_api.dart';

/// 签到状态
enum SigninStatus { initial, loading, checkedIn, notCheckedIn, error }

/// 签到历史项
class SigninHistoryItem {
  final String checkinId;
  final DateTime checkinTime;
  final String status;

  SigninHistoryItem({
    required this.checkinId,
    required this.checkinTime,
    required this.status,
  });

  factory SigninHistoryItem.fromJson(Map<String, dynamic> json) {
    return SigninHistoryItem(
      checkinId: json['checkin_id'] ?? '',
      checkinTime: DateTime.parse(json['checkin_time'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'completed',
    );
  }
}

/// 签到状态类
class SigninState {
  final SigninStatus status;
  final int? streakDays;
  final String? lastCheckinTime;
  final String? errorMessage;
  final List<SigninHistoryItem> historyItems;
  final int historyPage;
  final bool hasMoreHistory;
  final bool isLoadingHistory;

  const SigninState({
    this.status = SigninStatus.initial,
    this.streakDays,
    this.lastCheckinTime,
    this.errorMessage,
    this.historyItems = const [],
    this.historyPage = 1,
    this.hasMoreHistory = true,
    this.isLoadingHistory = false,
  });

  SigninState copyWith({
    SigninStatus? status,
    int? streakDays,
    String? lastCheckinTime,
    String? errorMessage,
    List<SigninHistoryItem>? historyItems,
    int? historyPage,
    bool? hasMoreHistory,
    bool? isLoadingHistory,
  }) {
    return SigninState(
      status: status ?? this.status,
      streakDays: streakDays ?? this.streakDays,
      lastCheckinTime: lastCheckinTime ?? this.lastCheckinTime,
      errorMessage: errorMessage ?? this.errorMessage,
      historyItems: historyItems ?? this.historyItems,
      historyPage: historyPage ?? this.historyPage,
      hasMoreHistory: hasMoreHistory ?? this.hasMoreHistory,
      isLoadingHistory: isLoadingHistory ?? this.isLoadingHistory,
    );
  }

  bool get isCheckedIn => status == SigninStatus.checkedIn;
  bool get isLoading => status == SigninStatus.loading;
}

/// 签到状态管理器
class SigninNotifier extends Notifier<SigninState> {
  late final SigninApi _api;

  @override
  SigninState build() {
    _api = SigninApi();
    _loadStatus();
    return const SigninState();
  }

  /// 加载签到状态
  Future<void> _loadStatus() async {
    state = state.copyWith(status: SigninStatus.loading);
    try {
      final data = await _api.getStatus();
      state = SigninState(
        status: data['today_checked_in']
            ? SigninStatus.checkedIn
            : SigninStatus.notCheckedIn,
        streakDays: data['streak_days'],
        lastCheckinTime: data['last_checkin_time'],
      );
    } catch (e) {
      state = state.copyWith(
        status: SigninStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 签到
  Future<void> checkIn() async {
    state = state.copyWith(status: SigninStatus.loading);
    try {
      final data = await _api.checkIn();
      state = SigninState(
        status: SigninStatus.checkedIn,
        streakDays: data['streak_days'],
        lastCheckinTime: data['check_in_time'],
      );
    } catch (e) {
      state = state.copyWith(
        status: SigninStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  /// 刷新状态
  Future<void> refresh() async {
    await _loadStatus();
  }

  /// 加载签到历史
  Future<void> loadHistory({bool refresh = false}) async {
    if (state.isLoadingHistory || (!state.hasMoreHistory && !refresh)) {
      return;
    }

    state = state.copyWith(
      isLoadingHistory: true,
      historyPage: refresh ? 1 : state.historyPage,
      historyItems: refresh ? [] : state.historyItems,
    );

    try {
      final data = await _api.getHistory(
        page: state.historyPage,
        limit: 20,
      );

      final newItems = (data['items'] as List?)
              ?.map((item) => SigninHistoryItem.fromJson(item))
              .toList() ??
          [];

      state = state.copyWith(
        historyItems: [...state.historyItems, ...newItems],
        hasMoreHistory: newItems.length == 20,
        historyPage: state.historyPage + 1,
        isLoadingHistory: false,
      );
    } catch (e) {
      state = state.copyWith(
        errorMessage: e.toString(),
        isLoadingHistory: false,
      );
    }
  }

  /// 刷新历史记录
  Future<void> refreshHistory() async {
    await loadHistory(refresh: true);
  }
}

/// 签到状态Provider
final signinProvider = NotifierProvider<SigninNotifier, SigninState>(SigninNotifier.new);
