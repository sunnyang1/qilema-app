"""
阿里云短信适配器集成测试

测试适配器的各项功能，包括模拟器模式和真实服务接口
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from app.core.adapters.adapter_factory import AdapterFactory, get_adapter_config
from app.core.adapters.aliyun_sms_adapter import (
    AliyunSMSAdapter,
    create_aliyun_sms_adapter,
)


class TestAliyunSMSAdapterSimulator:
    """测试短信适配器 - 模拟器模式"""

    def setup_method(self):
        """每个测试方法前设置"""
        # 确保使用模拟器模式
        os.environ["SMS_USE_REAL_SERVICE"] = "false"
        self.adapter = AliyunSMSAdapter(
            enabled=True,
            success_rate=100.0,
            access_key_id="test_key",
            access_key_secret="test_secret",
            sign_name="起了吗",
        )

    def test_init_default(self):
        """测试默认初始化"""
        adapter = AliyunSMSAdapter()
        assert adapter.use_real_service is False
        assert adapter.enabled is True
        assert adapter.max_retries == 3

    def test_send_sms_success(self):
        """测试发送短信成功"""
        result = self.adapter.send(
            phone_number="13800138000",
            content="您的验证码是123456",
            template_code="SMS_123456",
            template_params={"code": "123456"},
        )

        assert result["status"] == "success"
        assert result["data"]["phone_number"] == "13800138000"
        assert result["data"]["template_code"] == "SMS_123456"
        assert "message_id" in result["data"]

    def test_send_sms_with_template_params(self):
        """测试使用模板参数发送短信"""
        result = self.adapter.send(
            phone_number="13800138000",
            content="尊敬的用户{{name}}，您的验证码是{{code}}",
            template_code="SMS_TEMPLATE_001",
            template_params={"name": "张三", "code": "654321"},
        )

        assert result["status"] == "success"
        # 模拟器会进行模板变量替换
        assert "654321" in result["data"]["content"]

    def test_send_sms_disabled(self):
        """测试禁用状态下发送短信"""
        disabled_adapter = AliyunSMSAdapter(enabled=False)
        result = disabled_adapter.send(phone_number="13800138000", content="测试内容")

        assert result["status"] == "disabled"

    def test_phone_number_masking(self):
        """测试手机号脱敏"""
        masked = AliyunSMSAdapter._mask_phone_number("13800138000")
        assert masked == "138****8000"

    def test_check_quota_simulator(self):
        """测试模拟器模式下的额度查询"""
        quota = self.adapter.check_quota()

        assert quota["status"] == "success"
        assert quota["data"]["remaining_quota"] == 999999
        assert quota["data"]["is_low"] is False

    def test_get_send_status_simulator(self):
        """测试模拟器模式下的状态查询"""
        status = self.adapter.get_send_status("msg_123456")

        assert status["status"] == "success"
        assert status["data"]["send_status"] == "SUCCESS"


class TestAliyunSMSAdapterRealService:
    """测试短信适配器 - 真实服务接口（使用Mock）"""

    def setup_method(self):
        """每个测试方法前设置"""
        # 设置为真实服务模式
        os.environ["SMS_USE_REAL_SERVICE"] = "true"

    @patch("app.core.adapters.aliyun_sms_adapter.AliyunSMSAdapter._init_aliyun_client")
    def test_init_real_service(self, mock_init):
        """测试真实服务初始化"""
        adapter = AliyunSMSAdapter(
            access_key_id="test_key",
            access_key_secret="test_secret",
            sign_name="起了吗",
        )

        assert adapter.use_real_service is True
        assert adapter.access_key_id == "test_key"
        assert adapter.sign_name == "起了吗"
        mock_init.assert_called_once()

    @patch("app.core.adapters.aliyun_sms_adapter.AliyunSMSAdapter._init_aliyun_client")
    def test_send_real_service_requires_template(self, mock_init):
        """测试真实服务发送需要模板代码"""
        adapter = AliyunSMSAdapter(
            access_key_id="test_key",
            access_key_secret="test_secret",
            sign_name="起了吗",
        )
        adapter.use_real_service = True

        # 不传递template_code应该失败
        result = adapter._send_real(
            phone_number="13800138000", template_code=None, template_params=None
        )

        assert result["status"] == "failed"
        assert result["error_code"] == "template_required"

    def test_error_code_mapping(self):
        """测试错误码映射"""
        # 测试已知的错误码映射
        assert (
            AliyunSMSAdapter._map_error_code("isv.BUSINESS_LIMIT_CONTROL")
            == "rate_limit_exceeded"
        )
        assert (
            AliyunSMSAdapter._map_error_code("isv.MOBILE_NUMBER_ILLEGAL")
            == "invalid_phone"
        )
        assert (
            AliyunSMSAdapter._map_error_code("isv.AMOUNT_NOT_ENOUGH")
            == "insufficient_balance"
        )
        # 测试未知错误码
        assert AliyunSMSAdapter._map_error_code("UNKNOWN_ERROR") == "unknown_error"


class TestAdapterFactory:
    """测试适配器工厂"""

    def test_create_sms_adapter_simulator(self):
        """测试创建短信模拟器"""
        os.environ["SMS_USE_REAL_SERVICE"] = "false"

        adapter = AdapterFactory.create_sms_adapter()

        # 模拟器模式下返回SMSNotificationSimulator
        from app.core.notification_simulators import SMSNotificationSimulator

        assert isinstance(adapter, SMSNotificationSimulator)
        # AliyunSMSAdapter在模拟器模式下也继承SMSNotificationSimulator
        assert (
            not hasattr(adapter, "use_real_service")
            or adapter.use_real_service is False
        )

    def test_create_sms_adapter_real(self):
        """测试创建真实短信适配器"""
        os.environ["SMS_USE_REAL_SERVICE"] = "true"

        with patch.object(AliyunSMSAdapter, "_init_aliyun_client"):
            adapter = AdapterFactory.create_sms_adapter()
            assert adapter.use_real_service is True

    def test_create_push_adapter(self):
        """测试创建推送适配器"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import PushNotificationSimulator

        adapter = AdapterFactory.create_push_adapter()

        assert isinstance(adapter, PushNotificationSimulator)

    def test_create_phone_adapter(self):
        """测试创建电话适配器"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import PhoneNotificationSimulator

        adapter = AdapterFactory.create_phone_adapter()

        assert isinstance(adapter, PhoneNotificationSimulator)

    def test_create_email_adapter(self):
        """测试创建邮件适配器"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import EmailNotificationSimulator

        adapter = AdapterFactory.create_email_adapter()

        assert isinstance(adapter, EmailNotificationSimulator)


