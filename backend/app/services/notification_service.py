"""
消息通知服务

实现APP推送通知、短信通知、电话通知等核心功能
继承BaseService获得统一的CRUD和缓存能力
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import logging

from app.models.notification_model import Notification, NotificationPreference
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationQuery, NotificationStatistics as NotificationStatisticsSchema,
    SendNotificationRequest, BatchSendNotificationRequest, MarkAsReadRequest,
    NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPriority, NotificationChannelEnum, NotificationStatusEnum, NotificationTypeEnum
)
from app.core.notification_simulators import (
    NotificationServiceConfig,
    create_push_simulator,
    create_sms_simulator,
    create_phone_simulator,
    create_email_simulator
)
from app.services.base_service import BaseService
from app.core.cache_config import CacheConfig
from app.core.cache import cache_result, invalidate_cache

logger = logging.getLogger(__name__)


class NotificationService(BaseService[Notification]):
    """消息通知服务
    
    继承BaseService获得统一的CRUD和缓存能力
    """
    
    # 基类配置
    model_class = Notification
    cache_prefix = CacheConfig.PREFIX_NOTIFICATION
    cache_ttl = CacheConfig.TTL_NOTIFICATION_LIST

    def __init__(self, config: Optional[NotificationServiceConfig] = None):
        """
        初始化通知服务

        Args:
            config: 通知服务配置对象，如果为None则使用默认配置
        """
        # 初始化配置
        self.config = config or NotificationServiceConfig()

        # 初始化通知模拟器
        self.push_simulator = create_push_simulator(self.config)
        self.sms_simulator = create_sms_simulator(self.config)
        self.phone_simulator = create_phone_simulator(self.config)
        self.email_simulator = create_email_simulator(self.config)

        # 保留旧配置字段以保持向后兼容
        self.push_service_config = {
            "enabled": self.push_simulator.enabled,
            "app_key": "",
            "master_secret": ""
        }

        self.sms_service_config = {
            "enabled": self.sms_simulator.enabled,
            "access_key": "",
            "access_secret": "",
            "sign_name": "",
            "template_code": ""
        }
    
    # ========== 通知发送核心逻辑 ==========
    
    def send_notification(
        self,
        db: Session,
        request: SendNotificationRequest,
        recipient_type: Optional[str] = None,
        recipient_id: Optional[str] = None
    ) -> Optional[Notification]:
        """
        发送通知

        根据通知偏好设置,选择合适的通知渠道发送通知
        """
        preference = self._get_or_create_preference(db, request.user_id)

        if not self._is_notification_enabled(preference, request):
            return None

        channel = self._select_notification_channel(preference, request)
        if not channel:
            logger.error(f"无法为用户 {request.user_id} 选择通知渠道")
            return None

        notification = self._create_and_send_notification(db, request, channel, recipient_type, recipient_id)
        return notification

    def _get_or_create_preference(self, db: Session, user_id: str) -> NotificationPreference:
        """获取或创建用户通知偏好设置"""
        preference = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()

        if not preference:
            preference = self._create_default_preference(db, user_id)

        return preference

    def _is_notification_enabled(
        self,
        preference: NotificationPreference,
        request: SendNotificationRequest
    ) -> bool:
        """检查通知是否应该发送"""
        if not self._is_notification_type_enabled(preference, request.notification_type):
            logger.info(f"用户 {request.user_id} 的 {request.notification_type} 通知已禁用")
            return False

        if not self._should_send_during_mute(preference, request):
            logger.info(f"用户 {request.user_id} 当前处于免打扰时段")
            return False

        return True

    def _should_send_during_mute(
        self,
        preference: NotificationPreference,
        request: SendNotificationRequest
    ) -> bool:
        """判断免打扰时段是否应该发送通知"""
        if not self._is_mute_enabled(preference):
            return True

        # 紧急通知不受免打扰限制
        return request.priority == NotificationPriority.URGENT

    def _select_notification_channel(
        self,
        preference: NotificationPreference,
        request: SendNotificationRequest
    ) -> Optional[str]:
        """选择通知渠道"""
        return request.channel or self._select_channel(preference, request.notification_type, request.priority)

    def _create_and_send_notification(
        self,
        db: Session,
        request: SendNotificationRequest,
        channel: str,
        recipient_type: Optional[str],
        recipient_id: Optional[str]
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
            status=NotificationStatusEnum.PENDING
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        self._send_notification_by_channel(notification, channel)

        return notification

    def _send_notification_by_channel(self, notification: Notification, channel: str):
        """根据渠道发送通知（支持降级策略）"""
        # 如果启用了降级策略，使用降级逻辑发送
        if self.config.is_degradation_enabled():
            self._send_notification_with_degradation(notification, channel)
        else:
            # 不启用降级策略，直接发送
            self._send_notification_directly(notification, channel)

    def _send_notification_with_degradation(self, notification: Notification, initial_channel: str):
        """
        使用降级策略发送通知

        Args:
            notification: 通知对象
            initial_channel: 初始通知渠道
        """
        # 获取渠道优先级
        channel_priority = self.config.get_channel_priority()
        # 将channel转换为字符串（枚举值）
        initial_channel_str = str(initial_channel)

        # 首先尝试初始渠道
        try:
            result = self._try_send_by_channel(notification, initial_channel_str)
            if result["success"]:
                # 发送成功
                self._mark_notification_sent(notification)
                logger.info(f"通知发送成功（使用渠道: {initial_channel_str}）: {notification.title}")
                return
            # 初始渠道失败，记录日志
            logger.warning(f"初始渠道发送失败（渠道: {initial_channel_str}）: {result['error']}")
        except Exception as e:
            logger.error(f"初始渠道发送异常（渠道: {initial_channel_str}）: {str(e)}")

        # 初始渠道失败，按照优先级尝试其他渠道
        for channel in channel_priority:
            # 跳过已尝试的初始渠道
            if channel == initial_channel_str:
                continue

            # 记录降级日志
            logger.info(f"通知降级：尝试渠道 {channel}")

            try:
                # 尝试通过当前渠道发送
                result = self._try_send_by_channel(notification, channel)

                if result["success"]:
                    # 发送成功，更新通知渠道为实际使用的渠道
                    notification.channel = NotificationChannelEnum(channel)
                    self._mark_notification_sent(notification)
                    logger.info(f"通知发送成功（使用渠道: {channel}）: {notification.title}")
                    return
                else:
                    # 发送失败，继续尝试下一个渠道
                    logger.warning(f"通知发送失败（渠道: {channel}）: {result['error']}")
                    continue

            except Exception as e:
                # 发送异常，继续尝试下一个渠道
                logger.error(f"通知发送异常（渠道: {channel}）: {str(e)}")
                continue

        # 所有渠道都失败了
        self._mark_notification_failed(notification, "所有通知渠道都发送失败")

    def _send_notification_directly(self, notification: Notification, channel: str):
        """
        直接发送通知（不使用降级策略）

        Args:
            notification: 通知对象
            channel: 通知渠道
        """
        try:
            self._try_send_by_channel(notification, channel)
            self._mark_notification_sent(notification)
        except Exception as e:
            self._mark_notification_failed(notification, str(e))

    def _try_send_by_channel(self, notification: Notification, channel: str) -> Dict[str, Any]:
        """
        尝试通过指定渠道发送通知

        Args:
            notification: 通知对象
            channel: 通知渠道

        Returns:
            dict: 包含success和error字段的结果字典
        """
        try:
            if channel == NotificationChannelEnum.PUSH.value:
                self._send_push_notification(notification)
            elif channel == NotificationChannelEnum.SMS.value:
                self._send_sms_notification(notification)
            elif channel == NotificationChannelEnum.PHONE.value:
                self._send_phone_notification(notification)
            elif channel == NotificationChannelEnum.EMAIL.value:
                self._send_email_notification(notification)
            else:
                raise ValueError(f"不支持的通知渠道: {channel}")

            return {"success": True, "error": None}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _mark_notification_sent(self, notification: Notification):
        """标记通知为已发送"""
        notification.status = NotificationStatusEnum.SENT
        notification.sent_at = datetime.utcnow()
        db = notification._sa_instance_state.session
        db.commit()

    def _mark_notification_failed(self, notification: Notification, error_message: str):
        """标记通知发送失败"""
        logger.error(f"发送通知失败: {error_message}")
        notification.status = NotificationStatusEnum.FAILED
        notification.error_message = error_message
        notification.retry_count += 1
        db = notification._sa_instance_state.session
        db.commit()
    
    def batch_send_notification(
        self,
        db: Session,
        request: BatchSendNotificationRequest
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
                data=request.data
            )
            
            notification = self.send_notification(db, send_request)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def send_to_emergency_contacts(
        self,
        db: Session,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.HIGH,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """
        向紧急联系人发送通知
        
        用于签到、预警、SOS等场景
        """
        # 查询紧急联系人
        emergency_contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id,
            EmergencyContact.is_active == True
        ).all()
        
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
                related_id=contact.id
            )
            
            notification = self.send_notification(db, send_request, recipient_type="emergency_contact", recipient_id=str(contact.id))
            if notification:
                notifications.append(notification)
        
        return notifications
    
    # ========== 通知记录管理 ==========
    
    @classmethod
    def get_notifications(cls, db: Session, query_params: NotificationQuery) -> List[Notification]:
        """查询通知记录（带缓存）"""
        # 构建缓存键
        cache_key = CacheConfig.make_key(
            CacheConfig.PREFIX_NOTIFICATION_LIST,
            query_params.user_id,
            query_params.notification_type or "all",
            query_params.status or "all",
            query_params.offset,
            query_params.limit
        )
        
        # 尝试从缓存获取
        cached = cache_result(cache_key, None, ttl=CacheConfig.TTL_NOTIFICATION_LIST)
        # 注意：这里简化处理，实际应该使用get_cached获取
        
        query = db.query(Notification).filter(Notification.user_id == query_params.user_id)
        
        if query_params.notification_type:
            query = query.filter(Notification.notification_type == query_params.notification_type)
        
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
        
        return query.order_by(desc(Notification.created_at)).offset(query_params.offset).limit(query_params.limit).all()
    
    @classmethod
    def mark_as_read(cls, db: Session, notification_ids: List[int]) -> int:
        """标记通知为已读"""
        notifications = db.query(Notification).filter(Notification.id.in_(notification_ids)).all()
        
        count = 0
        user_ids = set()
        for notification in notifications:
            if notification.read_at is None:
                notification.read_at = datetime.utcnow()
                notification.status = NotificationStatusEnum.READ
                count += 1
                user_ids.add(notification.user_id)
        
        db.commit()
        
        # 清除相关缓存
        for user_id in user_ids:
            cls._invalidate_user_notification_cache(user_id)
        
        return count
    
    @classmethod
    def get_unread_count(cls, db: Session, user_id: str) -> int:
        """获取未读通知数量（带缓存）"""
        cache_key = CacheConfig.make_key(
            CacheConfig.PREFIX_NOTIFICATION,
            user_id,
            "unread_count"
        )
        
        # 这里简化处理，实际应该使用缓存装饰器
        count = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ).scalar()
        
        return count or 0
    
    @classmethod
    def _invalidate_user_notification_cache(cls, user_id: str):
        """清除用户通知相关缓存"""
        invalidate_cache(CacheConfig.make_pattern(CacheConfig.PREFIX_NOTIFICATION_LIST, user_id))
        invalidate_cache(CacheConfig.make_key(CacheConfig.PREFIX_NOTIFICATION, user_id, "unread_count"))
    
    # ========== 通知偏好管理 ==========
    
    @classmethod
    def create_preference(cls, db: Session, preference_data: NotificationPreferenceCreate) -> NotificationPreference:
        """创建通知偏好设置"""
        preference = NotificationPreference(**preference_data.dict())
        db.add(preference)
        db.commit()
        db.refresh(preference)
        
        # 清除缓存
        invalidate_cache(CacheConfig.make_key(CacheConfig.PREFIX_NOTIFICATION_PREFS, preference.user_id))
        
        return preference
    
    @classmethod
    def update_preference(cls, db: Session, user_id: str, update_data: NotificationPreferenceUpdate) -> Optional[NotificationPreference]:
        """更新通知偏好设置"""
        preference = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not preference:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preference, field, value)
        
        db.commit()
        db.refresh(preference)
        
        # 清除缓存
        invalidate_cache(CacheConfig.make_key(CacheConfig.PREFIX_NOTIFICATION_PREFS, user_id))
        
        return preference
    
    @classmethod
    def get_preference(cls, db: Session, user_id: str) -> Optional[NotificationPreference]:
        """获取通知偏好设置（带缓存）"""
        cache_key = CacheConfig.make_key(CacheConfig.PREFIX_NOTIFICATION_PREFS, user_id)
        
        # 这里简化处理，实际应该使用缓存装饰器
        return db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    
    # ========== 通知模板管理 ==========
    
    @classmethod
    def create_template(cls, db: Session, template_data: NotificationTemplateCreate) -> Dict[str, Any]:
        """创建通知模板（暂存内存中，待NotificationTemplate模型实现后迁移到数据库）"""
        # TODO: 待NotificationTemplate模型实现后，迁移到数据库
        logger.info(f"创建通知模板: {template_data.template_code}")
        return {
            "id": 1,
            "template_code": template_data.template_code,
            "template_name": template_data.template_name,
            "notification_type": template_data.notification_type,
            "channel": template_data.channel,
            "title_template": template_data.title_template,
            "content_template": template_data.content_template,
            "data_schema": template_data.data_schema,
            "priority": template_data.priority,
            "is_active": True
        }
    
    @classmethod
    def get_template(cls, db: Session, template_code: str) -> Optional[Dict[str, Any]]:
        """获取通知模板（暂存内存中，待NotificationTemplate模型实现后迁移到数据库）"""
        # TODO: 待NotificationTemplate模型实现后，从数据库查询
        logger.info(f"获取通知模板: {template_code}")
        return None
    
    def render_template(self, template: NotificationTemplate, data: Dict[str, Any]) -> Dict[str, str]:
        """渲染通知模板"""
        title = template.title_template
        content = template.content_template
        
        # 简单的模板渲染(实际可以使用更强大的模板引擎如Jinja2)
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            title = title.replace(placeholder, str(value))
            content = content.replace(placeholder, str(value))
        
        return {"title": title, "content": content}
    
    # ========== 通知统计 ==========
    
    @classmethod
    def get_statistics(cls, db: Session, user_id: str, start_date: datetime, end_date: datetime) -> NotificationStatisticsSchema:
        """获取通知统计数据"""
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_date,
            Notification.created_at <= end_date
        ).all()
        
        # 统计总数
        total_sent = len([n for n in notifications if n.status == NotificationStatusEnum.SENT])
        total_delivered = len([n for n in notifications if n.status == NotificationStatusEnum.DELIVERED])
        total_read = len([n for n in notifications if n.read_at is not None])
        total_failed = len([n for n in notifications if n.status == NotificationStatusEnum.FAILED])
        
        # 按类型统计
        checkin_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.CHECKIN])
        alert_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.ALERT])
        sos_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.SOS])
        system_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.SYSTEM])
        health_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.HEALTH])
        device_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.DEVICE])
        reminder_count = len([n for n in notifications if n.notification_type == NotificationTypeEnum.REMINDER])
        
        # 未读数量
        unread_count = len([n for n in notifications if n.read_at is None])
        
        return NotificationStatisticsSchema(
            user_id=user_id,
            stat_date=start_date.strftime("%Y-%m-%d"),
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_read=total_read,
            total_failed=total_failed,
            unread_count=unread_count,
            checkin_count=checkin_count,
            alert_count=alert_count,
            sos_count=sos_count,
            system_count=system_count,
            health_count=health_count,
            device_count=device_count,
            reminder_count=reminder_count
        )
    
    # ========== 私有方法 ==========
    
    def _create_default_preference(self, db: Session, user_id: str) -> NotificationPreference:
        """创建默认通知偏好设置"""
        preference = NotificationPreference(user_id=user_id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference
    
    @staticmethod
    def _is_notification_type_enabled(preference: NotificationPreference, notification_type: NotificationTypeEnum) -> bool:
        """检查通知类型是否启用"""
        # 从偏好设置中查找对应的启用字段
        type_field_map = {
            "checkin": "checkin_enabled",
            "alert": "alert_enabled", 
            "sos": "sos_enabled",
            "system": "system_enabled",
            "health": "health_enabled",
            "device": "device_enabled",
            "reminder": "reminder_enabled"
        }
        
        type_str = notification_type.value if hasattr(notification_type, 'value') else str(notification_type)
        field_name = type_field_map.get(type_str)
        
        if field_name and hasattr(preference, field_name):
            return getattr(preference, field_name)
        return True
    
    @staticmethod
    def _is_mute_enabled(preference: NotificationPreference) -> bool:
        """检查是否处于免打扰时段"""
        if not hasattr(preference, 'mute_enabled') or not preference.mute_enabled:
            return False
        
        if not hasattr(preference, 'mute_start_time') or not hasattr(preference, 'mute_end_time'):
            return False
            
        if not preference.mute_start_time or not preference.mute_end_time:
            return False
        
        current_time = datetime.now().strftime("%H:%M")
        start_time = preference.mute_start_time
        end_time = preference.mute_end_time
        
        # 判断当前时间是否在免打扰时段内
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # 跨天情况
            return current_time >= start_time or current_time <= end_time
    
    @staticmethod
    def _select_channel(
        preference: NotificationPreference,
        notification_type: NotificationTypeEnum,
        priority: NotificationPriority
    ) -> Optional[NotificationChannelEnum]:
        """选择通知渠道"""
        # 根据优先级和用户偏好选择渠道
        if priority == NotificationPriority.URGENT or str(priority) == "urgent":
            # 紧急通知: 优先电话通知,然后短信
            if hasattr(preference, 'phone_enabled') and preference.phone_enabled:
                return NotificationChannelEnum.PHONE
            elif hasattr(preference, 'sms_enabled') and preference.sms_enabled:
                return NotificationChannelEnum.SMS
            elif hasattr(preference, 'push_enabled') and preference.push_enabled:
                return NotificationChannelEnum.PUSH
        elif priority == NotificationPriority.HIGH or str(priority) == "high":
            # 高优先级: 优先短信,然后推送
            if hasattr(preference, 'sms_enabled') and preference.sms_enabled:
                return NotificationChannelEnum.SMS
            elif hasattr(preference, 'push_enabled') and preference.push_enabled:
                return NotificationChannelEnum.PUSH
        else:
            # 普通/低优先级: 优先推送
            if hasattr(preference, 'push_enabled') and preference.push_enabled:
                return NotificationChannelEnum.PUSH
        
        return None
    
    @staticmethod
    def _select_contact_channel(contact: EmergencyContact) -> NotificationChannelEnum:
        """选择紧急联系人通知渠道"""
        # 根据紧急联系人的通知方式选择渠道
        if hasattr(contact, 'notification_method') and contact.notification_method == "phone":
            return NotificationChannelEnum.PHONE
        else:
            return NotificationChannelEnum.SMS
    
    def _send_push_notification(self, notification: Notification):
        """
        发送APP推送通知

        使用推送通知模拟器发送
        """
        if not self.push_simulator.enabled:
            logger.info(f"推送服务未启用,模拟发送推送通知: {notification.title}")
            return

        # 获取用户的推送token
        user = self._get_user_by_notification(notification)
        if not user:
            logger.warning(f"用户 {notification.user_id} 不存在，无法发送推送")
            return

        # 使用模拟器发送推送
        result = self.push_simulator.send(
            user_id=notification.user_id,
            title=notification.title,
            content=notification.content,
            data=notification.data
        )

        # 记录结果
        if result["status"] == "success":
            logger.info(f"推送通知发送成功: {notification.title}")
        else:
            logger.error(f"推送通知发送失败: {result.get('message')}")

    
    def _send_sms_notification(self, notification: Notification):
        """
        发送短信通知

        使用短信通知模拟器发送
        """
        if not self.sms_simulator.enabled:
            logger.info(f"短信服务未启用,模拟发送短信通知: {notification.title}")
            return

        # 获取用户的手机号
        user = self._get_user_by_notification(notification)
        if not user or not user.phone:
            logger.warning(f"用户 {notification.user_id} 没有手机号，无法发送短信")
            return

        # 使用模拟器发送短信
        result = self.sms_simulator.send(
            phone_number=user.phone,
            content=notification.content
        )

        # 记录结果
        if result["status"] == "success":
            logger.info(f"短信通知发送成功: {notification.title}")
        else:
            logger.error(f"短信通知发送失败: {result.get('message')}")

    
    def _send_phone_notification(self, notification: Notification):
        """
        发送电话通知

        使用电话通知模拟器发送
        """
        # 获取接收者手机号
        phone_number = None
        if notification.recipient_type == "emergency_contact":
            # 紧急联系人
            emergency_contact = self._get_emergency_contact(notification)
            if emergency_contact:
                phone_number = emergency_contact.phone_number
        else:
            # 用户本人
            user = self._get_user_by_notification(notification)
            if user:
                phone_number = user.phone

        if not phone_number:
            logger.warning(f"无法获取通知接收者手机号，无法发送电话通知: {notification.title}")
            return

        # 使用模拟器发送电话
        result = self.phone_simulator.call(
            phone_number=phone_number,
            content=notification.content
        )

        # 记录结果
        if result["status"] == "success":
            logger.info(f"电话通知发送成功: {notification.title}")
        else:
            logger.error(f"电话通知发送失败: {result.get('message')}")

    
    def _send_email_notification(self, notification: Notification):
        """
        发送邮件通知

        使用邮件通知模拟器发送
        """
        # 获取用户的邮箱
        user = self._get_user_by_notification(notification)
        if not user or not user.email:
            logger.warning(f"用户 {notification.user_id} 没有邮箱，无法发送邮件")
            return

        # 使用模拟器发送邮件
        result = self.email_simulator.send(
            to_email=user.email,
            subject=notification.title,
            content=notification.content
        )

        # 记录结果
        if result["status"] == "success":
            logger.info(f"邮件通知发送成功: {notification.title}")
        else:
            logger.error(f"邮件通知发送失败: {result.get('message')}")

    def _get_user_by_notification(self, notification: Notification) -> Optional[User]:
        """
        根据通知获取用户信息

        Args:
            notification: 通知对象

        Returns:
            User: 用户对象，如果不存在则返回None
        """
        from app.core.database import get_db
        db = next(get_db())
        try:
            return db.query(User).filter(User.user_id == notification.user_id).first()
        finally:
            db.close()

    def _get_emergency_contact(self, notification: Notification) -> Optional[EmergencyContact]:
        """
        根据通知获取紧急联系人信息

        Args:
            notification: 通知对象

        Returns:
            EmergencyContact: 紧急联系人对象，如果不存在则返回None
        """
        if not notification.recipient_id:
            return None

        from app.core.database import get_db
        db = next(get_db())
        try:
            return db.query(EmergencyContact).filter(
                EmergencyContact.id == notification.recipient_id
            ).first()
        finally:
            db.close()

