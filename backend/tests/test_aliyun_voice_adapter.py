"""
阿里云语音适配器集成测试

测试适配器的各项功能，包括模拟器模式和真实服务接口
"""

import os
from unittest.mock import patch

from app.core.adapters.adapter_factory import AdapterFactory
from app.core.adapters.aliyun_voice_adapter import (
    AliyunVoiceAdapter,
    create_aliyun_voice_adapter,
)


class TestAliyunVoiceAdapterSimulator:
    """测试语音适配器 - 模拟器模式"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "false"
        self.adapter = AliyunVoiceAdapter(
            enabled=True,
            success_rate=100.0,
            access_key_id="test_key",
            access_key_secret="test_secret",
            called_show_number="0571-12345678",
        )

    def test_init_default(self):
        """测试默认初始化"""
        adapter = AliyunVoiceAdapter()
        assert adapter.use_real_service is False
        assert adapter.enabled is True

    def test_send_voice_success(self):
        """测试发送语音通知成功"""
        result = self.adapter.send(
            phone_number="13800138000",
            content="您好，这是测试语音通知",
            call_type="tts",
        )

        assert result["status"] == "success"
        assert result["data"]["phone_number"] == "13800138000"

    def test_send_verify_code(self):
        """测试发送语音验证码"""
        result = self.adapter.send(
            phone_number="13800138000", content="123456", call_type="verify"
        )

        assert result["status"] == "success"

    def test_send_voice_disabled(self):
        """测试禁用状态下发送语音"""
        disabled_adapter = AliyunVoiceAdapter(enabled=False)
        result = disabled_adapter.send(phone_number="13800138000", content="测试内容")

        assert result["status"] == "disabled"

    def test_call_method(self):
        """测试call方法"""
        result = self.adapter.call(phone_number="13800138000", content="测试语音内容")

        assert result["status"] == "success"

    def test_send_verify_code_method(self):
        """测试send_verify_code便捷方法"""
        result = self.adapter.send_verify_code(
            phone_number="13800138000", code="654321"
        )

        assert result["status"] == "success"

    def test_get_call_status_simulator(self):
        """测试模拟器模式下的通话状态查询"""
        status = self.adapter.get_call_status("call_123456")

        assert status["status"] == "success"
        assert status["data"]["call_status"] == "SUCCESS"


class TestAliyunVoiceAdapterRealService:
    """测试语音适配器 - 真实服务接口（使用Mock）"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "true"

    @patch(
        "app.core.adapters.aliyun_voice_adapter.AliyunVoiceAdapter._init_aliyun_client"
    )
    def test_init_real_service(self, mock_init):
        """测试真实服务初始化"""
        adapter = AliyunVoiceAdapter(
            access_key_id="test_key",
            access_key_secret="test_secret",
            called_show_number="0571-12345678",
        )

        assert adapter.use_real_service is True
        assert adapter.called_show_number == "0571-12345678"
        mock_init.assert_called_once()

    def test_error_code_mapping(self):
        """测试错误码映射"""
        assert (
            AliyunVoiceAdapter._map_error_code("isv.BUSINESS_LIMIT_CONTROL")
            == "rate_limit_exceeded"
        )
        assert (
            AliyunVoiceAdapter._map_error_code("isv.AMOUNT_NOT_ENOUGH")
            == "insufficient_balance"
        )
        assert (
            AliyunVoiceAdapter._map_error_code("isv.INVALID_NUMBER") == "invalid_phone"
        )
        assert AliyunVoiceAdapter._map_error_code("UNKNOWN_ERROR") == "unknown_error"


class TestVoiceAdapterFactory:
    """测试语音适配器工厂"""

    def test_create_phone_adapter_simulator(self):
        """测试创建电话模拟器"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import PhoneNotificationSimulator

        adapter = AdapterFactory.create_phone_adapter()

        assert isinstance(adapter, PhoneNotificationSimulator)

    @patch(
        "app.core.adapters.aliyun_voice_adapter.AliyunVoiceAdapter._init_aliyun_client"
    )
    def test_create_phone_adapter_real(self, mock_init):
        """测试创建真实电话适配器"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "true"

        adapter = AdapterFactory.create_phone_adapter()

        assert isinstance(adapter, AliyunVoiceAdapter)
        assert adapter.use_real_service is True


class TestCreateVoiceAdapter:
    """测试创建语音适配器函数"""

    def test_create_with_config(self):
        """测试使用配置创建"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "false"

        config = {
            "enabled": True,
            "tts_voice": "Siyue",
            "called_show_number": "0571-87654321",
        }

        adapter = create_aliyun_voice_adapter(config)

        assert adapter.tts_voice == "Siyue"
        assert adapter.called_show_number == "0571-87654321"

    def test_create_default(self):
        """测试使用默认配置创建"""
        os.environ["PHONE_USE_REAL_SERVICE"] = "false"

        adapter = create_aliyun_voice_adapter()

        assert adapter.enabled is True
