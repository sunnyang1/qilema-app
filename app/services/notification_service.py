"""
消息通知服务

实现APP推送通知、短信通知、电话通知等核心功能
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import logging

from app.models.notification_model import Notification
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationQuery, NotificationStatistics as NotificationStatisticsSchema,
    SendNotificationRequest, BatchSendNotificationRequest, MarkAsReadRequest,
    NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    NotificationPriority
)

logger = logging.getLogger(__name__)


class NotificationService:
    """消息通知服务"""
    
    def __init__(self):
        # 推送服务配置(实际应该从配置文件读取)
        self.push_service_config = {
            "enabled": False,
            "app_key": "",
            "master_secret": ""
        }
        
        # 短信服务配置(实际应该从配置文件读取)
        self.sms_service_config = {
            "enabled": False,
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
        # 检查用户通知偏好设置
        preference = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == request.user_id
        ).first()
        
        if not preference:
            # 创建默认偏好设置
            preference = self._create_default_preference(db, request.user_id)
        
        # 检查通知类型是否启用
        if not self._is_notification_type_enabled(preference, request.notification_type):
            logger.info(f"用户 {request.user_id} 的 {request.notification_type} 通知已禁用")
            return None
        
        # 检查免打扰设置
        if self._is_mute_enabled(preference):
            logger.info(f"用户 {request.user_id} 当前处于免打扰时段")
            # 根据优先级决定是否发送
            if request.priority != NotificationPriority.URGENT:
                return None
        
        # 选择通知渠道
        channel = request.channel or self._select_channel(preference, request.notification_type, request.priority)
        
        if not channel:
            logger.error(f"无法为用户 {request.user_id} 选择通知渠道")
            return None
        
        # 创建通知记录
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
            status=NotificationStatus.PENDING
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # 发送通知
        try:
            if channel == NotificationChannel.PUSH:
                self._send_push_notification(notification)
            elif channel == NotificationChannel.SMS:
                self._send_sms_notification(notification)
            elif channel == NotificationChannel.PHONE:
                self._send_phone_notification(notification)
            elif channel == NotificationChannel.EMAIL:
                self._send_email_notification(notification)
            
            # 更新通知状态
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now()
            db.commit()
            
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.retry_count += 1
            db.commit()
        
        return notification
    
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
    
    def get_notifications(self, db: Session, query_params: NotificationQuery) -> List[Notification]:
        """查询通知记录"""
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
    
    def mark_as_read(self, db: Session, notification_ids: List[int]) -> int:
        """标记通知为已读"""
        notifications = db.query(Notification).filter(Notification.id.in_(notification_ids)).all()
        
        count = 0
        for notification in notifications:
            if notification.read_at is None:
                notification.read_at = datetime.now()
                notification.status = NotificationStatus.READ
                count += 1
        
        db.commit()
        return count
    
    def get_unread_count(self, db: Session, user_id: str) -> int:
        """获取未读通知数量"""
        count = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ).scalar()
        
        return count or 0
    
    # ========== 通知偏好管理 ==========
    
    def create_preference(self, db: Session, preference_data: NotificationPreferenceCreate) -> NotificationPreference:
        """创建通知偏好设置"""
        preference = NotificationPreference(**preference_data.dict())
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference
    
    def update_preference(self, db: Session, user_id: str, update_data: NotificationPreferenceUpdate) -> Optional[NotificationPreference]:
        """更新通知偏好设置"""
        preference = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not preference:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preference, field, value)
        
        db.commit()
        db.refresh(preference)
        return preference
    
    def get_preference(self, db: Session, user_id: str) -> Optional[NotificationPreference]:
        """获取通知偏好设置"""
        return db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
    
    # ========== 通知模板管理 ==========
    
    def create_template(self, db: Session, template_data: NotificationTemplateCreate) -> NotificationTemplate:
        """创建通知模板"""
        template = NotificationTemplate(**template_data.dict())
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    def get_template(self, db: Session, template_code: str) -> Optional[NotificationTemplate]:
        """获取通知模板"""
        return db.query(NotificationTemplate).filter(
            NotificationTemplate.template_code == template_code,
            NotificationTemplate.is_active == True
        ).first()
    
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
    
    def get_statistics(self, db: Session, user_id: str, start_date: datetime, end_date: datetime) -> NotificationStatisticsSchema:
        """获取通知统计数据"""
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_date,
            Notification.created_at <= end_date
        ).all()
        
        # 统计总数
        total_sent = len([n for n in notifications if n.status == NotificationStatus.SENT])
        total_delivered = len([n for n in notifications if n.status == NotificationStatus.DELIVERED])
        total_read = len([n for n in notifications if n.read_at is not None])
        total_failed = len([n for n in notifications if n.status == NotificationStatus.FAILED])
        
        # 按类型统计
        checkin_count = len([n for n in notifications if n.notification_type == NotificationType.CHECKIN])
        alert_count = len([n for n in notifications if n.notification_type == NotificationType.ALERT])
        sos_count = len([n for n in notifications if n.notification_type == NotificationType.SOS])
        system_count = len([n for n in notifications if n.notification_type == NotificationType.SYSTEM])
        health_count = len([n for n in notifications if n.notification_type == NotificationType.HEALTH])
        device_count = len([n for n in notifications if n.notification_type == NotificationType.DEVICE])
        reminder_count = len([n for n in notifications if n.notification_type == NotificationType.REMINDER])
        
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
    
    def _is_notification_type_enabled(self, preference: NotificationPreference, notification_type: NotificationType) -> bool:
        """检查通知类型是否启用"""
        type_mapping = {
            NotificationType.CHECKIN: preference.checkin_enabled,
            NotificationType.ALERT: preference.alert_enabled,
            NotificationType.SOS: preference.sos_enabled,
            NotificationType.SYSTEM: preference.system_enabled,
            NotificationType.HEALTH: preference.health_enabled,
            NotificationType.DEVICE: preference.device_enabled,
            NotificationType.REMINDER: preference.reminder_enabled
        }
        return type_mapping.get(notification_type, True)
    
    def _is_mute_enabled(self, preference: NotificationPreference) -> bool:
        """检查是否处于免打扰时段"""
        if not preference.mute_enabled:
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
    
    def _select_channel(
        self,
        preference: NotificationPreference,
        notification_type: NotificationType,
        priority: NotificationPriority
    ) -> Optional[NotificationChannel]:
        """选择通知渠道"""
        # 根据优先级和用户偏好选择渠道
        if priority == NotificationPriority.URGENT:
            # 紧急通知: 优先电话通知,然后短信
            if preference.phone_enabled:
                return NotificationChannel.PHONE
            elif preference.sms_enabled:
                return NotificationChannel.SMS
            elif preference.push_enabled:
                return NotificationChannel.PUSH
        elif priority == NotificationPriority.HIGH:
            # 高优先级: 优先短信,然后推送
            if preference.sms_enabled:
                return NotificationChannel.SMS
            elif preference.push_enabled:
                return NotificationChannel.PUSH
        else:
            # 普通/低优先级: 优先推送
            if preference.push_enabled:
                return NotificationChannel.PUSH
        
        return None
    
    def _select_contact_channel(self, contact: EmergencyContact) -> NotificationChannel:
        """选择紧急联系人通知渠道"""
        # 根据紧急联系人的通知方式选择渠道
        if contact.notification_method == "sms":
            return NotificationChannel.SMS
        elif contact.notification_method == "phone":
            return NotificationChannel.PHONE
        else:
            return NotificationChannel.SMS
    
    def _send_push_notification(self, notification: Notification):
        """
        发送APP推送通知
        
        实际应该调用推送服务SDK(极光推送/个推/FCM)
        """
        if not self.push_service_config["enabled"]:
            logger.info(f"推送服务未启用,模拟发送推送通知: {notification.title}")
            return
        
        # 实际推送逻辑
        # 这里应该调用极光推送/个推/FCM等推送服务的SDK
        logger.info(f"发送推送通知: {notification.title}")
    
    def _send_sms_notification(self, notification: Notification):
        """
        发送短信通知
        
        实际应该调用短信服务SDK(阿里云短信/腾讯云短信)
        """
        if not self.sms_service_config["enabled"]:
            logger.info(f"短信服务未启用,模拟发送短信通知: {notification.title}")
            return
        
        # 实际短信发送逻辑
        # 这里应该调用阿里云短信/腾讯云短信等短信服务的SDK
        logger.info(f"发送短信通知: {notification.title}")
    
    def _send_phone_notification(self, notification: Notification):
        """
        发送电话通知
        
        实际应该调用电话拨打API
        """
        logger.info(f"发送电话通知: {notification.title}")
        # 实际电话拨打逻辑
        # 这里应该调用电话拨打API
    
    def _send_email_notification(self, notification: Notification):
        """
        发送邮件通知
        
        实际应该调用邮件发送API
        """
        logger.info(f"发送邮件通知: {notification.title}")
        # 实际邮件发送逻辑
        # 这里应该调用邮件发送API
