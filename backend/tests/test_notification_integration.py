"""
通知服务集成测试套件

测试通知服务的端到端集成，包括模拟器、降级策略等
"""

from unittest.mock import Mock, patch

from app.core.notification_simulators import NotificationServiceConfig
from app.models.notification_model import Notification
from app.schemas.notification import (
    NotificationChannelEnum,
    NotificationPriorityEnum,
    NotificationTypeEnum,
    SendNotificationRequest,
)
from app.services.notification_service import NotificationService
from sqlalchemy.orm import Session


class TestNotificationServiceIntegration:
    """测试通知服务集成"""

    def test_service_initialization(self):
        """测试服务初始化"""
        service = NotificationService()
        assert service.config is not None
        assert service.push_simulator is not None
        assert service.sms_simulator is not None
        assert service.phone_simulator is not None
        assert service.email_simulator is not None

    def test_service_with_custom_config(self):
        """测试使用自定义配置初始化服务"""
        config = NotificationServiceConfig()
        service = NotificationService(config)
        assert service.config == config

    def test_send_push_notification_integration(self):
        """测试发送推送通知的集成"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试推送"
        notification.content = "这是一条测试推送"
        notification.user_id = "test_user"
        notification.channel = NotificationChannelEnum.PUSH

        # 模拟获取用户
        with patch.object(service, "_get_user_by_notification") as mock_get_user:
            mock_user = Mock()
            mock_user.phone = "13800138000"
            mock_user.email = "test@example.com"
            mock_get_user.return_value = mock_user

            with patch("app.core.database.get_db") as mock_db:
                mock_session = Mock()
                mock_db.return_value = iter([mock_session])

                # 发送推送通知
                service._send_push_notification(notification)

                # 验证用户信息被获取
                mock_get_user.assert_called_once()

    def test_send_sms_notification_integration(self):
        """测试发送短信通知的集成"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试短信"
        notification.content = "这是一条测试短信"
        notification.user_id = "test_user"
        notification.channel = NotificationChannelEnum.SMS

        # 模拟获取用户
        with patch.object(service, "_get_user_by_notification") as mock_get_user:
            mock_user = Mock()
            mock_user.phone = "13800138000"
            mock_user.email = "test@example.com"
            mock_get_user.return_value = mock_user

            with patch("app.core.database.get_db") as mock_db:
                mock_session = Mock()
                mock_db.return_value = iter([mock_session])

                # 发送短信通知
                service._send_sms_notification(notification)

                # 验证用户信息被获取
                mock_get_user.assert_called_once()

    def test_send_phone_notification_integration(self):
        """测试发送电话通知的集成"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试电话"
        notification.content = "这是一条测试电话"
        notification.recipient_type = "emergency_contact"
        notification.recipient_id = "contact_001"

        # 模拟获取紧急联系人
        with patch.object(service, "_get_emergency_contact") as mock_get_contact:
            mock_contact = Mock()
            mock_contact.phone_number = "13900139000"
            mock_get_contact.return_value = mock_contact

            with patch("app.core.database.get_db") as mock_db:
                mock_session = Mock()
                mock_db.return_value = iter([mock_session])

                # 发送电话通知
                service._send_phone_notification(notification)

                # 验证联系人信息被获取
                mock_get_contact.assert_called_once()

    def test_send_email_notification_integration(self):
        """测试发送邮件通知的集成"""
        service = NotificationService()
        notification = Mock()
        notification.title = "测试邮件"
        notification.content = "这是一条测试邮件"
        notification.user_id = "test_user"
        notification.channel = NotificationChannelEnum.EMAIL

        # 模拟获取用户
        with patch.object(service, "_get_user_by_notification") as mock_get_user:
            mock_user = Mock()
            mock_user.phone = "13800138000"
            mock_user.email = "test@example.com"
            mock_get_user.return_value = mock_user

            with patch("app.core.database.get_db") as mock_db:
                mock_session = Mock()
                mock_db.return_value = iter([mock_session])

                # 发送邮件通知
                service._send_email_notification(notification)

                # 验证用户信息被获取
                mock_get_user.assert_called_once()


class TestNotificationDegradationIntegration:
    """测试通知降级集成"""

    def test_degradation_flow_push_to_phone(self):
        """测试从push降级到phone的流程"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        notification = Mock()
        notification.title = "紧急通知"
        notification.content = "这是一个紧急通知"
        notification.channel = "push"

        # 模拟push失败，phone成功
        with patch.object(service, "_try_send_by_channel") as mock_send:
            call_count = [0]

            def side_effect(notification, channel):
                call_count[0] += 1
                if channel == "push":
                    return {"success": False, "error": "推送失败"}
                elif channel == "phone":
                    return {"success": True, "error": None}
                return {"success": False, "error": "发送失败"}

            mock_send.side_effect = side_effect

            with patch.object(service, "_mark_notification_sent"):
                service._send_notification_by_channel(notification, "push")

                # 验证尝试了push和phone两个渠道
                assert call_count[0] == 2

    def test_degradation_flow_all_channels_fail(self):
        """测试所有渠道都失败的降级流程"""
        config = NotificationServiceConfig()
        service = NotificationService(config)

        notification = Mock()
        notification.title = "测试通知"
        notification.content = "测试内容"
        notification.channel = "push"

        # 模拟所有渠道都失败
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": False, "error": "发送失败"}

            with patch.object(service, "_mark_notification_failed"):
                service._send_notification_by_channel(notification, "push")

                # 验证尝试了所有渠道
                priority = config.get_channel_priority()
                assert mock_send.call_count == len(priority)

    def test_degradation_disabled_direct_send(self):
        """测试禁用降级时直接发送"""
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

        notification = Mock()
        notification.title = "测试通知"
        notification.content = "测试内容"
        notification.channel = "push"

        # 模拟发送
        with patch.object(service, "_try_send_by_channel") as mock_send:
            mock_send.return_value = {"success": True, "error": None}

            with patch.object(service, "_mark_notification_sent"):
                service._send_notification_by_channel(notification, "push")

                # 验证只尝试了一个渠道
                assert mock_send.call_count == 1


