"""
120急救中心对接Schema验证

提供120呼叫、救护车追踪、救援记录等数据验证
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# ========== 枚举定义 ==========


class EmergencyCallStatus(str, Enum):
    """急救呼叫状态枚举"""

    DIALING = "dialing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class AmbulanceStatus(str, Enum):
    """救护车状态枚举"""

    DISPATCHED = "dispatched"
    ON_ROUTE = "on_route"
    AT_SCENE = "at_scene"
    TRANSPORTING = "transporting"
    AT_HOSPITAL = "at_hospital"
    COMPLETED = "completed"


# ========== 急救中心配置相关 ==========


class EmergencyCenterBase(BaseModel):
    """急救中心基础模型"""

    center_name: str = Field(..., min_length=1, max_length=200, description="急救中心名称")
    center_code: str = Field(..., min_length=1, max_length=50, description="急救中心代码")
    province: Optional[str] = Field(None, max_length=100, description="省份")
    city: str = Field(..., min_length=1, max_length=100, description="城市")
    district: Optional[str] = Field(None, max_length=100, description="区县")


class EmergencyCenterCreate(EmergencyCenterBase):
    """创建急救中心"""

    phone: str = Field(..., min_length=1, description="联系电话")
    emergency_phone: Optional[str] = Field(None, description="急救专用电话")
    api_endpoint: Optional[str] = Field(None, description="API接口地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    service_area: Optional[str] = Field(None, description="服务范围描述")
    service_radius: Optional[int] = Field(None, ge=0, description="服务半径(米)")
    is_active: bool = Field(True, description="是否启用")
    is_24h: bool = Field(True, description="是否24小时服务")
    has_ambulance_tracking: bool = Field(False, description="是否支持救护车追踪")
    has_auto_dispatch: bool = Field(False, description="是否支持自动派车")


class EmergencyCenterUpdate(BaseModel):
    """更新急救中心"""

    center_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=1)
    emergency_phone: Optional[str] = Field(None)
    api_endpoint: Optional[str] = Field(None)
    api_key: Optional[str] = Field(None)
    service_area: Optional[str] = Field(None)
    service_radius: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = Field(None)
    is_24h: Optional[bool] = Field(None)
    has_ambulance_tracking: Optional[bool] = Field(None)
    has_auto_dispatch: Optional[bool] = Field(None)


class EmergencyCenterResponse(EmergencyCenterBase):
    """急救中心响应"""

    id: int
    phone: str
    emergency_phone: Optional[str]
    is_active: bool
    is_24h: bool
    has_ambulance_tracking: bool
    has_auto_dispatch: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ========== 120急救呼叫相关 ==========


class EmergencyCallCreate(BaseModel):
    """创建120急救呼叫"""

    user_id: str = Field(..., description="用户ID")
    sos_request_id: Optional[int] = Field(None, description="关联的SOS请求ID")
    emergency_center_id: Optional[int] = Field(None, description="急救中心ID")
    caller_location: str = Field(..., description="拨打者位置(经度,纬度)")


class EmergencyCallUpdate(BaseModel):
    """更新120急救呼叫"""

    call_status: Optional[EmergencyCallStatus] = Field(None, description="呼叫状态")
    connected_at: Optional[datetime] = Field(None, description="接通时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    address_sent: Optional[str] = Field(None, description="发送的地址信息")
    location_sent_at: Optional[datetime] = Field(None, description="位置发送时间")
    health_summary_sent: Optional[bool] = Field(None, description="是否发送健康档案摘要")
    health_summary_content: Optional[str] = Field(None, description="发送的健康档案内容")
    health_summary_sent_at: Optional[datetime] = Field(None, description="健康档案发送时间")
    call_recording_url: Optional[str] = Field(None, description="通话录音URL")
    call_notes: Optional[str] = Field(None, description="通话备注")
    operator_name: Optional[str] = Field(None, description="接听调度员姓名")
    is_successful: Optional[bool] = Field(None, description="是否拨打成功")
    failure_reason: Optional[str] = Field(None, description="失败原因")


class EmergencyCallResponse(BaseModel):
    """120急救呼叫响应"""

    id: int
    user_id: str
    sos_request_id: Optional[int]
    emergency_center_id: Optional[int]
    call_status: EmergencyCallStatus
    dialed_at: datetime
    connected_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    caller_location: str
    address_sent: Optional[str]
    location_sent_at: Optional[datetime]
    health_summary_sent: bool
    health_summary_content: Optional[str]
    health_summary_sent_at: Optional[datetime]
    call_recording_url: Optional[str]
    call_notes: Optional[str]
    operator_name: Optional[str]
    is_successful: bool
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ========== 救护车相关 ==========


class AmbulanceCreate(BaseModel):
    """创建救护车"""

    emergency_call_id: int = Field(..., description="急救呼叫记录ID")
    target_resource_id: Optional[int] = Field(None, description="目标医院ID")
    ambulance_number: Optional[str] = Field(None, max_length=50, description="救护车编号")
    ambulance_type: Optional[str] = Field(None, description="救护车类型")
    plate_number: Optional[str] = Field(None, max_length=50, description="车牌号")
    patient_name: Optional[str] = Field(None, max_length=100, description="患者姓名")
    patient_condition: Optional[str] = Field(None, description="患者病情")
    medical_team: Optional[str] = Field(None, description="医疗团队信息")
    contact_phone: Optional[str] = Field(None, description="联系电话")


class AmbulanceUpdate(BaseModel):
    """更新救护车"""

    status: Optional[AmbulanceStatus] = Field(None, description="救护车状态")
    current_latitude: Optional[float] = Field(None, ge=-90, le=90, description="当前纬度")
    current_longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="当前经度"
    )
    current_address: Optional[str] = Field(None, description="当前地址")
    location_updated_at: Optional[datetime] = Field(None, description="位置更新时间")
    arrived_at_scene_at: Optional[datetime] = Field(None, description="到达现场时间")
    departed_from_scene_at: Optional[datetime] = Field(None, description="离开现场时间")
    arrived_at_hospital_at: Optional[datetime] = Field(None, description="到达医院时间")
    patient_name: Optional[str] = Field(None, max_length=100)
    patient_condition: Optional[str] = Field(None)
    medical_team: Optional[str] = Field(None)
    contact_phone: Optional[str] = Field(None)
    eta_minutes: Optional[int] = Field(None, ge=0, description="预计到达时间(分钟)")


class AmbulanceResponse(BaseModel):
    """救护车响应"""

    id: int
    emergency_call_id: int
    target_resource_id: Optional[int]
    ambulance_number: Optional[str]
    ambulance_type: Optional[str]
    plate_number: Optional[str]
    status: AmbulanceStatus
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    current_address: Optional[str]
    location_updated_at: Optional[datetime]
    dispatched_at: Optional[datetime]
    arrived_at_scene_at: Optional[datetime]
    departed_from_scene_at: Optional[datetime]
    arrived_at_hospital_at: Optional[datetime]
    patient_name: Optional[str]
    patient_condition: Optional[str]
    medical_team: Optional[str]
    contact_phone: Optional[str]
    eta_minutes: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AmbulanceLocation(BaseModel):
    """救护车位置信息"""

    ambulance_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, description="当前地址")
    timestamp: datetime = Field(default_factory=datetime.now, description="更新时间")


# ========== 救援记录相关 ==========


class RescueRecordCreate(BaseModel):
    """创建救援记录"""

    user_id: str = Field(..., description="用户ID")
    sos_request_id: Optional[int] = Field(None, description="关联的SOS请求ID")
    emergency_call_id: Optional[int] = Field(None, description="关联的急救呼叫ID")
    rescue_type: str = Field(..., description="救援类型")
    urgency_level: str = Field(..., description="紧急程度")
    incident_time: datetime = Field(..., description="事故发生时间")
    alarm_time: datetime = Field(..., description="报警时间")
    incident_location: str = Field(..., description="事故地点(经度,纬度)")
    incident_address: Optional[str] = Field(None, description="事故地址")
    hospital_id: Optional[int] = Field(None, description="送达医院ID")


class RescueRecordUpdate(BaseModel):
    """更新救援记录"""

    dispatch_time: Optional[datetime] = Field(None, description="派出时间")
    arrival_time: Optional[datetime] = Field(None, description="到达现场时间")
    transport_time: Optional[datetime] = Field(None, description="运送时间")
    hospital_arrival_time: Optional[datetime] = Field(None, description="到达医院时间")
    completion_time: Optional[datetime] = Field(None, description="救援完成时间")
    outcome: Optional[str] = Field(None, description="救援结果")
    patient_status: Optional[str] = Field(None, description="患者状态")
    ambulance_cost: Optional[float] = Field(None, ge=0, description="救护车费用")
    medical_cost: Optional[float] = Field(None, ge=0, description="医疗费用")
    user_feedback: Optional[str] = Field(None, description="用户反馈")
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="用户评分")


class RescueRecordResponse(BaseModel):
    """救援记录响应"""

    id: int
    user_id: str
    sos_request_id: Optional[int]
    emergency_call_id: Optional[int]
    rescue_type: str
    urgency_level: str
    incident_time: datetime
    alarm_time: datetime
    dispatch_time: Optional[datetime]
    arrival_time: Optional[datetime]
    transport_time: Optional[datetime]
    hospital_arrival_time: Optional[datetime]
    completion_time: Optional[datetime]
    incident_location: str
    incident_address: Optional[str]
    hospital_id: Optional[int]
    outcome: Optional[str]
    patient_status: Optional[str]
    ambulance_cost: Optional[float]
    medical_cost: Optional[float]
    response_time_minutes: Optional[int]
    overall_duration_minutes: Optional[int]
    user_feedback: Optional[str]
    user_rating: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ========== 120拨号请求 ==========


class Call120Request(BaseModel):
    """120拨号请求"""

    user_id: str = Field(..., description="用户ID")
    sos_request_id: Optional[int] = Field(None, description="关联的SOS请求ID")
    caller_location: str = Field(..., description="拨打者位置(经度,纬度)")
    send_health_summary: bool = Field(True, description="是否发送健康档案摘要")


class Call120Response(BaseModel):
    """120拨号响应"""

    call_id: int
    call_status: str
    dialed_at: datetime
    emergency_center_id: Optional[int]
    emergency_center_name: Optional[str]
    emergency_phone: str
    location_sent: bool
    health_summary_sent: bool
    ambulance_dispatched: Optional[bool] = Field(None, description="是否已派出救护车")


# ========== 健康档案摘要 ==========


class HealthSummary(BaseModel):
    """健康档案摘要"""

    user_id: str = Field(..., description="用户ID")
    user_name: Optional[str] = Field(None, description="用户姓名")
    age: Optional[int] = Field(None, description="年龄")
    blood_type: Optional[str] = Field(None, description="血型")

    # 健康状况
    chronic_diseases: Optional[List[str]] = Field(None, description="慢性病史")
    allergies: Optional[List[str]] = Field(None, description="过敏史")
    current_medications: Optional[List[str]] = Field(None, description="当前用药")

    # 最新健康数据
    latest_heart_rate: Optional[float] = Field(None, description="最新心率")
    latest_blood_pressure: Optional[str] = Field(None, description="最新血压")
    latest_blood_oxygen: Optional[float] = Field(None, description="最新血氧")

    # 紧急联系人
    emergency_contacts: Optional[List[dict]] = Field(None, description="紧急联系人列表")

    # 最近设备异常
    recent_anomalies: Optional[List[dict]] = Field(None, description="最近异常记录")

    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")


# ========== 救护车追踪 ==========


class AmbulanceTracking(BaseModel):
    """救护车追踪信息"""

    ambulance_id: int
    ambulance_number: Optional[str]
    status: AmbulanceStatus
    current_location: dict = Field(..., description="当前位置(纬度,经度)")
    current_address: Optional[str]
    eta_minutes: Optional[int]
    distance_to_scene: Optional[float] = Field(None, description="到现场距离(米)")
    distance_to_hospital: Optional[float] = Field(None, description="到医院距离(米)")
    contact_phone: Optional[str]
    location_updated_at: datetime


class AmbulanceTrackingQuery(BaseModel):
    """救护车追踪查询"""

    emergency_call_id: int = Field(..., description="急救呼叫记录ID")
