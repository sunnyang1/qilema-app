"""
用户模型 (SQLAlchemy 2.x 风格)
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, inspect
from sqlalchemy.orm import Mapped, RelationshipProperty, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.alert import Alert, AlertSetting
    from app.models.anomaly import Anomaly
    from app.models.checkin import CheckIn
    from app.models.device import Device
    from app.models.emergency_contact import EmergencyContact
    from app.models.health_record import HealthRecord
    from app.models.health_trend import ActivityPattern, HealthTrend
    from app.models.login_record import LoginRecord
    from app.models.medication import (
        MedicationReminderItem,
        MedicationReminderLog,
        MedicationReminderNotification,
        MedicationReminderSchedule,
    )
    from app.models.notification_model import Notification, NotificationPreference
    from app.models.sos_request import EmergencyCall, SOSRequest
    from app.models.user_setting_model import UserSetting


class GenderEnum(str, enum.Enum):
    UNKNOWN = "0"
    MALE = "1"
    FEMALE = "2"


class BloodTypeEnum(str, enum.Enum):
    A = "A"
    B = "B"
    O = "O"  # noqa: E741
    AB = "AB"
    UNKNOWN = "UNKNOWN"


class User(Base, BaseModelMixin):
    """用户模型 (SQLAlchemy 2.x)"""

    __tablename__ = "users"

    # 主键和基本信息
    user_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, comment="用户唯一标识"
    )
    phone: Mapped[str] = mapped_column(
        String(11), unique=True, index=True, nullable=False, comment="手机号"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希值"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="昵称"
    )
    gender: Mapped[GenderEnum] = mapped_column(
        SQLEnum(GenderEnum), default=GenderEnum.UNKNOWN, comment="性别"
    )
    birth_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="出生日期"
    )
    blood_type: Mapped[BloodTypeEnum] = mapped_column(
        SQLEnum(BloodTypeEnum), default=BloodTypeEnum.UNKNOWN, comment="血型"
    )
    height: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="身高(cm)"
    )
    weight: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="体重(kg)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="注册时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    last_sign_in: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="最后登录时间"
    )

    # 关联关系 (SQLAlchemy 2.x: Mapped[List[T]] 或 Mapped[T])
    emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(
        "EmergencyContact", back_populates="user", cascade="all, delete-orphan"
    )
    checkins: Mapped[List["CheckIn"]] = relationship(
        "CheckIn", back_populates="user", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="user", cascade="all, delete-orphan"
    )
    alert_settings: Mapped[Optional["AlertSetting"]] = relationship(
        "AlertSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    sos_requests: Mapped[List["SOSRequest"]] = relationship(
        "SOSRequest", back_populates="user", cascade="all, delete-orphan"
    )
    devices: Mapped[List["Device"]] = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    login_records: Mapped[List["LoginRecord"]] = relationship(
        "LoginRecord", back_populates="user", cascade="all, delete-orphan"
    )
    user_setting: Mapped[Optional["UserSetting"]] = relationship(
        "UserSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    emergency_calls: Mapped[List["EmergencyCall"]] = relationship(
        "EmergencyCall", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    anomalies: Mapped[List["Anomaly"]] = relationship(
        "Anomaly", back_populates="user", cascade="all, delete-orphan"
    )
    health_trends: Mapped[List["HealthTrend"]] = relationship(
        "HealthTrend", back_populates="user", cascade="all, delete-orphan"
    )
    activity_patterns: Mapped[List["ActivityPattern"]] = relationship(
        "ActivityPattern", back_populates="user", cascade="all, delete-orphan"
    )
    health_record: Mapped[Optional["HealthRecord"]] = relationship(
        "HealthRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    medication_reminder_items: Mapped[List["MedicationReminderItem"]] = relationship(
        "MedicationReminderItem", back_populates="user", cascade="all, delete-orphan"
    )
    medication_reminder_schedules: Mapped[List["MedicationReminderSchedule"]] = relationship(
        "MedicationReminderSchedule",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    medication_reminder_notifications: Mapped[List["MedicationReminderNotification"]] = relationship(
        "MedicationReminderNotification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    medication_reminder_logs: Mapped[List["MedicationReminderLog"]] = relationship(
        "MedicationReminderLog", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """
        将用户模型转换为字典

        自动排除敏感字段password_hash和所有关联关系字段，除非显式包含
        """
        default_exclude = ["password_hash"]

        mapper = inspect(self.__class__)
        relationship_names = []
        for prop in mapper.attrs:
            if isinstance(prop, RelationshipProperty):
                relationship_names.append(prop.key)

        default_exclude.extend(relationship_names)

        if exclude:
            exclude = list(set(default_exclude + exclude))
        else:
            exclude = default_exclude

        return super().to_dict(exclude=exclude, include=include)
