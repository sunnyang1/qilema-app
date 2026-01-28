"""
设备SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class Device(Base):
    """设备模型"""
    __tablename__ = "devices"
    
    device_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    device_name = Column(String(50), nullable=False, comment="设备名称")
    device_type = Column(String(20), nullable=False, comment="设备类型")
    device_model = Column(String(50), nullable=True, comment="设备型号")
    firmware_version = Column(String(20), nullable=True, comment="固件版本")
    status = Column(String(20), nullable=False, default="active", comment="状态: active/inactive/offline")
    settings = Column(JSON, nullable=True, comment="设备设置")
    data = Column(JSON, nullable=True, comment="设备数据")
    last_sync_time = Column(DateTime, nullable=True, comment="最后同步时间")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")
    
    # 关系
    user = db_relationship("User", back_populates="devices")
    device_data = db_relationship("DeviceData", back_populates="device")
    device_threshold = db_relationship("DeviceThreshold", back_populates="device")
    anomalies = db_relationship("Anomaly", back_populates="device")
    health_trends = db_relationship("HealthTrend", back_populates="device")
    activity_patterns = db_relationship("ActivityPattern", back_populates="device")
