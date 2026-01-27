"""SOS求助数据模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class SOSTypeEnum(str, enum.Enum):
    """SOS类型枚举"""
    MANUAL = "manual"  # 手动触发
    AUTO = "auto"  # 自动触发(如心率骤停)
    DEVICE = "device"  # 设备触发


class SOSStatusEnum(str, enum.Enum):
    """SOS状态枚举"""
    PENDING = "pending"  # 待救援
    RESCUING = "rescuing"  # 救援中
    RESOLVED = "resolved"  # 已解除
    CANCELLED = "cancelled"  # 已取消


class SOSRequest(Base):
    """SOS求助请求模型"""
    __tablename__ = "sos_requests"
    
    id = Column(Integer, primary_key=True, index=True, comment="求助ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), index=True, nullable=False, comment="用户ID")
    
    # SOS基本信息
    sos_type = Column(SQLEnum(SOSTypeEnum), default=SOSTypeEnum.MANUAL, comment="SOS类型")
    status = Column(SQLEnum(SOSStatusEnum), default=SOSStatusEnum.PENDING, comment="求助状态")
    emergency_reason = Column(Text, nullable=True, comment="紧急原因描述")
    
    # 位置信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    address = Column(String(255), nullable=True, comment="地址描述")
    location_accuracy = Column(Float, default=0.0, comment="定位精度(米)")
    
    # 120急救对接
    call_120 = Column(Boolean, default=False, comment="是否拨打120")
    ambulance_contact = Column(String(50), nullable=True, comment="救护车联系方式")
    ambulance_eta = Column(Integer, nullable=True, comment="救护车预计到达时间(分钟)")
    
    # 时间信息
    trigger_time = Column(DateTime(timezone=True), server_default=func.now(), comment="触发时间")
    rescue_start_time = Column(DateTime(timezone=True), nullable=True, comment="救援开始时间")
    resolve_time = Column(DateTime(timezone=True), nullable=True, comment="解除/取消时间")
    location_share_end_time = Column(DateTime(timezone=True), nullable=True, comment="位置共享结束时间")
    
    # 状态变更信息
    status_change_reason = Column(String(255), nullable=True, comment="状态变更原因")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    user = db_relationship("User", back_populates="sos_requests")
    location_histories = db_relationship("SOSLocationHistory", back_populates="sos_request", cascade="all, delete-orphan")
    # emergency_calls = db_relationship("EmergencyCall", back_populates="sos_request")  # 等待 EmergencyCall 模型实现
    # anomalies = db_relationship("Anomaly", back_populates="sos_request")  # Anomaly 模型暂时未启用
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sos_type": self.sos_type.value if self.sos_type else None,
            "status": self.status.value if self.status else None,
            "emergency_reason": self.emergency_reason,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "location_accuracy": self.location_accuracy,
            "call_120": self.call_120,
            "ambulance_contact": self.ambulance_contact,
            "ambulance_eta": self.ambulance_eta,
            "trigger_time": self.trigger_time.isoformat() if self.trigger_time else None,
            "rescue_start_time": self.rescue_start_time.isoformat() if self.rescue_start_time else None,
            "resolve_time": self.resolve_time.isoformat() if self.resolve_time else None,
            "location_share_end_time": self.location_share_end_time.isoformat() if self.location_share_end_time else None,
            "status_change_reason": self.status_change_reason,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class SOSLocationHistory(Base):
    """SOS位置历史记录模型"""
    __tablename__ = "sos_location_histories"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    sos_request_id = Column(Integer, ForeignKey("sos_requests.id"), index=True, nullable=False, comment="SOS请求ID")
    
    # 位置信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    address = Column(String(255), nullable=True, comment="地址描述")
    location_accuracy = Column(Float, default=0.0, comment="定位精度(米)")
    
    # 时间信息
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录时间")
    
    # 关联关系
    sos_request = db_relationship("SOSRequest", back_populates="location_histories")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "sos_request_id": self.sos_request_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "location_accuracy": self.location_accuracy,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }
