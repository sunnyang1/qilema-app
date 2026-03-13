"""
消息通知SQLAlchemy模型
"""

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship as db_relationship


class Notification(Base, BaseModelMixin):
    """通知模型"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    notification_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="通知类型: checkin/alert/sos/system/health/device/reminder",
    )
    channel = Column(
        String(20), nullable=False, comment="通知渠道: push/sms/phone/email/wechat"
    )
    priority = Column(
        String(20),
        nullable=False,
        default="normal",
        comment="优先级: low/normal/high/urgent",
    )
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="状态: pending/sending/sent/delivered/read/failed",
    )
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, comment="通知内容")
    data = Column(JSON, nullable=True, comment="附加数据")

    # 接收者信息
    recipient_type = Column(
        String(50), nullable=True, comment="接收者类型: user/contact/emergency_center"
    )
    recipient_id = Column(String(36), nullable=True, comment="接收者ID")

    # 发送信息
    sent_at = Column(DateTime, nullable=True, comment="发送时间")
    delivered_at = Column(DateTime, nullable=True, comment="送达时间")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")

    # 关联信息
    related_type = Column(
        String(50),
        nullable=True,
        comment="关联对象类型: alert/sos_request/checkin/device",
    )
    related_id = Column(String(36), nullable=True, comment="关联对象ID")

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="notifications")


class NotificationPreference(Base, BaseModelMixin):
    """通知偏好设置模型"""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        unique=True,
        index=True,
        comment="用户ID",
    )

    # 推送通知设置
    push_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用推送通知")
    push_mute_enabled = Column(
        Boolean, nullable=False, default=False, comment="是否启用推送免打扰"
    )
    push_mute_start = Column(String(5), nullable=True, comment="免打扰开始时间 HH:MM")
    push_mute_end = Column(String(5), nullable=True, comment="免打扰结束时间 HH:MM")

    # 短信通知设置
    sms_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用短信通知")
    sms_mute_enabled = Column(
        Boolean, nullable=False, default=False, comment="是否启用短信免打扰"
    )
    sms_mute_start = Column(String(5), nullable=True, comment="免打扰开始时间 HH:MM")
    sms_mute_end = Column(String(5), nullable=True, comment="免打扰结束时间 HH:MM")

    # 电话通知设置
    phone_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用电话通知")
    phone_mute_enabled = Column(
        Boolean, nullable=False, default=False, comment="是否启用电话免打扰"
    )
    phone_mute_start = Column(String(5), nullable=True, comment="免打扰开始时间 HH:MM")
    phone_mute_end = Column(String(5), nullable=True, comment="免打扰结束时间 HH:MM")

    # 邮件通知设置
    email_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用邮件通知")
    email_mute_enabled = Column(
        Boolean, nullable=False, default=False, comment="是否启用邮件免打扰"
    )
    email_mute_start = Column(String(5), nullable=True, comment="免打扰开始时间 HH:MM")
    email_mute_end = Column(String(5), nullable=True, comment="免打扰结束时间 HH:MM")

    # 微信通知设置
    wechat_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用微信通知")
    wechat_mute_enabled = Column(
        Boolean, nullable=False, default=False, comment="是否启用微信免打扰"
    )
    wechat_mute_start = Column(String(5), nullable=True, comment="免打扰开始时间 HH:MM")
    wechat_mute_end = Column(String(5), nullable=True, comment="免打扰结束时间 HH:MM")

    # 紧急通知设置（不受免打扰限制）
    urgent_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用紧急通知")

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="notification_preferences")
