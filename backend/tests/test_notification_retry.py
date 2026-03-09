"""
测试通知服务的熔断器和重试机制
"""

import time
from unittest.mock import Mock, patch

import pytest
from app.models.notification_model import Notification
from app.services.notification_service import NotificationService
from conftest import TEST_CONFIG


class TestNotificationServiceRetryAndCircuitBreaker:
    """测试通知服务的重试和熔断机制"""

    def test_retry_with_exponential_backoff(self):
        """测试指数退退重试机制"""
        service = NotificationService()

        # 创建通知对象
        notification = Notification(
            user_id="test_user",
            title="Test",
            content="Test content",
            channel="push",
            retry_count=0,
        )

        # 模拟 _try_send_by_channel 方法
        with patch.object(
            service,
            "_try_send_by_channel",
            side_effect=[
                {"success": False, "error": "Fail"},
                {"success": False, "error": "Fail"},
                {"success": True},
            ],
        ):
            # 模拟数据库 session
            mock_db = Mock()
            with patch.object(service, "_mark_notification_sent"):
                with patch.object(service, "_mark_notification_failed"):
                    service._send_notification_directly(notification, "push")

            # 验证调用了3次（第1次 + 2次重试）
            assert service._try_send_by_channel.call_count == 3

    def test_circuit_breaker_opens_after_threshold(self):
        """测试熔断器在达到阈值后打开"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 5

        # 直接记录5次失败
        for i in range(5):
            service._record_circuit_breaker_failure("push")

        # 熔断器应该已打开
        assert service._check_circuit_breaker("push") is False

    def test_circuit_breaker_allows_after_timeout(self):
        """测试熔断器在超时后允许重试"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 5
        # 使用配置文件中的超时时间（默认1秒用于快速测试）
        test_timeout = 1  # 可以根据需要调整为 TEST_CONFIG["timeout"]["unit_test"]
        service.CIRCUIT_BREAKER_TIMEOUT = test_timeout  # 修改熔断器超时时间

        # 直接记录5次失败
        for i in range(5):
            service._record_circuit_breaker_failure("push")

        # 熔断器应该已打开
        assert service._check_circuit_breaker("push") is False

        # 等待超时（额外加0.5秒以确保时间充足）
        time.sleep(test_timeout + 0.5)

        # 熔断器应该已重置
        assert service._check_circuit_breaker("push") is True

    def test_circuit_breaker_resets_on_success(self):
        """测试成功发送后熔断器重置"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 5

        # 直接记录3次失败（未达到熔断阈值）
        for i in range(3):
            service._record_circuit_breaker_failure("push")

        # 熔断器应该未打开
        assert service._check_circuit_breaker("push") is True

        # 记录成功
        service._record_circuit_breaker_success("push")

        # 成功发送后，失败计数应该重置
        assert service._circuit_breaker_failures.get("push", 0) == 0

    def test_retry_delays(self):
        """测试重试延迟是否为指数退退"""
        service = NotificationService()

        # 验证重试延迟配置
        assert service.RETRY_DELAYS == [1, 2, 4]
        assert service.MAX_RETRIES == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
