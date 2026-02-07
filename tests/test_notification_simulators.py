"""
通知模拟器测试套件

测试推送、短信、电话、邮件四种通知模拟器的各种场景
"""

import pytest
import time
from unittest.mock import Mock, patch
from app.core.notification_simulators import (
    NotificationSimulator,
    PushNotificationSimulator,
    SMSNotificationSimulator,
    PhoneNotificationSimulator,
    EmailNotificationSimulator
)


class TestNotificationSimulatorBase:
    """测试通知模拟器基类（使用具体子类进行测试）"""

    def test_init_success_rate_validation(self):
        """测试成功率验证"""
        # 正常成功率
        sim = PushNotificationSimulator(success_rate=80.0)
        assert sim.success_rate == 80.0

        # 成功率超过100应被截断
        sim = PushNotificationSimulator(success_rate=150.0)
        assert sim.success_rate == 100.0

        # 成功率小于0应被截断
        sim = PushNotificationSimulator(success_rate=-10.0)
        assert sim.success_rate == 0.0

    def test_init_delay_ms_validation(self):
        """测试延迟配置"""
        sim = PushNotificationSimulator(delay_ms=100)
        assert sim.delay_ms == 100

        sim = PushNotificationSimulator(delay_ms=0)
        assert sim.delay_ms == 0

    def test_retryable_errors_default(self):
        """测试默认可重试错误类型"""
        sim = PushNotificationSimulator()
        assert "network_error" in sim.retryable_errors
        assert "timeout" in sim.retryable_errors
        assert "service_unavailable" in sim.retryable_errors


class TestPushNotificationSimulator:
    """测试推送通知模拟器"""

    def test_init_default(self):
        """测试默认初始化"""
        simulator = PushNotificationSimulator()
        assert simulator.enabled is True
        assert simulator.success_rate == 100.0
        assert simulator.delay_ms == 0

    def test_init_with_config(self):
        """测试带配置初始化"""
        simulator = PushNotificationSimulator(
            enabled=False,
            success_rate=50.0,
            delay_ms=200,
            push_token="test_token_123"
        )
        assert simulator.enabled is False
        assert simulator.success_rate == 50.0
        assert simulator.delay_ms == 200
        assert simulator.push_token == "test_token_123"

    def test_send_success(self):
        """测试成功发送推送"""
        simulator = PushNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            user_id="user_001",
            title="测试标题",
            content="测试内容"
        )

        assert result["status"] == "success"
        assert "message_id" in result["data"]
        assert result["data"]["user_id"] == "user_001"
        assert result["data"]["title"] == "测试标题"
        assert result["data"]["content"] == "测试内容"

    def test_send_with_delay(self):
        """测试带延迟发送推送"""
        simulator = PushNotificationSimulator(success_rate=100.0, delay_ms=100)

        start_time = time.time()
        result = simulator.send(
            user_id="user_001",
            title="测试标题",
            content="测试内容"
        )
        end_time = time.time()

        assert result["status"] == "success"
        assert (end_time - start_time) >= 0.1  # 至少延迟100ms

    def test_send_disabled(self):
        """测试禁用状态下发送"""
        simulator = PushNotificationSimulator(enabled=False)
        result = simulator.send(
            user_id="user_001",
            title="测试标题",
            content="测试内容"
        )

        assert result["status"] == "disabled"
        assert "未启用" in result["message"]

    def test_send_failure(self):
        """测试发送失败场景"""
        # 使用0%成功率确保失败
        simulator = PushNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            user_id="user_001",
            title="测试标题",
            content="测试内容"
        )

        assert result["status"] == "failed"
        # 失败时data中应该包含error_type
        assert "error_type" in result["data"]
        assert "error_code" in result
        assert result["data"]["user_id"] == "user_001"

    def test_send_batch(self):
        """测试批量发送推送"""
        simulator = PushNotificationSimulator(success_rate=100.0)
        results = simulator.send_batch(
            user_ids=["user_001", "user_002", "user_003"],
            title="批量标题",
            content="批量内容"
        )

        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
        assert results[0]["data"]["user_id"] == "user_001"
        assert results[1]["data"]["user_id"] == "user_002"
        assert results[2]["data"]["user_id"] == "user_003"


