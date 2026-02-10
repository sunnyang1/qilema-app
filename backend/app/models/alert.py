"""
预警SQLAlchemy模型
"""
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Boolean, Float
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base
from app.models.base_mixin import BaseModelMixin


class Alert(Base, BaseModelMixin):
    """预警模型"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), unique=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, comment="预警类型: checkin_absent, physiological_abnormal, sos_missed")
    severity = Column(String(20), nullable=False, default="medium", comment="严重程度: low, medium, high, critical")
    status = Column(String(20), nullable=False, default="active", comment="状态: active, resolved, dismissed")
    trigger_time = Column(DateTime, nullable=False, comment="触发时间")
    trigger_reason = Column(String(500), nullable=True, comment="触发原因")
    last_checkin_time = Column(DateTime, nullable=True, comment="最后签到时间")
    abnormal_data = Column(JSON, nullable=True, comment="异常数据")
    notification_sent = Column(JSON, nullable=True, comment="已发送的通知")
    resolved_at = Column(DateTime, nullable=True, comment="解决时间")
    resolved_reason = Column(String(500), nullable=True, comment="解决原因")
    resolved_by = Column(String(36), nullable=True, comment="解决人")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.utcnow(), comment="创建时间")
    
    # 关系
    user = db_relationship("User", back_populates="alerts")


class AlertSetting(Base, BaseModelMixin):
    """预警设置模型"""
    __tablename__ = "alert_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True, unique=True)
    
    # 未签到预警设置
    checkin_enabled = Column(Boolean, default=True, comment="启用未签到预警")
    checkin_threshold_hours = Column(Integer, default=24, comment="未签到阈值(小时)")
    
    # 生理异常预警设置
    abnormal_enabled = Column(Boolean, default=True, comment="启用生理异常预警")
    heart_rate_min = Column(Integer, nullable=True, comment="心率最小值")
    heart_rate_max = Column(Integer, nullable=True, comment="心率最大值")
    blood_pressure_systolic_min = Column(Integer, nullable=True, comment="收缩压最小值")
    blood_pressure_systolic_max = Column(Integer, nullable=True, comment="收缩压最大值")
    blood_pressure_diastolic_min = Column(Integer, nullable=True, comment="舒张压最小值")
    blood_pressure_diastolic_max = Column(Integer, nullable=True, comment="舒张压最大值")
    blood_oxygen_min = Column(Float, nullable=True, comment="血氧最小值")
    
    # 通知设置
    enable_notification = Column(Boolean, default=True, comment="启用通知")
    notification_channels = Column(JSON, nullable=True, comment="通知渠道: push, sms, phone")
    emergency_contact_notify = Column(Boolean, default=True, comment="通知紧急联系人")
    auto_resolve = Column(Boolean, default=True, comment="自动解决")

    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")
    
    # 关系
    user = db_relationship("User", back_populates="alert_settings")