class TestAdapterConfig:
    """测试适配器配置"""

    def test_get_adapter_config_sms(self):
        """测试获取短信适配器配置"""
        os.environ["NOTIFICATION_SMS_ENABLED"] = "true"
        os.environ["NOTIFICATION_SMS_SUCCESS_RATE"] = "95.0"
        os.environ["ALIYUN_ACCESS_KEY_ID"] = "test_access_key"
        os.environ["ALIYUN_SMS_SIGN_NAME"] = "测试签名"

        config = get_adapter_config("sms")

        assert config["enabled"] is True
        assert config["success_rate"] == 95.0
        assert config["access_key_id"] == "test_access_key"
        assert config["sign_name"] == "测试签名"

    def test_get_adapter_config_defaults(self):
        """测试获取默认配置"""
        # 清除环境变量
        for key in ["NOTIFICATION_EMAIL_ENABLED", "NOTIFICATION_EMAIL_MAX_RETRIES"]:
            if key in os.environ:
                del os.environ[key]

        config = get_adapter_config("email")

        assert config["enabled"] is True  # 默认值
        assert config["success_rate"] == 100.0
        assert config["max_retries"] == 3


class TestCreateAdapterFunction:
    """测试创建适配器函数"""

    def test_create_aliyun_sms_adapter_with_config(self):
        """测试使用配置创建适配器"""
        os.environ["SMS_USE_REAL_SERVICE"] = "false"

        config = {
            "enabled": True,
            "success_rate": 90.0,
            "access_key_id": "my_key",
            "sign_name": "我的签名",
        }

        adapter = create_aliyun_sms_adapter(config)

        assert adapter.success_rate == 90.0
        assert adapter.access_key_id == "my_key"
        assert adapter.sign_name == "我的签名"

    def test_create_aliyun_sms_adapter_default(self):
        """测试使用默认配置创建适配器"""
        os.environ["SMS_USE_REAL_SERVICE"] = "false"

        adapter = create_aliyun_sms_adapter()

        assert adapter.enabled is True
        assert adapter.max_retries == 3
