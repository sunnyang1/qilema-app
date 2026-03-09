"""
通知降级策略测试套件

测试通知渠道降级策略的各种场景
"""

from unittest.mock import Mock, patch

from app.core.notification_simulators import NotificationServiceConfig
from app.services.notification_service import NotificationService


class TestNotificationDegradationStrategy:
    """测试通知降级策略"""

    def test_degradation_enabled(self):
        """测试降级策略启用"""
        config = NotificationServiceConfig()
        service = NotificationService(config)
        assert service.config.is_degradation_enabled() is True

    def test_degradation_disabled(self):
        """测试降级策略禁用"""
        mock_config = Mock()
        mock_config.is_degradation_enabled.return_value = False
        # 模拟配置方法
        mock_config.get_push_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_sms_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_phone_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_email_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }

        service = NotificationService(mock_config)
        assert service.config.is_degradation_enabled() is False

    def test_channel_priority(self):
        """测试渠道优先级"""
        config = NotificationServiceConfig()
        priority = config.get_channel_priority()

        assert isinstance(priority, list)
        assert len(priority) > 0
        # 默认优先级应该是：phone > sms > push > email
        assert priority[0] == "phone"
        assert "sms" in priority
        assert "push" in priority
        assert "email" in priority

    def test_send_with_degradation_when_enabled(self):
        """测试启用降级时发送通知"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        # 创建模拟通知对象
        notification = Mock()
        notification.title = "测试通知"
        notification.channel = "push"  # 初始渠道是push
        notification.user_id = "test_user"

        # 模拟push失败，phone成功（phone优先级最高）
        with patch.object(service, "_try_send_by_channel") as mock_send:

            def side_effect(notification, channel):
                if channel == "push":
                    return {"success": False, "error": "推送失败"}
                elif channel == "phone":
                    return {"success": True, "error": None}
                return {"success": False, "error": "未知错误"}

            mock_send.side_effect = side_effect

            # 模拟标记发送成功
            with patch.object(service, "_mark_notification_sent"):
                service._send_notification_by_channel(notification, "push")

                # 应该尝试了两个渠道：push和phone
                assert mock_send.call_count == 2

    def test_send_without_degradation_when_disabled(self):
        """测试禁用降级时发送通知"""
        mock_config = Mock()
        mock_config.is_degradation_enabled.return_value = False
        # 模拟配置方法
        mock_config.get_push_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_sms_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_phone_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }
        mock_config.get_email_simulator_config.return_value = {
            "enabled": True,
            "success_rate": 100.0,
            "delay_ms": 0,
            "max_retries": 3,
            "retry_interval_ms": 1000,
        }

        service = NotificationService(mock_config)

        # 创建模拟通知对象
        notification = Mock()
        notification.title = "测试通知"
        notification.channel = "push"

        # 模拟发送
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": True, "error": None}

            with patch.object(service, "_mark_notification_sent"):
                service._send_notification_by_channel(notification, "push")

                # 只尝试一个渠道
                assert mock_send.call_count == 1

    def test_all_channels_failed(self):
        """测试所有渠道都失败的场景"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        notification = Mock()
        notification.title = "测试通知"
        notification.channel = "push"

        # 模拟所有渠道都失败
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": False, "error": "发送失败"}

            with patch.object(service, "_mark_notification_failed"):
                service._send_notification_by_channel(notification, "push")

                # 应该尝试所有渠道
                priority = config.get_channel_priority()
                assert mock_send.call_count == len(priority)

    def test_first_channel_success(self):
        """测试第一个渠道就成功"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        notification = Mock()
        notification.title = "测试通知"
        notification.channel = "phone"

        # 模拟第一个渠道就成功
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": True, "error": None}

            with patch.object(service, "_mark_notification_sent"):
                service._send_notification_by_channel(notification, "phone")

                # 只尝试一个渠道
                assert mock_send.call_count == 1

    def test_invalid_channel_in_priority(self):
        """测试初始渠道不在优先级列表中的场景"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        notification = Mock()
        notification.title = "测试通知"
        notification.channel = "wechat"  # wechat不在默认优先级列表中

        # 模拟发送
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": True, "error": None}

            with patch.object(service, "_mark_notification_sent"):
                with patch.object(service, "_mark_notification_failed"):
                    service._send_notification_by_channel(notification, "wechat")

                    # 应该尝试第一个优先级渠道
                    assert mock_send.call_count == 1


class TestTrySendByChannel:
    """测试_try_send_by_channel方法"""

    def test_send_push_success(self):
        """测试发送推送通知成功"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试推送"

        with patch.object(service, "_send_push_notification"):
            result = service._try_send_by_channel(notification, "push")
            assert result["success"] is True
            assert result["error"] is None

    def test_send_sms_success(self):
        """测试发送短信通知成功"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试短信"

        with patch.object(service, "_send_sms_notification"):
            result = service._try_send_by_channel(notification, "sms")
            assert result["success"] is True
            assert result["error"] is None

    def test_send_phone_success(self):
        """测试发送电话通知成功"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试电话"

        with patch.object(service, "_send_phone_notification"):
            result = service._try_send_by_channel(notification, "phone")
            assert result["success"] is True
            assert result["error"] is None

    def test_send_email_success(self):
        """测试发送邮件通知成功"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试邮件"

        with patch.object(service, "_send_email_notification"):
            result = service._try_send_by_channel(notification, "email")
            assert result["success"] is True
            assert result["error"] is None

    def test_send_invalid_channel(self):
        """测试发送到无效渠道"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试"

        result = service._try_send_by_channel(notification, "invalid_channel")
        assert result["success"] is False
        assert "不支持的通知渠道" in result["error"]

    def test_send_with_exception(self):
        """测试发送时发生异常"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试"

        with patch.object(
            service, "_send_push_notification", side_effect=Exception("发送异常")
        ):
            result = service._try_send_by_channel(notification, "push")
            assert result["success"] is False
            assert "发送异常" in result["error"]
