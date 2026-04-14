"""
消息通知SQLAlchemy模型 (SQLAlchemy 2.x)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base, BaseModelMixin):
    """通知模型 (SQLAlchemy 2.x)"""

    __tablename__ = "notifications"
    __table_args__ = (
        Index(
            "idx_notifications_user_created", "user_id", "created_at"
        ),  # For listing user notifications
        Index(
            "idx_notifications_user_status", "user_id", "status"
        ),  # For filtering by status
        Index(
            "idx_notifications_user_type", "user_id", "notification_type"
        ),  # For filtering by type
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="自增ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    notification_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="通知类型: checkin/alert/sos/system/health/device/reminder",
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="通知渠道: push/sms/phone/email/wechat"
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal",
        comment="优先级: low/normal/high/urgent",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="状态: pending/sending/sent/delivered/read/failed",
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="通知标题")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="通知内容")
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="附加数据")

    # 接收者信息
    recipient_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="接收者类型: user/contact/emergency_center"
    )
    recipient_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="接收者ID"
    )

    # 发送信息
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="发送时间"
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="送达时间"
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="阅读时间"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="错误信息"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="重试次数"
    )

    # 关联信息
    related_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="关联对象类型: alert/sos_request/checkin/device",
    )
    related_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="关联对象ID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="notifications")


class NotificationPreference(Base, BaseModelMixin):
    """通知偏好设置模型 (SQLAlchemy 2.x)"""

    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="自增ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        unique=True,
        index=True,
        comment="用户ID",
    )

    # 推送通知设置
    push_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用推送通知"
    )
    push_mute_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用推送免打扰"
    )
    push_mute_start: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰开始时间 HH:MM"
    )
    push_mute_end: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰结束时间 HH:MM"
    )

    # 短信通知设置
    sms_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用短信通知"
    )
    sms_mute_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用短信免打扰"
    )
    sms_mute_start: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰开始时间 HH:MM"
    )
    sms_mute_end: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰结束时间 HH:MM"
    )

    # 电话通知设置
    phone_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用电话通知"
    )
    phone_mute_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用电话免打扰"
    )
    phone_mute_start: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰开始时间 HH:MM"
    )
    phone_mute_end: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰结束时间 HH:MM"
    )

    # 邮件通知设置
    email_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用邮件通知"
    )
    email_mute_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用邮件免打扰"
    )
    email_mute_start: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰开始时间 HH:MM"
    )
    email_mute_end: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰结束时间 HH:MM"
    )

    # 微信通知设置
    wechat_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用微信通知"
    )
    wechat_mute_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否启用微信免打扰"
    )
    wechat_mute_start: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰开始时间 HH:MM"
    )
    wechat_mute_end: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, comment="免打扰结束时间 HH:MM"
    )

    # 紧急通知设置（不受免打扰限制）
    urgent_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用紧急通知"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship(
        "User", back_populates="notification_preferences"
    )
