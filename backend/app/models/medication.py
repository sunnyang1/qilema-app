"""
用药提醒功能模型

提供药品管理、用药计划、提醒和服药记录功能
"""

from datetime import datetime, time, date
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin


class MedicationType(str, PyEnum):
    """药品类型"""
    PRESCRIPTION = "prescription"    # 处方药
    OTC = "otc"                      # 非处方药
    SUPPLEMENT = "supplement"        # 保健品/补充剂
    HERBAL = "herbal"                # 中药/草药
    OTHER = "other"                  # 其他


class MedicationUnit(str, PyEnum):
    """剂量单位"""
    PILL = "pill"          # 片
    CAPSULE = "capsule"    # 粒/胶囊
    ML = "ml"              # 毫升
    MG = "mg"              # 毫克
    G = "g"                # 克
    IU = "iu"              # 国际单位
    DROPS = "drops"        # 滴
    PATCH = "patch"        # 贴
    SPRAY = "spray"        # 喷
    OTHER = "other"        # 其他


class ScheduleFrequency(str, PyEnum):
    """用药频率"""
    ONCE = "once"              # 一次性
    DAILY = "daily"            # 每日
    EVERY_OTHER_DAY = "every_other_day"  # 隔日
    WEEKLY = "weekly"          # 每周
    MONTHLY = "monthly"        # 每月
    AS_NEEDED = "as_needed"    # 按需/必要时
    CUSTOM = "custom"          # 自定义


class ReminderStatus(str, PyEnum):
    """提醒状态"""
    PENDING = "pending"        # 待提醒
    SENT = "sent"              # 已发送
    CONFIRMED = "confirmed"    # 已确认（用户收到）
    DISMISSED = "dismissed"    # 已忽略
    EXPIRED = "expired"        # 已过期


class LogStatus(str, PyEnum):
    """服药记录状态"""
    TAKEN = "taken"            # 已服用
    MISSED = "missed"          # 错过/未服用
    SKIPPED = "skipped"        # 主动跳过
    DELAYED = "delayed"        # 延迟服用


