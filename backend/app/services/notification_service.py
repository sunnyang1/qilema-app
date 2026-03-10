"""
消息通知服务

此模块已重构，NotificationService 现在作为门面模式实现。
为了保持向后兼容，此文件重新导出新的门面服务。

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

# 为了保持向后兼容，重新导出新的门面服务
from app.services.notification import (
    CircuitBreakerService,
    NotificationSenderService,
    NotificationService,
    NotificationStatsService,
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
