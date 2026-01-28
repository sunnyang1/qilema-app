"""
设备数据SQLAlchemy模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship as db_relationship
from app.core.database import Base


class DeviceData(Base):
    """设备数据模型"""
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    data_id = Column(String(36), unique=True, index=True, comment="数据ID")
    device_id = Column(String(36), ForeignKey("devices.device_id"), nullable=False, index=True, comment="设备ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True, comment="用户ID")
    data_type = Column(String(50), nullable=False, comment="数据类型: heart_rate/steps/sleep/blood_pressure/blood_oxygen/temperature")
    data_value = Column(JSON, nullable=False, comment="数据值")
    upload_time = Column(DateTime, nullable=False, comment="上传时间")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")

    # 关系
    device = db_relationship("Device", back_populates="device_data")


class DeviceThreshold(Base):
    """设备阈值模型"""
    __tablename__ = "device_thresholds"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    device_id = Column(String(36), ForeignKey("devices.device_id"), nullable=False, unique=True, index=True, comment="设备ID")
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True, comment="用户ID")

    # 心率阈值
    heart_rate_min = Column(Integer, nullable=True, comment="心率最小值(bpm)")
    heart_rate_max = Column(Integer, nullable=True, comment="心率最大值(bpm)")

    # 血压阈值
    blood_pressure_systolic_min = Column(Integer, nullable=True, comment="收缩压最小值(mmHg)")
    blood_pressure_systolic_max = Column(Integer, nullable=True, comment="收缩压最大值(mmHg)")
    blood_pressure_diastolic_min = Column(Integer, nullable=True, comment="舒张压最小值(mmHg)")
    blood_pressure_diastolic_max = Column(Integer, nullable=True, comment="舒张压最大值(mmHg)")

    # 血氧阈值
    blood_oxygen_min = Column(Float, nullable=True, comment="血氧最小值(%)")

    # 体温阈值
    temperature_min = Column(Float, nullable=True, comment="体温最小值(℃)")
    temperature_max = Column(Float, nullable=True, comment="体温最大值(℃)")

    # 其他阈值
    steps_min = Column(Integer, nullable=True, comment="步数最小值")
    steps_max = Column(Integer, nullable=True, comment="步数最大值")
    sleep_duration_min = Column(Float, nullable=True, comment="睡眠时长最小值(小时)")

    enabled = Column(Integer, default=1, nullable=False, comment="是否启用: 0=禁用 1=启用")
    created_at = Column(DateTime, nullable=False, default=lambda: __import__('datetime').datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    device = db_relationship("Device", back_populates="device_threshold")
    user = db_relationship("User")
