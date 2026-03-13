"""
熔断器服务单元测试
"""

from unittest.mock import MagicMock, patch

import pytest
from app.services.notification import CircuitBreakerService


class TestCircuitBreakerService:
    """熔断器服务测试类"""

    def test_check_initial_state(self):
        """测试初始状态，熔断器应该关闭"""
        service = CircuitBreakerService()
        assert service.check("sms") is True
        assert service.check("push") is True

    def test_check_after_failures_below_threshold(self):
        """测试失败次数低于阈值时，熔断器应该关闭"""
        service = CircuitBreakerService()
        service.threshold = 5  # 设置阈值为5

        # 记录4次失败（低于阈值）
        for _ in range(4):
            service.record_failure("sms")

        # 熔断器应该仍然关闭
        assert service.check("sms") is True

    def test_check_after_failures_reach_threshold(self):
        """测试失败次数达到阈值时，熔断器应该开启"""
        service = CircuitBreakerService()
        service.threshold = 3  # 设置阈值为3
        service.timeout = 60  # 设置超时60秒

        # 记录3次失败（达到阈值）
        for _ in range(3):
            service.record_failure("sms")

        # 熔断器应该开启
        assert service.check("sms") is False

    def test_record_success_resets_failures(self):
        """测试记录成功后重置失败次数"""
        service = CircuitBreakerService()
        service.threshold = 3

        # 记录2次失败
        service.record_failure("sms")
        service.record_failure("sms")

        # 记录成功
        service.record_success("sms")

        # 熔断器应该关闭
        assert service.check("sms") is True
        assert service._failures.get("sms", 0) == 0

    def test_get_state(self):
        """测试获取熔断器状态"""
        service = CircuitBreakerService()
        service.threshold = 3
        service.timeout = 60

        # 初始状态
        state = service.get_state("sms")
        assert state["channel"] == "sms"
        assert state["failures"] == 0
        assert state["is_open"] is False

        # 记录失败后
        service.record_failure("sms")
        state = service.get_state("sms")
        assert state["failures"] == 1

    def test_reset_single_channel(self):
        """测试重置单个渠道"""
        service = CircuitBreakerService()
        service.threshold = 3

        # 记录失败
        service.record_failure("sms")
        service.record_failure("push")

        # 重置 sms
        service.reset("sms")

        assert service._failures.get("sms") is None
        assert service._failures.get("push") == 1

    def test_reset_all_channels(self):
        """测试重置所有渠道"""
        service = CircuitBreakerService()

        # 记录失败
        service.record_failure("sms")
        service.record_failure("push")

        # 重置所有
        service.reset()

        assert len(service._failures) == 0
        assert len(service._last_failure) == 0

    def test_thread_safety(self):
        """测试线程安全"""
        import threading

        service = CircuitBreakerService()
        service.threshold = 100

        errors = []

        def record_failures():
            try:
                for _ in range(10):
                    service.record_failure("sms")
            except Exception as e:
                errors.append(e)

        # 创建多个线程同时记录失败
        threads = [threading.Thread(target=record_failures) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 应该没有错误
        assert len(errors) == 0
        # 总共应该记录了50次失败
        assert service._failures["sms"] == 50

    def test_persist_enabled_does_not_crash(self):
        """测试启用持久化不会崩溃（Redis 可能不可用）"""
        service = CircuitBreakerService()
        service.persist_enabled = True

        # 这些操作不应该崩溃，即使 Redis 不可用
        service.record_failure("sms")
        service.record_success("sms")
        service._load_from_redis()

        # 验证状态正确
        assert service._failures.get("sms", 0) == 0
