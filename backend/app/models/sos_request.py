"""SOS求助数据模型 (SQLAlchemy 2.x)"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base_mixin import BaseModelMixin

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.anomaly import Anomaly
    from app.models.user import User


class SOSTypeEnum(str, enum.Enum):
    """SOS类型枚举"""

    MANUAL = "manual"  # 手动触发
    AUTO = "auto"  # 自动触发
    DEVICE = "device"  # 设备触发


class SOSStatusEnum(str, enum.Enum):
    """SOS状态枚举"""

    PENDING = "pending"  # 待救援
    RESCUING = "rescuing"  # 救援中
    RESOLVED = "resolved"  # 已解除
    CANCELLED = "cancelled"  # 已取消


class SOSRequest(Base, BaseModelMixin):
    """SOS求助请求模型 (SQLAlchemy 2.x)"""

    __tablename__ = "sos_requests"

    __table_args__ = (
        Index(
            "idx_sos_user_triggered", "user_id", "trigger_time"
        ),  # For user SOS history
        Index("idx_sos_status", "status"),  # For filtering by status
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="求助ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
        comment="用户ID",
    )

    # SOS基本信息
    sos_type: Mapped[SOSTypeEnum] = mapped_column(
        SQLEnum(SOSTypeEnum), default=SOSTypeEnum.MANUAL, comment="SOS类型"
    )
    status: Mapped[SOSStatusEnum] = mapped_column(
        SQLEnum(SOSStatusEnum), default=SOSStatusEnum.PENDING, comment="求助状态"
    )
    emergency_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="紧急原因描述"
    )

    # 位置信息
    latitude: Mapped[float] = mapped_column(Float, nullable=False, comment="纬度")
    longitude: Mapped[float] = mapped_column(Float, nullable=False, comment="经度")
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="地址描述"
    )
    location_accuracy: Mapped[float] = mapped_column(
        Float, default=0.0, comment="定位精度(米)"
    )

    # 120急救对接
    call_120: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否拨打120")
    ambulance_contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="救护车联系方式"
    )
    ambulance_eta: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="救护车预计到达时间(分钟)"
    )

    # 时间信息
    trigger_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="触发时间"
    )
    rescue_start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="救援开始时间"
    )
    resolve_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="解除/取消时间"
    )
    location_share_end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="位置共享结束时间"
    )

    # 状态变更信息
    status_change_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="状态变更原因"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关联关系 - SOSRequest.user is frequently accessed, use lazy='joined' for immediate loading
    user: Mapped["User"] = relationship(
        "User", back_populates="sos_requests", lazy="joined"
    )
    location_histories: Mapped[List["SOSLocationHistory"]] = relationship(
        "SOSLocationHistory", back_populates="sos_request", cascade="all, delete-orphan"
    )
    anomalies: Mapped[List["Anomaly"]] = relationship(
        "Anomaly", back_populates="sos_request"
    )


class SOSLocationHistory(Base, BaseModelMixin):
    """SOS位置历史记录模型 (SQLAlchemy 2.x)"""

    __tablename__ = "sos_location_histories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, comment="记录ID"
    )
    sos_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sos_requests.id"),
        index=True,
        nullable=False,
        comment="SOS请求ID",
    )

    # 位置信息
    latitude: Mapped[float] = mapped_column(Float, nullable=False, comment="纬度")
    longitude: Mapped[float] = mapped_column(Float, nullable=False, comment="经度")
    address: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="地址描述"
    )
    location_accuracy: Mapped[float] = mapped_column(
        Float, default=0.0, comment="定位精度(米)"
    )

    # 时间信息
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="记录时间"
    )

    # 关联关系
    sos_request: Mapped["SOSRequest"] = relationship(
        "SOSRequest", back_populates="location_histories"
    )
