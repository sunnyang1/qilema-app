"""
通知降级策略测试套件

测试通知渠道降级策略的各种场景
@deprecated: 这些测试针对旧架构，需要重写以适配新服务结构
"""

from unittest.mock import Mock

import pytest
from app.core.notification_simulators import NotificationServiceConfig
from app.services.notification import NotificationService

pytestmark = pytest.mark.skip(reason="这些测试需要重写以适配新的服务架构 (Facade + 子服务)")


class TestNotificationDegradationStrategy:
    """测试通知降级策略"""

    def test_degradation_enabled(self):
        """测试降级策略启用"""
        mock_db = Mock()
        service = NotificationService(mock_db)
        assert service.config.is_degradation_enabled() is True
