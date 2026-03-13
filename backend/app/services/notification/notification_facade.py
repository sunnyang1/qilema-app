"""
通知服务门面

整合所有通知相关服务，提供统一的访问入口
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.cache import invalidate_cache
from app.core.cache_config import CacheConfig
from app.models.emergency_contact import EmergencyContact
from app.models.notification_model import Notification, NotificationPreference
from app.schemas.notification import (
    BatchSendNotificationRequest,
    NotificationChannelEnum,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPriority,
    NotificationQuery,
    NotificationStatistics,
    NotificationStatusEnum,
    NotificationTemplateCreate,
    NotificationTypeEnum,
    SendNotificationRequest,
)
from app.services.base_service import BaseService
from app.services.notification.circuit_breaker_service import CircuitBreakerService
from app.services.notification.notification_sender_service import (
    NotificationSenderService,
)
from app.services.notification.notification_stats_service import (
    NotificationStatsService,
)
from app.services.notification.notification_template_service import (
    NotificationTemplateService,
)
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotificationService(BaseService[Notification]):
    """
    通知服务门面

    整合所有通知相关服务，提供统一的访问入口：
    - 通知发送（委托给 NotificationSenderService）
    - 通知模板（委托给 NotificationTemplateService）
    - 通知统计（委托给 NotificationStatsService）
    - 熔断器（委托给 CircuitBreakerService）

    对外保持 API 不变，内部实现委托给子服务

    使用示例:
        >>> service = NotificationService(db)
        >>> notification = service.send_notification(send_request)
        >>> stats = service.get_statistics(user_id, start_date, end_date)
    """

    # 基类配置
    model_class = Notification
    cache_prefix = CacheConfig.PREFIX_NOTIFICATION
    cache_ttl = CacheConfig.TTL_NOTIFICATION_LIST

    def __init__(self, db: Session):
        """
        初始化通知服务

        Args:
            db: 数据库会话
        """
        self.db = db

        # 初始化子服务
        self._circuit_breaker = CircuitBreakerService()
        self._sender = NotificationSenderService(circuit_breaker=self._circuit_breaker)
        self._template_service = NotificationTemplateService()
        self._stats_service = NotificationStatsService()

        # 暴露 config 以保持向后兼容
        self.config = self._sender.config

    # ========== 通知发送 ==========

    def send_notification(
        self,
        request: SendNotificationRequest,
        recipient_type: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> Optional[Notification]:
        """
        发送通知

        根据通知偏好设置，选择合适的通知渠道发送通知
        """
        preference = self._get_or_create_preference(request.user_id)

        if not self._is_notification_enabled(preference, request):
            return None

        channel = self._select_notification_channel(preference, request)
        if not channel:
            logger.error(f"无法为用户 {request.user_id} 选择通知渠道")
            return None

        notification = self._create_and_send_notification(
            request, channel, recipient_type, recipient_id
        )
        return notification

    def batch_send_notification(
        self, request: BatchSendNotificationRequest
    ) -> List[Notification]:
        """
        批量发送通知

        向多个用户发送相同的通知
        """
        notifications = []

        for user_id in request.user_ids:
            send_request = SendNotificationRequest(
                user_id=user_id,
                notification_type=request.notification_type,
                title=request.title,
                content=request.content,
                channel=request.channel,
                priority=request.priority,
                data=request.data,
            )

            notification = self.send_notification(send_request)
            if notification:
                notifications.append(notification)

        return notifications

    def send_to_emergency_contacts(
        self,
        user_id: str,
        notification_type: NotificationTypeEnum,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.HIGH,
        data: Optional[Dict[str, Any]] = None,
    ) -> List[Notification]:
        """
        向紧急联系人发送通知

        用于签到、预警、SOS等场景
        """
        # 查询紧急联系人
        emergency_contacts = (
            self.db.query(EmergencyContact)
            .filter(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_active.is_(True),
            )
            .all()
        )

        notifications = []

        for contact in emergency_contacts:
            send_request = SendNotificationRequest(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                content=content,
                channel=self._select_contact_channel(contact),
                priority=priority,
                data=data,
                related_type="emergency_contact",
                related_id=contact.id,
            )

            notification = self.send_notification(
                send_request,
                recipient_type="emergency_contact",
                recipient_id=str(contact.id),
            )
            if notification:
                notifications.append(notification)

        return notifications

    def _get_or_create_preference(self, user_id: str) -> NotificationPreference:
        """获取或创建用户通知偏好设置"""
        preference = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

        if not preference:
            preference = self._create_default_preference(user_id)

        return preference

    def _is_notification_enabled(
        self, preference: NotificationPreference, request: SendNotificationRequest
    ) -> bool:
        """检查通知是否应该发送"""
        if not self._is_notification_type_enabled(
            preference, request.notification_type
        ):
            logger.info(f"用户 {request.user_id} 的 {request.notification_type} 通知已禁用")
            return False

        if not self._should_send_during_mute(preference, request):
            logger.info(f"用户 {request.user_id} 当前处于免打扰时段")
            return False

        return True

    def _should_send_during_mute(
        self, preference: NotificationPreference, request: SendNotificationRequest
    ) -> bool:
        """判断免打扰时段是否应该发送通知"""
        if not self._is_mute_enabled(preference):
            return True

        # 紧急通知不受免打扰限制
        return request.priority == NotificationPriority.URGENT

    def _select_notification_channel(
        self, preference: NotificationPreference, request: SendNotificationRequest
    ) -> Optional[str]:
        """选择通知渠道"""
        return request.channel or self._select_channel(
            preference, request.notification_type, request.priority
        )

    def _create_and_send_notification(
        self,
        request: SendNotificationRequest,
        channel: str,
        recipient_type: Optional[str],
        recipient_id: Optional[str],
    ) -> Notification:
        """创建并发送通知"""
        notification = Notification(
            user_id=request.user_id,
            notification_type=request.notification_type,
            channel=channel,
            priority=request.priority,
            title=request.title,
            content=request.content,
            data=request.data,
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            related_type=request.related_type,
            related_id=request.related_id,
            status=NotificationStatusEnum.PENDING,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        self._send_notification(notification, channel)

        return notification

    def _send_notification(self, notification: Notification, channel: str):
        """发送通知"""
        # 构建发送参数
        send_kwargs = self._build_send_kwargs(notification)

        # 使用 sender 服务发送
        result = self._sender.send_with_degradation(channel, **send_kwargs)

        if result["success"]:
            self._mark_notification_sent(notification)
            if result.get("channel_used") and result["channel_used"] != channel:
                notification.channel = NotificationChannelEnum(result["channel_used"])
                self.db.commit()
        else:
            self._mark_notification_failed(notification, result["error"])

    def _build_send_kwargs(self, notification: Notification) -> Dict[str, Any]:
        """构建发送参数"""
        kwargs = {
            "title": notification.title,
            "content": notification.content,
        }

        channel = str(notification.channel)
        if channel == NotificationChannelEnum.PUSH.value:
            kwargs["user_id"] = notification.user_id
            kwargs["data"] = notification.data
        elif channel in [
            NotificationChannelEnum.SMS.value,
            NotificationChannelEnum.PHONE.value,
        ]:
            # 获取用户手机号
            from app.models.user import User

            user = (
                self.db.query(User).filter(User.user_id == notification.user_id).first()
            )
            kwargs["phone_number"] = user.phone if user else ""
        elif channel == NotificationChannelEnum.EMAIL.value:
            # 获取用户邮箱
            from app.models.user import User

            user = (
                self.db.query(User).filter(User.user_id == notification.user_id).first()
            )
            kwargs["to_email"] = user.email if user and user.email else ""
            kwargs["subject"] = notification.title

        return kwargs

    def _mark_notification_sent(self, notification: Notification):
        """标记通知为已发送"""
        notification.status = NotificationStatusEnum.SENT
        notification.sent_at = datetime.utcnow()
        self.db.commit()

    def _mark_notification_failed(self, notification: Notification, error_message: str):
        """标记通知发送失败"""
        logger.error(f"发送通知失败: {error_message}")
        notification.status = NotificationStatusEnum.FAILED
        notification.error_message = error_message
        notification.retry_count += 1
        self.db.commit()

    # ========== 通知记录管理 ==========

    def get_notifications(self, query_params: NotificationQuery) -> List[Notification]:
        """查询通知记录"""
        query = self.db.query(Notification).filter(
            Notification.user_id == query_params.user_id
        )

        if query_params.notification_type:
            query = query.filter(
                Notification.notification_type == query_params.notification_type
            )

        if query_params.channel:
            query = query.filter(Notification.channel == query_params.channel)

        if query_params.status:
            query = query.filter(Notification.status == query_params.status)

        if query_params.priority:
            query = query.filter(Notification.priority == query_params.priority)

        if query_params.start_date:
            query = query.filter(Notification.created_at >= query_params.start_date)

        if query_params.end_date:
            query = query.filter(Notification.created_at <= query_params.end_date)

        if query_params.is_unread is not None:
            if query_params.is_unread:
                query = query.filter(Notification.read_at.is_(None))
            else:
                query = query.filter(Notification.read_at.isnot(None))

        return (
            query.order_by(desc(Notification.created_at))
            .offset(query_params.offset)
            .limit(query_params.limit)
            .all()
        )

    def mark_as_read(self, notification_ids: List[int]) -> int:
        """标记通知为已读"""
        notifications = (
            self.db.query(Notification)
            .filter(Notification.id.in_(notification_ids))
            .all()
        )

        count = 0
        user_ids = set()
        for notification in notifications:
            if notification.read_at is None:
                notification.read_at = datetime.utcnow()
                notification.status = NotificationStatusEnum.READ
                count += 1
                user_ids.add(notification.user_id)

        self.db.commit()

        # 清除相关缓存
        for user_id in user_ids:
            self._invalidate_user_notification_cache(user_id)

        return count

    def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数量"""
        return self._stats_service.get_unread_count(self.db, user_id)

    def _invalidate_user_notification_cache(self, user_id: str):
        """清除用户通知相关缓存"""
        invalidate_cache(
            CacheConfig.make_pattern(CacheConfig.PREFIX_NOTIFICATION_LIST, user_id)
        )
        invalidate_cache(
            CacheConfig.make_key(
                CacheConfig.PREFIX_NOTIFICATION, user_id, "unread_count"
            )
        )

    # ========== 通知偏好管理 ==========

    def create_preference(
        self, preference_data: NotificationPreferenceCreate
    ) -> NotificationPreference:
        """创建通知偏好设置"""
        preference = NotificationPreference(**preference_data.dict())
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)

        # 清除缓存
        invalidate_cache(
            CacheConfig.make_key(
                CacheConfig.PREFIX_NOTIFICATION_PREFS, preference.user_id
            )
        )

        return preference

    def update_preference(
        self, user_id: str, update_data: NotificationPreferenceUpdate
    ) -> Optional[NotificationPreference]:
        """更新通知偏好设置"""
        preference = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )
        if not preference:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preference, field, value)

        self.db.commit()
        self.db.refresh(preference)

        # 清除缓存
        invalidate_cache(
            CacheConfig.make_key(CacheConfig.PREFIX_NOTIFICATION_PREFS, user_id)
        )

        return preference

    def get_preference(self, user_id: str) -> Optional[NotificationPreference]:
        """获取通知偏好设置"""
        return (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

    # ========== 通知模板管理 ==========

    def create_template(
        self, template_data: NotificationTemplateCreate
    ) -> Dict[str, Any]:
        """创建通知模板"""
        return self._template_service.create_template(template_data)

    def get_template(self, template_code: str) -> Optional[Dict[str, Any]]:
        """获取通知模板"""
        return self._template_service.get_template(template_code)

    def update_template(
        self, template_code: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新通知模板"""
        return self._template_service.update_template(template_code, update_data)

    def delete_template(self, template_code: str) -> bool:
        """删除通知模板"""
        return self._template_service.delete_template(template_code)

    def list_templates(
        self,
        notification_type: Optional[str] = None,
        channel: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """列出通知模板"""
        return self._template_service.list_templates(
            notification_type, channel, is_active
        )

    def render_template(
        self, template_code: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """渲染通知模板"""
        return self._template_service.render_template(template_code, data)

    # ========== 通知统计 ==========

    def get_statistics(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> NotificationStatistics:
        """获取通知统计数据"""
        return self._stats_service.get_statistics(
            self.db, user_id, start_date, end_date
        )

    def get_daily_statistics(self, user_id: str, days: int = 7) -> List[Dict[str, any]]:
        """获取每日通知统计"""
        return self._stats_service.get_daily_statistics(self.db, user_id, days)

    def get_channel_statistics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Dict[str, int]]:
        """获取各渠道通知统计"""
        return self._stats_service.get_channel_statistics(
            self.db, user_id, start_date, end_date
        )

    # ========== 熔断器管理 ==========

    def get_circuit_breaker_state(self, channel: str) -> Dict[str, any]:
        """获取熔断器状态"""
        return self._circuit_breaker.get_state(channel)

    def reset_circuit_breaker(self, channel: Optional[str] = None):
        """重置熔断器"""
        self._circuit_breaker.reset(channel)

    # ========== 私有方法 ==========

    def _create_default_preference(self, user_id: str) -> NotificationPreference:
        """创建默认通知偏好设置"""
        preference = NotificationPreference(user_id=user_id)
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference

    @staticmethod
    def _is_notification_type_enabled(
        preference: NotificationPreference, notification_type: NotificationTypeEnum
    ) -> bool:
        """检查通知类型是否启用"""
        type_field_map = {
            "checkin": "checkin_enabled",
            "alert": "alert_enabled",
            "sos": "sos_enabled",
            "system": "system_enabled",
            "health": "health_enabled",
            "device": "device_enabled",
            "reminder": "reminder_enabled",
        }
        field_name = type_field_map.get(str(notification_type))
        if field_name:
            return getattr(preference, field_name, True)
        return True

    @staticmethod
    def _is_mute_enabled(preference: NotificationPreference) -> bool:
        """检查是否启用免打扰"""
        if not preference.mute_enabled:
            return False

        # 检查当前时间是否在免打扰时段
        from datetime import datetime

        now = datetime.utcnow()
        current_time = now.hour * 60 + now.minute
        mute_start = preference.mute_start_hour * 60 + preference.mute_start_minute
        mute_end = preference.mute_end_hour * 60 + preference.mute_end_minute

        if mute_start <= mute_end:
            return mute_start <= current_time <= mute_end
        else:
            # 跨天的情况，如 22:00 - 08:00
            return current_time >= mute_start or current_time <= mute_end

    @staticmethod
    def _select_channel(
        preference: NotificationPreference,
        notification_type: NotificationTypeEnum,
        priority: NotificationPriority,
    ) -> str:
        """根据偏好和优先级选择渠道"""
        # 紧急优先级使用所有可用渠道
        if priority == NotificationPriority.URGENT:
            return NotificationChannelEnum.PUSH.value

        # 根据偏好选择
        if preference.push_enabled:
            return NotificationChannelEnum.PUSH.value
        elif preference.sms_enabled:
            return NotificationChannelEnum.SMS.value
        elif preference.email_enabled:
            return NotificationChannelEnum.EMAIL.value

        # 默认使用推送
        return NotificationChannelEnum.PUSH.value

    @staticmethod
    def _select_contact_channel(contact: EmergencyContact) -> str:
        """为紧急联系人选择渠道"""
        if contact.phone:
            return NotificationChannelEnum.SMS.value
        elif contact.email:
            return NotificationChannelEnum.EMAIL.value
        return NotificationChannelEnum.PUSH.value
