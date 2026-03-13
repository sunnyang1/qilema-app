"""
设备数据SQLAlchemy模型
"""

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship as db_relationship


class DeviceData(Base, BaseModelMixin):
    """设备数据模型"""

    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    data_id = Column(String(36), unique=True, index=True, comment="数据ID")
    device_id = Column(
        String(36),
        ForeignKey("devices.device_id"),
        nullable=False,
        index=True,
        comment="设备ID",
    )
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    data_type = Column(
        String(50),
        nullable=False,
        comment="数据类型: heart_rate/steps/sleep/blood_pressure/blood_oxygen/temperature",
    )
    data_value = Column(JSON, nullable=False, comment="数据值")
    upload_time = Column(DateTime, nullable=False, comment="上传时间")
    data_timestamp = Column(DateTime, nullable=True, comment="数据时间戳（用于时间序列分析）")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )

    # 独立字段（用于方便查询和索引）
    # 心率相关
    heart_rate = Column(Integer, nullable=True, comment="心率(bpm)")

    # 血压相关
    systolic_pressure = Column(Integer, nullable=True, comment="收缩压(mmHg)")
    diastolic_pressure = Column(Integer, nullable=True, comment="舒张压(mmHg)")

    # 血氧相关
    blood_oxygen = Column(Float, nullable=True, comment="血氧(%)")

    # 体温相关
    body_temperature = Column(Float, nullable=True, comment="体温(℃)")

    # 运动相关
    steps = Column(Integer, nullable=True, comment="步数")
    calories = Column(Integer, nullable=True, comment="卡路里")
    distance = Column(Float, nullable=True, comment="距离")

    # 睡眠相关
    sleep_duration = Column(Float, nullable=True, comment="睡眠时长")

    # 关系
    device = db_relationship("Device", back_populates="device_data")


class DeviceThreshold(Base, BaseModelMixin):
    """设备阈值模型"""

    __tablename__ = "device_thresholds"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    device_id = Column(
        String(36),
        ForeignKey("devices.device_id"),
        nullable=False,
        unique=True,
        index=True,
        comment="设备ID",
    )
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )

    # 心率阈值
    heart_rate_min = Column(Integer, nullable=True, comment="心率最小值(bpm)")
    heart_rate_max = Column(Integer, nullable=True, comment="心率最大值(bpm)")

    # 血压阈值
    blood_pressure_systolic_min = Column(Integer, nullable=True, comment="收缩压最小值(mmHg)")
    blood_pressure_systolic_max = Column(Integer, nullable=True, comment="收缩压最大值(mmHg)")
    blood_pressure_diastolic_min = Column(
        Integer, nullable=True, comment="舒张压最小值(mmHg)"
    )
    blood_pressure_diastolic_max = Column(
        Integer, nullable=True, comment="舒张压最大值(mmHg)"
    )

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
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    device = db_relationship("Device", back_populates="device_threshold")
    user = db_relationship("User")
