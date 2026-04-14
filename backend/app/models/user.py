"""
用户模型 (SQLAlchemy 2.x 风格)
"""

import enum
import re
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func

from app.models.base_mixin import BaseModelMixin

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

    # 数据库索引优化
    __table_args__ = (
        Index("idx_users_phone_created", "phone", "created_at"),
        Index("idx_users_last_sign_in", "last_sign_in"),
    )

    # 预定义关联关系名称列表，避免运行时 inspect 开销
    _RELATIONSHIP_NAMES = frozenset(
        [
            "emergency_contacts",
            "checkins",
            "alerts",
            "alert_settings",
            "sos_requests",
            "devices",
            "login_records",
            "user_setting",
            "emergency_calls",
            "notifications",
            "notification_preferences",
            "anomalies",
            "health_trends",
            "activity_patterns",
            "health_record",
            "medication_reminder_items",
            "medication_reminder_schedules",
            "medication_reminder_notifications",
            "medication_reminder_logs",
        ]
    )

    # 需要手动清理的大数据量关系（lazy='dynamic' 不使用 cascade）
    _DYNAMIC_RELATIONS = frozenset(
        [
            "notifications",
            "medication_reminder_notifications",
            "medication_reminder_logs",
        ]
    )

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
    # 中频/小数据量 - lazy='select' (default)
    emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(
        "EmergencyContact", back_populates="user", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="user", cascade="all, delete-orphan"
    )
    sos_requests: Mapped[List["SOSRequest"]] = relationship(
        "SOSRequest", back_populates="user", cascade="all, delete-orphan"
    )
    devices: Mapped[List["Device"]] = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    emergency_calls: Mapped[List["EmergencyCall"]] = relationship(
        "EmergencyCall", back_populates="user", cascade="all, delete-orphan"
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
    medication_reminder_items: Mapped[List["MedicationReminderItem"]] = relationship(
        "MedicationReminderItem", back_populates="user", cascade="all, delete-orphan"
    )
    medication_reminder_schedules: Mapped[
        List["MedicationReminderSchedule"]
    ] = relationship(
        "MedicationReminderSchedule",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # 一对一/总是需要 - lazy='joined'
    alert_settings: Mapped[Optional["AlertSetting"]] = relationship(
        "AlertSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
    )
    user_setting: Mapped[Optional["UserSetting"]] = relationship(
        "UserSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
    )
    notification_preferences: Mapped[Optional["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
    )
    health_record: Mapped[Optional["HealthRecord"]] = relationship(
        "HealthRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
    )

    # 高频/大数据量 - 使用 lazy='select' + cascade 确保级联删除正常工作
    # Note: SQLAlchemy 2.x 中 lazy='dynamic' 与 cascade='delete-orphan' 组合有兼容性问题
    checkins: Mapped[List["CheckIn"]] = relationship(
        "CheckIn", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    login_records: Mapped[List["LoginRecord"]] = relationship(
        "LoginRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    # 大数据量表 notifications - 使用 passive_deletes 避免级联删除问题
    # 删除用户时需要在应用层手动清理或归档
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="dynamic"
    )
    medication_reminder_notifications: Mapped[
        List["MedicationReminderNotification"]
    ] = relationship(
        "MedicationReminderNotification",
        back_populates="user",
        lazy="dynamic",
    )
    medication_reminder_logs: Mapped[List["MedicationReminderLog"]] = relationship(
        "MedicationReminderLog", back_populates="user", lazy="dynamic"
    )

    @validates("phone")
    def validate_phone(self, key: str, phone: str) -> str:
        """验证手机号格式（中国大陆手机号：11位，1开头，第二位3-9）"""
        if not phone:
            raise ValueError("手机号不能为空")
        if not re.match(r"^1[3-9]\d{9}$", phone):
            raise ValueError(f"无效的手机号格式: {phone}")
        return phone

    @validates("nickname")
    def validate_nickname(self, key: str, nickname: Optional[str]) -> Optional[str]:
        """验证昵称长度"""
        if nickname and len(nickname) > 50:
            raise ValueError("昵称长度不能超过50个字符")
        return nickname

    @validates("height")
    def validate_height(self, key: str, height: Optional[int]) -> Optional[int]:
        """验证身高范围"""
        if height is not None:
            if height < 50 or height > 300:
                raise ValueError("身高必须在50-300cm之间")
        return height

    @validates("weight")
    def validate_weight(self, key: str, weight: Optional[int]) -> Optional[int]:
        """验证体重范围"""
        if weight is not None:
            if weight < 20 or weight > 500:
                raise ValueError("体重必须在20-500kg之间")
        return weight

    def cleanup_dynamic_relations(self, db_session) -> None:
        """
        清理大数据量关系（用于删除用户前手动清理 lazy='dynamic' 关系）

        Args:
            db_session: SQLAlchemy 数据库会话
        """
        # 清理通知记录
        if hasattr(self, "notifications") and self.notifications:
            for notification in self.notifications:
                db_session.delete(notification)

        # 清理用药提醒通知
        if (
            hasattr(self, "medication_reminder_notifications")
            and self.medication_reminder_notifications
        ):
            for item in self.medication_reminder_notifications:
                db_session.delete(item)

        # 清理用药记录日志
        if hasattr(self, "medication_reminder_logs") and self.medication_reminder_logs:
            for log in self.medication_reminder_logs:
                db_session.delete(log)

    def to_dict(
        self,
        exclude: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        include_relations: Optional[List[str]] = None,
    ) -> dict:
        """
        将用户模型转换为字典

        自动排除敏感字段password_hash和所有关联关系字段，除非显式包含

        Args:
            exclude: 额外排除的字段列表
            include: 强制包含的字段列表（覆盖默认排除）
            include_relations: 要包含的关联关系名称列表（用于序列化特定关系）

        Returns:
            dict: 用户数据字典
        """
        # 基础排除列表
        default_exclude = ["password_hash"]

        # 处理 include_relations：从排除列表中移除指定的关联关系
        relations_to_exclude = set(self._RELATIONSHIP_NAMES)
        if include_relations:
            relations_to_exclude -= set(include_relations)

        default_exclude.extend(relations_to_exclude)

        if exclude:
            exclude = list(set(default_exclude + exclude))
        else:
            exclude = default_exclude

        # 处理 include：如果指定了 include，确保这些字段不被排除
        if include:
            exclude = [e for e in exclude if e not in include]

        return super().to_dict(exclude=exclude, include=include)
