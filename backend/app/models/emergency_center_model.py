"""
120急救中心SQLAlchemy模型
"""

import enum

from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship as db_relationship


class EmergencyCallStatus(str, enum.Enum):
    """急救呼叫状态枚举"""

    DIALING = "dialing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class AmbulanceStatus(str, enum.Enum):
    """救护车状态枚举"""

    DISPATCHED = "dispatched"
    ON_ROUTE = "on_route"
    AT_SCENE = "at_scene"
    TRANSPORTING = "transporting"
    AT_HOSPITAL = "at_hospital"
    COMPLETED = "completed"


class EmergencyCenter(Base):
    """急救中心模型"""

    __tablename__ = "emergency_centers"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    center_name = Column(String(200), nullable=False, comment="急救中心名称")
    center_code = Column(
        String(50), unique=True, nullable=False, index=True, comment="急救中心代码"
    )
    province = Column(String(100), nullable=True, comment="省份")
    city = Column(String(100), nullable=False, comment="城市")
    district = Column(String(100), nullable=True, comment="区县")
    phone = Column(String(20), nullable=False, comment="联系电话")
    emergency_phone = Column(String(20), nullable=True, comment="急救专用电话")
    api_endpoint = Column(String(255), nullable=True, comment="API接口地址")
    api_key = Column(String(255), nullable=True, comment="API密钥")
    service_area = Column(Text, nullable=True, comment="服务范围描述")
    service_radius = Column(Integer, nullable=True, comment="服务半径(米)")
    is_active = Column(Integer, nullable=False, default=1, comment="是否启用: 0=否 1=是")
    is_24h = Column(Integer, nullable=False, default=1, comment="是否24小时服务: 0=否 1=是")
    has_ambulance_tracking = Column(
        Integer, nullable=False, default=0, comment="是否支持救护车追踪: 0=否 1=是"
    )
    has_auto_dispatch = Column(
        Integer, nullable=False, default=0, comment="是否支持自动派车: 0=否 1=是"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")


class EmergencyCall(Base):
    """120急救呼叫记录模型"""

    __tablename__ = "emergency_calls"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    sos_request_id = Column(String(36), nullable=True, index=True, comment="关联的SOS请求ID")
    emergency_center_id = Column(
        Integer,
        ForeignKey("emergency_centers.id"),
        nullable=True,
        index=True,
        comment="急救中心ID",
    )
    call_status = Column(
        SQLEnum(EmergencyCallStatus),
        nullable=False,
        default=EmergencyCallStatus.DIALING,
        comment="呼叫状态: dialing/connected/disconnected/failed",
    )
    dialed_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="拨号时间",
    )
    connected_at = Column(DateTime, nullable=True, comment="接通时间")
    ended_at = Column(DateTime, nullable=True, comment="结束时间")
    duration_seconds = Column(Integer, nullable=True, comment="通话时长(秒)")
    caller_location = Column(String(100), nullable=False, comment="拨打者位置(经度,纬度)")
    address_sent = Column(Text, nullable=True, comment="发送的地址信息")
    location_sent_at = Column(DateTime, nullable=True, comment="位置发送时间")
    health_summary_sent = Column(
        Integer, nullable=False, default=0, comment="是否发送健康档案摘要: 0=否 1=是"
    )
    health_summary_content = Column(Text, nullable=True, comment="发送的健康档案内容")
    health_summary_sent_at = Column(DateTime, nullable=True, comment="健康档案发送时间")
    call_recording_url = Column(String(255), nullable=True, comment="通话录音URL")
    call_notes = Column(Text, nullable=True, comment="通话备注")
    operator_name = Column(String(50), nullable=True, comment="接听调度员姓名")
    is_successful = Column(
        Integer, nullable=False, default=0, comment="是否拨打成功: 0=否 1=是"
    )
    failure_reason = Column(Text, nullable=True, comment="失败原因")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="emergency_calls")
    emergency_center = db_relationship("EmergencyCenter")


class Ambulance(Base):
    """救护车模型"""

    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    emergency_call_id = Column(
        Integer,
        ForeignKey("emergency_calls.id"),
        nullable=False,
        index=True,
        comment="急救呼叫记录ID",
    )
    target_resource_id = Column(Integer, nullable=True, index=True, comment="目标医院ID")
    ambulance_number = Column(String(50), nullable=True, comment="救护车编号")
    ambulance_type = Column(String(50), nullable=True, comment="救护车类型")
    plate_number = Column(String(50), nullable=True, comment="车牌号")
    status = Column(
        SQLEnum(AmbulanceStatus),
        nullable=False,
        default=AmbulanceStatus.DISPATCHED,
        comment="状态: dispatched/on_route/at_scene/transporting/at_hospital/completed",
    )
    current_latitude = Column(Float, nullable=True, comment="当前纬度")
    current_longitude = Column(Float, nullable=True, comment="当前经度")
    current_address = Column(String(255), nullable=True, comment="当前地址")
    location_updated_at = Column(DateTime, nullable=True, comment="位置更新时间")
    dispatched_at = Column(DateTime, nullable=True, comment="派出时间")
    arrived_at_scene_at = Column(DateTime, nullable=True, comment="到达现场时间")
    departed_from_scene_at = Column(DateTime, nullable=True, comment="离开现场时间")
    arrived_at_hospital_at = Column(DateTime, nullable=True, comment="到达医院时间")
    patient_name = Column(String(100), nullable=True, comment="患者姓名")
    patient_condition = Column(Text, nullable=True, comment="患者病情")
    medical_team = Column(Text, nullable=True, comment="医疗团队信息")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    eta_minutes = Column(Integer, nullable=True, comment="预计到达时间(分钟)")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")


class RescueRecord(Base):
    """救援记录模型"""

    __tablename__ = "rescue_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
        comment="用户ID",
    )
    sos_request_id = Column(Integer, nullable=True, index=True, comment="关联的SOS请求ID")
    emergency_call_id = Column(
        Integer,
        ForeignKey("emergency_calls.id"),
        nullable=True,
        index=True,
        comment="关联的急救呼叫ID",
    )
    rescue_type = Column(String(50), nullable=False, comment="救援类型")
    urgency_level = Column(String(20), nullable=False, comment="紧急程度")
    incident_time = Column(DateTime, nullable=False, comment="事故发生时间")
    alarm_time = Column(DateTime, nullable=False, comment="报警时间")
    dispatch_time = Column(DateTime, nullable=True, comment="派出时间")
    arrival_time = Column(DateTime, nullable=True, comment="到达现场时间")
    transport_time = Column(DateTime, nullable=True, comment="运送时间")
    hospital_arrival_time = Column(DateTime, nullable=True, comment="到达医院时间")
    completion_time = Column(DateTime, nullable=True, comment="救援完成时间")
    incident_location = Column(String(100), nullable=False, comment="事故地点(经度,纬度)")
    incident_address = Column(String(255), nullable=True, comment="事故地址")
    hospital_id = Column(Integer, nullable=True, comment="送达医院ID")
    outcome = Column(String(50), nullable=True, comment="救援结果")
    patient_status = Column(String(50), nullable=True, comment="患者状态")
    response_time_minutes = Column(Integer, nullable=True, comment="响应时间(分钟)")
    overall_duration_minutes = Column(Integer, nullable=True, comment="总时长(分钟)")
    ambulance_cost = Column(Float, nullable=True, comment="救护车费用")
    medical_cost = Column(Float, nullable=True, comment="医疗费用")
    user_feedback = Column(Text, nullable=True, comment="用户反馈")
    user_rating = Column(Integer, nullable=True, comment="用户评分")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")
