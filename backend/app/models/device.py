"""
设备SQLAlchemy模型 (SQLAlchemy 2.x)
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class Device(Base, BaseModelMixin):
    """设备模型 (SQLAlchemy 2.x)"""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    device_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, comment="设备ID"
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    device_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="设备名称"
    )
    device_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="设备类型"
    )
    device_brand: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="设备品牌"
    )
    device_model: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="设备型号"
    )
    firmware_version: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="固件版本"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="状态: active/inactive/offline",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否激活"
    )
    is_online: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否在线"
    )
    battery_level: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="电池电量(0-100)"
    )
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="设备设置"
    )
    data: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="设备数据"
    )
    last_sync_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后同步时间"
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最后同步时间(别名)"
    )
    bound_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="绑定时间"
    )
    unbound_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="解绑时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="devices")
    device_data: Mapped[List["DeviceData"]] = relationship(
        "DeviceData", back_populates="device"
    )
    device_threshold: Mapped[Optional["DeviceThreshold"]] = relationship(
        "DeviceThreshold", back_populates="device"
    )
    anomalies: Mapped[List["Anomaly"]] = relationship(
        "Anomaly", back_populates="device"
    )
    health_trends: Mapped[List["HealthTrend"]] = relationship(
        "HealthTrend", back_populates="device"
    )
    activity_patterns: Mapped[List["ActivityPattern"]] = relationship(
        "ActivityPattern", back_populates="device"
    )
