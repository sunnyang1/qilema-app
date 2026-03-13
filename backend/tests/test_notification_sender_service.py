"""
通知发送服务单元测试
"""

from unittest.mock import MagicMock, patch

import pytest
from app.services.notification import CircuitBreakerService, NotificationSenderService


class TestNotificationSenderService:
    """通知发送服务测试类"""

    def test_send_with_retry_success_first_attempt(self):
        """测试第一次尝试就成功"""
        service = NotificationSenderService()
        service.max_retries = 3

        # Mock 发送方法
        with patch.object(
            service, "_try_send", return_value={"success": True, "error": None}
        ):
            with patch.object(
                service.circuit_breaker, "record_success"
            ) as mock_success:
                result = service.send_with_retry(
                    "sms", phone_number="13800138000", content="test"
                )

        assert result["success"] is True
        mock_success.assert_called_once_with("sms")

    def test_send_with_retry_success_after_retries(self):
        """测试重试后成功"""
        service = NotificationSenderService()
        service.max_retries = 3
        service.retry_delays = [0.1, 0.1]  # 缩短延迟

        # 前两次失败，第三次成功
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                return {"success": False, "error": "network error"}
            return {"success": True, "error": None}

        with patch.object(service, "_try_send", side_effect=side_effect):
            with patch.object(service.circuit_breaker, "record_failure"):
                with patch.object(service.circuit_breaker, "record_success"):
                    result = service.send_with_retry(
                        "sms", phone_number="13800138000", content="test"
                    )

        assert result["success"] is True
        assert call_count[0] == 3

    def test_send_with_retry_all_failures(self):
        """测试所有重试都失败"""
        service = NotificationSenderService()
        service.max_retries = 2
        service.retry_delays = [0.01]  # 缩短延迟

        with patch.object(
            service,
            "_try_send",
            return_value={"success": False, "error": "server error"},
        ):
            with patch.object(
                service.circuit_breaker, "record_failure"
            ) as mock_failure:
                result = service.send_with_retry(
                    "sms", phone_number="13800138000", content="test"
                )

        assert result["success"] is False
        assert "server error" in result["error"]
        mock_failure.assert_called_once_with("sms")

    def test_send_with_degradation_primary_success(self):
        """测试降级策略 - 主渠道成功"""
        service = NotificationSenderService()

        with patch.object(service, "send_with_retry", return_value={"success": True}):
            result = service.send_with_degradation(
                "sms", phone_number="13800138000", content="test"
            )

        assert result["success"] is True
        assert result["channel_used"] == "sms"

    def test_send_with_degradation_fallback_success(self):
        """测试降级策略 - 降级渠道成功"""
        service = NotificationSenderService()
        service.config = MagicMock()
        service.config.get_channel_priority.return_value = ["push", "sms", "email"]
        service.config.is_degradation_enabled.return_value = True

        # sms 失败，push 成功
        def mock_send_with_retry(channel, **kwargs):
            if channel == "sms":
                return {"success": False, "error": "failed"}
            return {"success": True}

        with patch.object(service, "send_with_retry", side_effect=mock_send_with_retry):
            with patch.object(service.circuit_breaker, "check", return_value=True):
                result = service.send_with_degradation(
                    "sms", phone_number="13800138000", content="test"
                )

        assert result["success"] is True
        assert result["channel_used"] == "push"

    def test_send_with_degradation_all_fail(self):
        """测试降级策略 - 所有渠道失败"""
        service = NotificationSenderService()
        service.config = MagicMock()
        service.config.get_channel_priority.return_value = ["push", "sms"]
        service.config.is_degradation_enabled.return_value = True

        with patch.object(
            service,
            "send_with_retry",
            return_value={"success": False, "error": "failed"},
        ):
            with patch.object(service.circuit_breaker, "check", return_value=True):
                result = service.send_with_degradation(
                    "sms", phone_number="13800138000", content="test"
                )

        assert result["success"] is False
        assert "所有通知渠道都发送失败" in result["error"]

    def test_try_send_sms(self):
        """测试发送短信"""
        service = NotificationSenderService()

        with patch.object(
            service.sms_simulator,
            "send",
            return_value={
                "status": "success",
                "message": "发送成功",
                "data": {"message_id": "123"},
            },
        ):
            result = service._try_send(
                "sms", phone_number="13800138000", content="test"
            )

        assert result["success"] is True

    def test_try_send_push(self):
        """测试发送推送"""
        service = NotificationSenderService()

        with patch.object(
            service.push_simulator,
            "send",
            return_value={
                "status": "success",
                "message": "发送成功",
                "data": {"message_id": "456"},
            },
        ):
            result = service._try_send(
                "push", user_id="user123", title="test", content="hello"
            )

        assert result["success"] is True

    def test_try_send_phone(self):
        """测试发送电话"""
        service = NotificationSenderService()

        with patch.object(
            service.phone_simulator,
            "send",
            return_value={
                "status": "success",
                "message": "发送成功",
                "data": {"call_id": "789"},
            },
        ):
            result = service._try_send(
                "phone", phone_number="13800138000", content="test"
            )

        assert result["success"] is True

    def test_try_send_email(self):
        """测试发送邮件"""
        service = NotificationSenderService()

        with patch.object(
            service.email_simulator,
            "send",
            return_value={
                "status": "success",
                "message": "发送成功",
                "data": {"message_id": "abc"},
            },
        ):
            result = service._try_send(
                "email", to_email="test@example.com", subject="test", content="hello"
            )

        assert result["success"] is True

    def test_try_send_invalid_channel(self):
        """测试无效渠道"""
        service = NotificationSenderService()

        result = service._try_send("invalid_channel", content="test")

        assert result["success"] is False
        assert "不支持的通知渠道" in result["error"]

    def test_circuit_breaker_integration(self):
        """测试熔断器集成"""
        circuit_breaker = CircuitBreakerService()
        circuit_breaker.threshold = 1

        service = NotificationSenderService(circuit_breaker=circuit_breaker)
        service.max_retries = 2
        service.retry_delays = [0.01]

        # 第一次调用失败，触发熔断
        with patch.object(
            service, "_try_send", return_value={"success": False, "error": "error"}
        ):
            service.send_with_retry("sms", phone_number="13800138000", content="test")

        # 熔断器应该开启
        assert circuit_breaker.check("sms") is False

    def test_send_push_notification(self):
        """测试 _send_push 方法"""
        service = NotificationSenderService()

        with patch.object(
            service.push_simulator,
            "send",
            return_value={"status": "success", "data": {"message_id": "123"}},
        ):
            result = service._send_push(
                user_id="user123", title="test", content="hello"
            )

        assert result["success"] is True
        assert result["data"]["message_id"] == "123"

    def test_send_sms_notification(self):
        """测试 _send_sms 方法"""
        service = NotificationSenderService()

        with patch.object(
            service.sms_simulator,
            "send",
            return_value={"status": "success", "data": {"message_id": "456"}},
        ):
            result = service._send_sms(phone_number="13800138000", content="hello")

        assert result["success"] is True
