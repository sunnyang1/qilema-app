"""
预警SQLAlchemy模型 (SQLAlchemy 2.x)
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class Alert(Base, BaseModelMixin):
    """预警模型 (SQLAlchemy 2.x)"""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    alert_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="预警类型",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        comment="严重程度",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="状态",
    )
    trigger_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="触发时间"
    )
    trigger_reason: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="触发原因"
    )
    last_checkin_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后签到时间"
    )
    abnormal_data: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="异常数据"
    )
    notification_sent: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="已发送的通知"
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="解决时间"
    )
    resolved_reason: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="解决原因"
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, comment="解决人"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="创建时间",
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="alerts")


class AlertSetting(Base, BaseModelMixin):
    """预警设置模型 (SQLAlchemy 2.x)"""

    __tablename__ = "alert_settings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True, unique=True
    )

    # 未签到预警设置
    checkin_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="启用未签到预警"
    )
    checkin_threshold_hours: Mapped[int] = mapped_column(
        Integer, default=24, comment="未签到阈值(小时)"
    )

    # 生理异常预警设置
    abnormal_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="启用生理异常预警"
    )
    heart_rate_min: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="心率最小值"
    )
    heart_rate_max: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="心率最大值"
    )
    blood_pressure_systolic_min: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="收缩压最小值"
    )
    blood_pressure_systolic_max: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="收缩压最大值"
    )
    blood_pressure_diastolic_min: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="舒张压最小值"
    )
    blood_pressure_diastolic_max: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="舒张压最大值"
    )
    blood_oxygen_min: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="血氧最小值"
    )

    # 通知设置
    enable_notification: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="启用通知"
    )
    notification_channels: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True, comment="通知渠道"
    )
    emergency_contact_notify: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="通知紧急联系人"
    )
    auto_resolve: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="自动解决"
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
    user: Mapped["User"] = relationship("User", back_populates="alert_settings")