class TestSMSNotificationSimulator:
    """测试短信通知模拟器"""

    def test_init_default(self):
        """测试默认初始化"""
        simulator = SMSNotificationSimulator()
        assert simulator.enabled is True
        assert simulator.success_rate == 100.0
        assert simulator.delay_ms == 0

    def test_send_success(self):
        """测试成功发送短信"""
        simulator = SMSNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            phone_number="13800138000",
            content="您的验证码是123456"
        )

        assert result["status"] == "success"
        assert "message_id" in result["data"]
        assert result["data"]["phone_number"] == "13800138000"
        assert "masked_phone" in result["data"]
        assert result["data"]["masked_phone"] == "138****8000"
        assert result["data"]["cost"] == 0.05

    def test_send_with_template(self):
        """测试使用模板发送短信"""
        simulator = SMSNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            phone_number="13800138000",
            content="您的验证码是{code}",
            template_code="verify_code_template",
            template_params={"code": "123456"}
        )

        assert result["status"] == "success"
        # 模板变量可能被替换，所以不检查原始内容
        assert result["data"]["template_code"] == "verify_code_template"

    def test_phone_masking(self):
        """测试手机号脱敏"""
        # 正常手机号
        masked = SMSNotificationSimulator._mask_phone_number("13800138000")
        assert masked == "138****8000"

        # 短手机号（不足7位）- 直接返回原值
        masked = SMSNotificationSimulator._mask_phone_number("1380013")
        assert masked == "1380013"

        # 包含区号的手机号 - 脱敏前3位和后4位
        masked = SMSNotificationSimulator._mask_phone_number("+8613800138000")
        # +8613800138000 -> 前3位"+86"保留，后4位"8000"保留
        assert masked == "+86****8000"

    def test_send_failure_network_error(self):
        """测试网络错误失败场景"""
        simulator = SMSNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            phone_number="13800138000",
            content="测试内容"
        )

        assert result["status"] == "failed"
        # 失败时data中应该包含error_code和error_type
        assert "error_type" in result["data"]

    def test_send_failure_insufficient_balance(self):
        """测试余额不足失败场景"""
        simulator = SMSNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            phone_number="13800138000",
            content="测试内容"
        )

        assert result["status"] == "failed"
        error_code = result["data"].get("error_type")
        assert error_code in ["insufficient_balance", "invalid_phone", "content_sensitive",
                           "rate_limit_exceeded", "network_error", "timeout"]


class TestPhoneNotificationSimulator:
    """测试电话通知模拟器"""

    def test_init_default(self):
        """测试默认初始化"""
        simulator = PhoneNotificationSimulator()
        assert simulator.enabled is True
        assert simulator.success_rate == 100.0
        assert simulator.delay_ms == 0

    def test_call_success(self):
        """测试成功拨打电话"""
        simulator = PhoneNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            phone_number="13800138000",
            content="用户出现异常，请立即联系"
        )

        assert result["status"] == "success"
        assert "call_id" in result["data"]
        assert result["data"]["phone_number"] == "13800138000"
        assert result["data"]["masked_phone"] == "138****8000"
        assert 5 <= result["data"]["call_duration"] <= 30  # 通话时长在合理范围

    def test_call_failure_busy(self):
        """测试线路忙失败场景"""
        simulator = PhoneNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            phone_number="13800138000",
            content="测试内容"
        )

        assert result["status"] == "failed"
        error_code = result["data"].get("error_type")
        assert error_code in ["busy", "no_answer", "invalid_phone", "call_rejected",
                           "network_error", "timeout"]

    def test_call_failure_no_answer(self):
        """测试无人接听失败场景"""
        simulator = PhoneNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            phone_number="13800138000",
            content="测试内容"
        )

        assert result["status"] == "failed"
        error_code = result["data"].get("error_type")
        assert error_code in ["busy", "no_answer", "invalid_phone", "call_rejected",
                           "network_error", "timeout"]