class TestNotificationSimulatorsIntegration:
    """测试通知模拟器集成"""

    def test_push_simulator_send_success(self):
        """测试推送模拟器成功发送"""
        from app.core.notification_simulators import PushNotificationSimulator

        simulator = PushNotificationSimulator(success_rate=100.0)

        result = simulator.send(user_id="user_001", title="测试推送", content="测试内容")

        assert result["status"] == "success"
        assert "message_id" in result["data"]

    def test_sms_simulator_send_success(self):
        """测试短信模拟器成功发送"""
        from app.core.notification_simulators import SMSNotificationSimulator

        simulator = SMSNotificationSimulator(success_rate=100.0)

        result = simulator.send(phone_number="13800138000", content="测试内容")

        assert result["status"] == "success"
        assert "masked_phone" in result["data"]
        assert result["data"]["masked_phone"] == "138****8000"

    def test_phone_simulator_call_success(self):
        """测试电话模拟器成功拨号"""
        from app.core.notification_simulators import PhoneNotificationSimulator

        simulator = PhoneNotificationSimulator(success_rate=100.0)

        result = simulator.call(phone_number="13800138000", content="测试内容")

        assert result["status"] == "success"
        assert "call_duration" in result["data"]
        assert 5 <= result["data"]["call_duration"] <= 30

    def test_email_simulator_send_success(self):
        """测试邮件模拟器成功发送"""
        from app.core.notification_simulators import EmailNotificationSimulator

        simulator = EmailNotificationSimulator(success_rate=100.0)

        result = simulator.send(
            to_email="test@example.com", subject="测试主题", content="测试内容"
        )

        assert result["status"] == "success"
        assert "masked_email" in result["data"]
        assert result["data"]["masked_email"] == "t***@example.com"


class TestEndToEndFlow:
    """测试端到端流程"""

    def test_complete_notification_flow(self):
        """测试完整的通知流程"""
        service = NotificationService()

        # 创建通知请求
        request = SendNotificationRequest(
            user_id="test_user",
            notification_type=NotificationTypeEnum.ALERT,
            channel=NotificationChannelEnum.PUSH,
            priority=NotificationPriorityEnum.NORMAL,
            title="测试通知",
            content="这是一条测试通知",
        )

        # 模拟数据库会话
        mock_db = Mock(spec=Session)

        with patch.object(service, "_get_or_create_preference") as mock_get_pref:
            # 直接跳过通知类型和mute检查
            with patch.object(service, "_is_notification_enabled", return_value=True):
                with patch.object(
                    service, "_select_notification_channel", return_value="push"
                ):
                    # 模拟创建通知
                    mock_notification = Mock(spec=Notification)
                    mock_notification.title = "测试通知"
                    mock_notification.user_id = "test_user"

                    with patch.object(
                        service, "_create_and_send_notification"
                    ) as mock_create:
                        mock_create.return_value = mock_notification

                        # 发送通知
                        result = service.send_notification(mock_db, request)

                        # 验证通知被发送
                        assert result is not None
                        assert result.title == "测试通知"

    def test_notification_failure_handling(self):
        """测试通知失败的处理"""
        service = NotificationService()

        notification = Mock(spec=Notification)
        notification.title = "失败通知"
        notification.status = "pending"
        notification.retry_count = 0

        # 模拟数据库会话
        notification._sa_instance_state = Mock()
        notification._sa_instance_state.session = Mock()

        # 标记通知失败
        service._mark_notification_failed(notification, "网络连接失败")

        # 验证通知状态和重试次数
        assert notification.status == "failed"
        assert notification.error_message == "网络连接失败"
        assert notification.retry_count == 1
