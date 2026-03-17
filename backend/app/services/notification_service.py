"""
消息通知服务

此模块作为门面模式实现，重新导出 notification 包中的所有服务。
为了保持向后兼容，支持从 app.services.notification_service 导入。

新的服务结构：
- app/services/notification/circuit_breaker_service.py
- app/services/notification/notification_sender_service.py
- app/services/notification/notification_template_service.py
- app/services/notification/notification_stats_service.py
- app/services/notification/notification_facade.py (门面)

使用示例:
    >>> from app.services.notification import NotificationService
    >>> # 或者
    >>> from app.services.notification_service import NotificationService
"""

# 重新导出 notification 包中的所有公共服务
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