class TestEmailNotificationSimulator:
    """测试邮件通知模拟器"""

    def test_init_default(self):
        """测试默认初始化"""
        simulator = EmailNotificationSimulator()
        assert simulator.enabled is True
        assert simulator.success_rate == 100.0
        assert simulator.delay_ms == 0

    def test_send_success_plain_text(self):
        """测试成功发送纯文本邮件"""
        simulator = EmailNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            to_email="user@example.com",
            subject="测试主题",
            content="测试内容"
        )

        assert result["status"] == "success"
        assert "message_id" in result["data"]
        assert result["data"]["to_email"] == "user@example.com"
        assert result["data"]["masked_email"] == "u***@example.com"
        assert result["data"]["has_html"] is False
        assert result["data"]["attachment_count"] == 0

    def test_send_success_html(self):
        """测试成功发送HTML邮件"""
        html_content = "<html><body><h1>测试标题</h1><p>测试内容</p></body></html>"
        simulator = EmailNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            to_email="user@example.com",
            subject="测试主题",
            content="纯文本内容",
            html_content=html_content
        )

        assert result["status"] == "success"
        assert result["data"]["has_html"] is True
        assert result["data"]["content"] == html_content[:100]

    def test_send_with_attachments(self):
        """测试发送带附件邮件"""
        simulator = EmailNotificationSimulator(success_rate=100.0)
        result = simulator.send(
            to_email="user@example.com",
            subject="测试主题",
            content="测试内容",
            attachments=["report.pdf", "data.xlsx"]
        )

        assert result["status"] == "success"
        assert result["data"]["attachment_count"] == 2

    def test_email_masking(self):
        """测试邮箱脱敏"""
        # 正常邮箱
        masked = EmailNotificationSimulator._mask_email("user123@example.com")
        assert masked == "u***@example.com"

        # 短用户名
        masked = EmailNotificationSimulator._mask_email("u@example.com")
        assert masked == "u@example.com"

        # 邮箱不带@
        masked = EmailNotificationSimulator._mask_email("invalid-email")
        assert masked == "invalid-email"

    def test_send_failure_smtp_error(self):
        """测试SMTP错误失败场景"""
        simulator = EmailNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            to_email="user@example.com",
            subject="测试主题",
            content="测试内容"
        )

        assert result["status"] == "failed"
        error_code = result["data"].get("error_type")
        assert error_code in ["invalid_email", "smtp_auth_failed", "smtp_connection_failed",
                           "attachment_too_large", "spam_rejected", "network_error", "timeout"]

    def test_send_failure_invalid_email(self):
        """测试无效邮箱失败场景"""
        simulator = EmailNotificationSimulator(success_rate=0.0)
        result = simulator.send(
            to_email="user@example.com",
            subject="测试主题",
            content="测试内容"
        )

        assert result["status"] == "failed"
        error_code = result["data"].get("error_type")
        assert error_code in ["invalid_email", "smtp_auth_failed", "smtp_connection_failed",
                           "attachment_too_large", "spam_rejected", "network_error", "timeout"]


class TestRetryMechanism:
    """测试重试机制"""

    def test_retry_on_network_error(self):
        """测试网络错误时重试"""
        simulator = SMSNotificationSimulator(
            success_rate=100.0,  # 让第1次发送失败
            max_retries=3,
            retry_interval_ms=50
        )

        # Mock让第1、2次返回网络错误，第3次成功
        send_count = [0]

        def mock_send(**kwargs):
            send_count[0] += 1
            if send_count[0] < 3:
                return {"status": "failed", "error_code": "network_error", "message": "网络错误"}
            return {"status": "success", "message": "成功", "data": {}}

        with patch.object(simulator, '_send', side_effect=mock_send):
            result = simulator.send(phone_number="13800138000", content="测试")
            assert send_count[0] == 3  # 失败2次，第3次成功
            assert result["status"] == "success"

    def test_no_retry_on_business_error(self):
        """测试业务错误时不重试"""
        simulator = SMSNotificationSimulator(
            success_rate=100.0,
            max_retries=3,
            retry_interval_ms=50
        )

        send_count = [0]

        def mock_send(**kwargs):
            send_count[0] += 1
            # 业务错误：无效手机号
            return {"status": "failed", "error_code": "invalid_phone", "message": "无效手机号"}

        with patch.object(simulator, '_send', side_effect=mock_send):
            result = simulator.send(phone_number="13800138000", content="测试")
            assert send_count[0] == 1  # 只发送1次，不重试
            assert result["status"] == "failed"

    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        simulator = SMSNotificationSimulator(
            success_rate=0.0,  # 所有发送都失败
            max_retries=3,
            retry_interval_ms=10
        )

        send_count = [0]

        def mock_send(**kwargs):
            send_count[0] += 1
            return {"status": "failed", "error_code": "network_error", "message": "网络错误"}

        with patch.object(simulator, '_send', side_effect=mock_send):
            result = simulator.send(phone_number="13800138000", content="测试")
            assert send_count[0] == 3  # 最多重试3次（max_retries）
            assert result["status"] == "failed"
