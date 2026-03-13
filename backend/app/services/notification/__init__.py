"""
通知服务模块

提供完整的通知服务功能：
- CircuitBreakerService: 熔断器服务
- NotificationSenderService: 通知发送服务
- NotificationTemplateService: 通知模板服务
- NotificationStatsService: 通知统计服务
- NotificationService: 门面服务，整合以上所有服务
"""

from app.services.notification.circuit_breaker_service import CircuitBreakerService
from app.services.notification.notification_facade import NotificationService
from app.services.notification.notification_sender_service import (
    NotificationSenderService,
)
from app.services.notification.notification_stats_service import (
    NotificationStatsService,
)
from app.services.notification.notification_template_service import (
    NotificationTemplate,
    NotificationTemplateService,
)

__all__ = [
    "CircuitBreakerService",
    "NotificationSenderService",
    "NotificationTemplateService",
    "NotificationTemplate",
    "NotificationStatsService",
    "NotificationService",
]