class MedicationReminderItem(Base, BaseModelMixin):
    """药品信息模型"""
    __tablename__ = "medication_reminder_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, index=True, comment="用户ID")
    
    # 药品基本信息
    name = Column(String(200), nullable=False, comment="药品名称")
    generic_name = Column(String(200), comment="通用名/成分名")
    brand_name = Column(String(200), comment="商品名/品牌")
    medication_type = Column(Enum(MedicationType), default=MedicationType.PRESCRIPTION,
                            comment="药品类型")
    
    # 剂量信息
    dosage = Column(Float, nullable=False, comment="单次剂量数值")
    unit = Column(Enum(MedicationUnit), nullable=False, comment="剂量单位")
    strength = Column(String(100), comment="规格（如500mg/片）")
    
    # 外观描述
    color = Column(String(50), comment="颜色")
    shape = Column(String(50), comment="形状")
    imprint = Column(String(100), comment="印记/刻字")
    
    # 其他信息
    instructions = Column(Text, comment="用药说明/注意事项")
    side_effects = Column(Text, comment="可能的副作用")
    storage = Column(String(200), comment="储存条件")
    prescription_info = Column(String(500), comment="处方信息（医生、医院等）")
    
    # 有效期和库存
    expiry_date = Column(Date, comment="有效期至")
    total_quantity = Column(Float, comment="总数量")
    remaining_quantity = Column(Float, comment="剩余数量")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="medication_reminder_items")
    schedules = relationship("MedicationReminderSchedule", back_populates="medication_item",
                            cascade="all, delete-orphan")
    logs = relationship("MedicationReminderLog", back_populates="medication_item",
                       cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicationReminderItem(id={self.id}, name={self.name})>"


class MedicationReminderSchedule(Base, BaseModelMixin):
    """用药计划模型"""
    __tablename__ = "medication_reminder_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, index=True, comment="用户ID")
    medication_item_id = Column(Integer, ForeignKey("medication_reminder_items.id", ondelete="CASCADE"),
                          nullable=False, index=True, comment="药品ID")
    
    # 计划基本信息
    name = Column(String(200), comment="计划名称（如：早餐后服用）")
    
    # 用药频率
    frequency = Column(Enum(ScheduleFrequency), nullable=False, comment="用药频率")
    
    # 用药时间（可设置多个时间点，用逗号分隔，如"08:00,12:00,18:00"）
    times_of_day = Column(String(200), nullable=False, comment="每日用药时间（HH:MM格式，逗号分隔）")
    
    # 具体日期设置
    days_of_week = Column(String(50), comment="每周哪几天（1-7，逗号分隔），空表示每天")
    specific_dates = Column(Text, comment="特定日期列表（JSON数组），用于自定义频率")
    
    # 计划周期
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, comment="结束日期（空表示长期）")
    
    # 剂量调整（如不填则使用药品默认剂量）
    custom_dosage = Column(Float, comment="自定义剂量")
    custom_unit = Column(Enum(MedicationUnit), comment="自定义单位")
    
    # 提醒设置
    reminder_enabled = Column(Boolean, default=True, comment="是否开启提醒")
    reminder_minutes_before = Column(Integer, default=0, comment="提前提醒分钟数")
    reminder_sound = Column(String(100), comment="提醒音效")
    
    # 时区
    timezone = Column(String(50), default="Asia/Shanghai", comment="时区")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_paused = Column(Boolean, default=False, comment="是否暂停")
    pause_until = Column(DateTime, comment="暂停至")
    
    # 统计
    total_doses = Column(Integer, default=0, comment="应服总次数")
    completed_doses = Column(Integer, default=0, comment="已完成次数")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="medication_reminder_schedules")
    medication_item = relationship("MedicationReminderItem", back_populates="schedules")
    reminders = relationship("MedicationReminderNotification", back_populates="schedule",
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicationReminderSchedule(id={self.id}, medication_item={self.medication_item_id})>"

    def get_times_list(self) -> List[str]:
        """获取用药时间列表"""
        if not self.times_of_day:
            return []
        return [t.strip() for t in self.times_of_day.split(",")]


class MedicationReminderNotification(Base, BaseModelMixin):
    """用药提醒记录模型"""
    __tablename__ = "medication_reminder_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, index=True, comment="用户ID")
    schedule_id = Column(Integer, ForeignKey("medication_reminder_schedules.id", ondelete="CASCADE"),
                        nullable=False, index=True, comment="用药计划ID")
    medication_item_id = Column(Integer, ForeignKey("medication_reminder_items.id", ondelete="CASCADE"),
                          nullable=False, index=True, comment="药品ID")
    
    # 提醒时间
    scheduled_time = Column(DateTime, nullable=False, comment="计划提醒时间")
    reminder_date = Column(Date, nullable=False, index=True, comment="提醒日期")
    reminder_time = Column(Time, nullable=False, comment="提醒时间")
    
    # 状态
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING, comment="提醒状态")
    
    # 发送记录
    sent_at = Column(DateTime, comment="实际发送时间")
    notification_type = Column(String(50), comment="通知类型（push/sms/phone）")
    notification_sent = Column(Boolean, default=False, comment="通知是否已发送")
    notification_error = Column(String(500), comment="通知发送错误信息")
    
    # 用户响应
    responded_at = Column(DateTime, comment="用户响应时间")
    response_action = Column(String(50), comment="用户响应动作（taken/skipped/snooze）")
    
    # 关联的服药记录
    log_id = Column(Integer, ForeignKey("medication_reminder_logs.id", ondelete="SET NULL"),
                   comment="对应的服药记录ID")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    user = relationship("User", back_populates="medication_reminder_notifications")
    schedule = relationship("MedicationReminderSchedule", back_populates="reminders")
    medication_item = relationship("MedicationReminderItem")

    def __repr__(self):
        return f"<MedicationReminderNotification(id={self.id}, status={self.status})>"


class MedicationReminderLog(Base, BaseModelMixin):
    """服药记录模型"""
    __tablename__ = "medication_reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, index=True, comment="用户ID")
    medication_item_id = Column(Integer, ForeignKey("medication_reminder_items.id", ondelete="CASCADE"),
                          nullable=False, index=True, comment="药品ID")
    schedule_id = Column(Integer, ForeignKey("medication_reminder_schedules.id", ondelete="SET NULL"),
                        comment="用药计划ID")
    reminder_id = Column(Integer, ForeignKey("medication_reminder_notifications.id", ondelete="SET NULL"),
                        comment="对应的提醒ID")
    
    # 服药信息
    scheduled_date = Column(Date, comment="计划服药日期")
    scheduled_time = Column(Time, comment="计划服药时间")
    taken_at = Column(DateTime, comment="实际服药时间")
    
    # 服药状态
    status = Column(Enum(LogStatus), nullable=False, comment="服药状态")
    
    # 剂量记录
    dosage_taken = Column(Float, comment="实际服用剂量")
    unit = Column(Enum(MedicationUnit), comment="单位")
    
    # 额外信息
    notes = Column(Text, comment="备注/感受")
    side_effects_noted = Column(Text, comment="注意到的副作用")
    skipped_reason = Column(String(200), comment="跳过原因")
    
    # 位置和设备
    location = Column(String(200), comment="服药地点")
    device_id = Column(String(36), comment="记录设备ID")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关联关系
    user = relationship("User", back_populates="medication_reminder_logs")
    medication_item = relationship("MedicationReminderItem", back_populates="logs")
    schedule = relationship("MedicationReminderSchedule")
    
    def __repr__(self):
        return f"<MedicationReminderLog(id={self.id}, status={self.status})>"
