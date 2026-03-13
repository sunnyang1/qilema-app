import enum
from typing import List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, inspect
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func

from ..core.database import Base


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
    """用户模型"""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, index=True, comment="用户唯一标识")
    phone = Column(String(11), unique=True, index=True, nullable=False, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    nickname = Column(String(50), nullable=True, comment="昵称")
    gender = Column(SQLEnum(GenderEnum), default=GenderEnum.UNKNOWN, comment="性别")
    birth_date = Column(DateTime, nullable=True, comment="出生日期")
    blood_type = Column(
        SQLEnum(BloodTypeEnum), default=BloodTypeEnum.UNKNOWN, comment="血型"
    )
    height = Column(Integer, nullable=True, comment="身高(cm)")
    weight = Column(Integer, nullable=True, comment="体重(kg)")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="注册时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    last_sign_in = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")

    # 关联关系
    emergency_contacts = db_relationship(
        "EmergencyContact", back_populates="user", cascade="all, delete-orphan"
    )
    checkins = db_relationship(
        "CheckIn", back_populates="user", cascade="all, delete-orphan"
    )
    alerts = db_relationship(
        "Alert", back_populates="user", cascade="all, delete-orphan"
    )
    alert_settings = db_relationship(
        "AlertSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    sos_requests = db_relationship(
        "SOSRequest", back_populates="user", cascade="all, delete-orphan"
    )
    devices = db_relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    login_records = db_relationship(
        "LoginRecord", back_populates="user", cascade="all, delete-orphan"
    )
    user_setting = db_relationship(
        "UserSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    emergency_calls = db_relationship(
        "EmergencyCall", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = db_relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    notification_preferences = db_relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    anomalies = db_relationship(
        "Anomaly", back_populates="user", cascade="all, delete-orphan"
    )
    health_trends = db_relationship(
        "HealthTrend", back_populates="user", cascade="all, delete-orphan"
    )
    activity_patterns = db_relationship(
        "ActivityPattern", back_populates="user", cascade="all, delete-orphan"
    )
    health_record = db_relationship(
        "HealthRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    medication_reminder_items = db_relationship(
        "MedicationReminderItem", back_populates="user", cascade="all, delete-orphan"
    )
    medication_reminder_schedules = db_relationship(
        "MedicationReminderSchedule",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    medication_reminder_notifications = db_relationship(
        "MedicationReminderNotification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    medication_reminder_logs = db_relationship(
        "MedicationReminderLog", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """
        将用户模型转换为字典

        自动排除敏感字段password_hash和所有关联关系字段，除非显式包含

        使用SQLAlchemy inspect功能自动检测关联关系，无需手动维护字段列表

        Args:
            exclude: 额外要排除的字段列表
            include: 只包含的字段列表（优先级高于exclude）

        Returns:
            dict: 用户数据的字典表示（不含敏感信息和关联关系）

        示例:
            >>> user.to_dict()
            {'user_id': 'xxx', 'phone': '13800138000', ...}

            >>> user.to_dict(exclude=['height', 'weight'])
            # 排除身高体重

            >>> user.to_dict(include=['user_id', 'nickname'])
            # 只包含指定字段
        """
        # 默认排除敏感字段
        default_exclude = ["password_hash"]

        # 自动检测所有关联关系字段
        mapper = inspect(self.__class__)
        relationship_names = []
        for prop in mapper.attrs:
            if isinstance(prop, RelationshipProperty):
                relationship_names.append(prop.key)

        # 合并敏感字段和关联关系字段
        default_exclude.extend(relationship_names)

        # 合并用户指定的排除字段
        if exclude:
            exclude = list(set(default_exclude + exclude))
        else:
            exclude = default_exclude

        # 调用mixin的to_dict方法
        return super().to_dict(exclude=exclude, include=include)
