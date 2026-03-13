"""
SendGrid邮件适配器集成测试

测试适配器的各项功能，包括模拟器模式和真实服务接口
"""

import os
from unittest.mock import patch

from app.core.adapters.adapter_factory import AdapterFactory
from app.core.adapters.sendgrid_adapter import SendGridAdapter, create_sendgrid_adapter


class TestSendGridAdapterSimulator:
    """测试邮件适配器 - 模拟器模式"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "false"
        self.adapter = SendGridAdapter(
            enabled=True,
            success_rate=100.0,
            api_key="test_key",
            from_email="test@qilema.com",
            from_name="测试",
        )

    def test_init_default(self):
        """测试默认初始化"""
        adapter = SendGridAdapter()
        assert adapter.use_real_service is False
        assert adapter.enabled is True

    def test_send_email_success(self):
        """测试发送邮件成功"""
        result = self.adapter.send(
            to_email="user@example.com", subject="测试邮件", content="这是测试邮件内容"
        )

        assert result["status"] == "success"
        assert result["data"]["to_email"] == "user@example.com"

    def test_send_email_with_html(self):
        """测试发送HTML邮件"""
        result = self.adapter.send(
            to_email="user@example.com",
            subject="测试HTML邮件",
            content="纯文本内容",
            html_content="<h1>HTML内容</h1>",
        )

        assert result["status"] == "success"
        assert result["data"]["has_html"] is True

    def test_send_email_disabled(self):
        """测试禁用状态下发送邮件"""
        disabled_adapter = SendGridAdapter(enabled=False)
        result = disabled_adapter.send(
            to_email="user@example.com", subject="测试", content="内容"
        )

        assert result["status"] == "disabled"

    def test_get_send_statistics_simulator(self):
        """测试模拟器模式下的统计查询"""
        stats = self.adapter.get_send_statistics(days=7)

        assert stats["status"] == "success"
        assert stats["data"]["total_sent"] == 100


class TestSendGridAdapterRealService:
    """测试邮件适配器 - 真实服务接口（使用Mock）"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "true"

    @patch("app.core.adapters.sendgrid_adapter.SendGridAdapter._init_sendgrid_client")
    def test_init_real_service(self, mock_init):
        """测试真实服务初始化"""
        adapter = SendGridAdapter(
            api_key="real_key", from_email="noreply@qilema.com", from_name="起了吗"
        )

        assert adapter.use_real_service is True
        assert adapter.from_email == "noreply@qilema.com"
        mock_init.assert_called_once()


class TestSendGridFactory:
    """测试邮件适配器工厂"""

    def test_create_email_adapter_simulator(self):
        """测试创建邮件模拟器"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import EmailNotificationSimulator

        adapter = AdapterFactory.create_email_adapter()

        assert isinstance(adapter, EmailNotificationSimulator)

    @patch("app.core.adapters.sendgrid_adapter.SendGridAdapter._init_sendgrid_client")
    def test_create_email_adapter_real(self, mock_init):
        """测试创建真实邮件适配器"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "true"

        adapter = AdapterFactory.create_email_adapter()

        assert isinstance(adapter, SendGridAdapter)
        assert adapter.use_real_service is True


class TestCreateSendGridAdapter:
    """测试创建SendGrid适配器函数"""

    def test_create_with_config(self):
        """测试使用配置创建"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "false"

        config = {
            "enabled": True,
            "from_email": "admin@qilema.com",
            "from_name": "管理员",
        }

        adapter = create_sendgrid_adapter(config)

        assert adapter.from_email == "admin@qilema.com"
        assert adapter.from_name == "管理员"

    def test_create_default(self):
        """测试使用默认配置创建"""
        os.environ["EMAIL_USE_REAL_SERVICE"] = "false"

        adapter = create_sendgrid_adapter()

        assert adapter.enabled is True
