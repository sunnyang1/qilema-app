"""
用户模型（优化版本）

优化内容：
1. 关联加载策略优化（lazy='dynamic'）
2. 添加数据库索引
3. to_dict() 性能优化
"""

import enum
from typing import TYPE_CHECKING, List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.alert_setting import AlertSetting
    from app.models.anomaly import Anomaly
    from app.models.checkin import CheckIn
    from app.models.device import Device
    from app.models.emergency_call import EmergencyCall
    from app.models.emergency_contact import EmergencyContact
    from app.models.health_record import HealthRecord
    from app.models.health_trend import HealthTrend
    from app.models.login_record import LoginRecord
    from app.models.medication_log import MedicationReminderLog
    from app.models.medication_notification import MedicationReminderNotification
    from app.models.medication_schedule import MedicationReminderSchedule
    from app.models.notification import Notification
    from app.models.notification_preference import NotificationPreference
    from app.models.sos_request import SOSRequest
    from app.models.user_setting import UserSetting


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
    """
    用户模型（优化版本）

    关联加载策略：
    - lazy='dynamic': 返回 Query 对象，支持链式过滤，适用于可能大量数据的关联
    - lazy='select': 首次访问时加载（默认），适用于小数据量关联
    - lazy='joined': 立即加载，适用于总是需要一起加载的关联
    """

    __tablename__ = "users"

    # 基础字段
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

    # ========== 关联关系（按使用频率分组）==========

    # --- 高频使用（使用 lazy='dynamic'）---
    # 这些关联可能有大量数据，使用 dynamic 可以链式过滤

    checkins = db_relationship(
        "CheckIn",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        doc="签到记录（高频，数据量大）",
    )
    notifications = db_relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        doc="通知消息（高频，数据量大）",
    )
    anomalies = db_relationship(
        "Anomaly",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        doc="异常记录（高频，数据量大）",
    )
    alerts = db_relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        doc="预警记录（高频，数据量大）",
    )
    devices = db_relationship(
        "Device",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        doc="绑定设备（中频）",
    )

    # --- 中频使用（使用 lazy='select' - 默认）---
    # 这些关联数据量适中，按需加载

    emergency_contacts = db_relationship(
        "EmergencyContact",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="紧急联系人（中频，通常一起加载）",
    )
    sos_requests = db_relationship(
        "SOSRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="SOS请求（中频）",
    )
    login_records = db_relationship(
        "LoginRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="登录记录（低频）",
    )

    # --- 低频使用（使用 lazy='select'）---
    # 这些关联很少使用，避免不必要加载

    emergency_calls = db_relationship(
        "EmergencyCall",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="紧急呼叫（低频）",
    )
    health_trends = db_relationship(
        "HealthTrend",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="健康趋势（低频）",
    )
    activity_patterns = db_relationship(
        "ActivityPattern",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="活动模式（低频）",
    )
    medication_reminder_items = db_relationship(
        "MedicationReminderItem",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="用药提醒项（低频）",
    )
    medication_reminder_schedules = db_relationship(
        "MedicationReminderSchedule",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="用药提醒计划（低频）",
    )
    medication_reminder_notifications = db_relationship(
        "MedicationReminderNotification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="用药提醒通知（低频）",
    )
    medication_reminder_logs = db_relationship(
        "MedicationReminderLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="用药提醒日志（低频）",
    )

    # --- 一对一关系（使用 lazy='joined' 或 'select'）---
    # 这些是一对一关系，数据量小

    health_record = db_relationship(
        "HealthRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined",
        doc="健康档案（一对一，常一起加载）",
    )
    user_setting = db_relationship(
        "UserSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
        doc="用户设置（一对一，按需加载）",
    )
    alert_settings = db_relationship(
        "AlertSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
        doc="预警设置（一对一，按需加载）",
    )
    notification_preferences = db_relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
        doc="通知偏好（一对一，按需加载）",
    )

    # ========== 表级索引 ==========
    __table_args__ = (
        # 复合索引：常用于查询的场景
        Index(
            "idx_users_phone_created",
            "phone",
            "created_at",
            doc="手机号+创建时间复合索引（用于按时间排序的用户查询）",
        ),
        Index("idx_users_last_sign_in", "last_sign_in", doc="最后登录时间索引（用于查询活跃用户）"),
    )

    # 定义关联关系字段名列表（用于 to_dict 排除）
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

    def to_dict(
        self,
        exclude: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        include_relations: Optional[List[str]] = None,
    ) -> dict:
        """
        将用户模型转换为字典（优化版本）

        性能优化：
        - 使用预定义的关联关系列表，避免运行时 inspect
        - 支持选择性包含关联关系

        Args:
            exclude: 额外要排除的字段列表
            include: 只包含的字段列表（优先级高于 exclude）
            include_relations: 要包含的关联关系字段名列表

        Returns:
            dict: 用户数据的字典表示

        示例:
            >>> user.to_dict()
            {'user_id': 'xxx', 'phone': '13800138000', ...}

            >>> user.to_dict(include_relations=['emergency_contacts'])
            # 包含紧急联系人数据
        """
        # 基础排除字段
        base_exclude = {"password_hash"}

        # 关联关系字段处理
        if include_relations:
            # 只排除未指定的关联关系
            relations_to_exclude = self._RELATIONSHIP_NAMES - set(include_relations)
            base_exclude.update(relations_to_exclude)
        else:
            # 默认排除所有关联关系
            base_exclude.update(self._RELATIONSHIP_NAMES)

        # 合并用户指定的排除字段
        if exclude:
            base_exclude.update(exclude)

        # 调用 mixin 的 to_dict 方法
        return super().to_dict(exclude=list(base_exclude), include=include)

    def to_dict_with_relations(
        self,
        relations: List[str],
        exclude: Optional[List[str]] = None,
    ) -> dict:
        """
        转换为字典并包含指定关联关系

        Args:
            relations: 要包含的关联关系字段名列表
            exclude: 额外要排除的字段列表

        Returns:
            dict: 包含指定关联关系的字典
        """
        data = self.to_dict(exclude=exclude, include_relations=relations)

        # 加载并序列化指定的关联关系
        for relation_name in relations:
            if relation_name in self._RELATIONSHIP_NAMES:
                relation_value = getattr(self, relation_name)
                if relation_value is not None:
                    if hasattr(relation_value, "__iter__"):
                        # 一对多关系
                        data[relation_name] = [
                            item.to_dict() if hasattr(item, "to_dict") else item
                            for item in relation_value
                        ]
                    else:
                        # 一对一关系
                        data[relation_name] = (
                            relation_value.to_dict()
                            if hasattr(relation_value, "to_dict")
                            else relation_value
                        )

        return data
