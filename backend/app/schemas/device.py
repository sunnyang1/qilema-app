"""
设备相关的Schema验证
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator


class DeviceType(str, Enum):
    """设备类型枚举"""

    SMART_WATCH = "smartwatch"
    SMART_BAND = "smartband"
    HEALTH_MONITOR = "health_monitor"
    OTHER = "other"


class DeviceCreate(BaseModel):
    """创建设备"""

    device_name: str = Field(..., min_length=1, max_length=50, description="设备名称")
    device_type: str = Field(..., min_length=1, max_length=20, description="设备类型")
    device_model: Optional[str] = Field(None, max_length=50, description="设备型号")
    firmware_version: Optional[str] = Field(None, max_length=20, description="固件版本")
    settings: Optional[Dict[str, Any]] = Field(None, description="设备设置")

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, v):
        """验证设备类型"""
        valid_types = ["smartwatch", "smartband", "health_monitor", "other"]
        if v not in valid_types:
            raise ValueError(f'设备类型必须是: {", ".join(valid_types)}')
        return v


class DeviceUpdate(BaseModel):
    """更新设备"""

    device_name: Optional[str] = Field(None, min_length=1, max_length=50)
    device_model: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None)
    settings: Optional[Dict[str, Any]] = Field(None)
    notes: Optional[str] = Field(None, description="备注")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v is not None and v not in ["active", "inactive", "offline"]:
            raise ValueError("状态必须是: active, inactive, 或 offline")
        return v


class DeviceResponse(BaseModel):
    """设备响应"""

    device_id: str
    user_id: str
    device_name: str
    device_type: str
    device_model: Optional[str]
    firmware_version: Optional[str]
    status: str
    settings: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    last_sync_time: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DeviceDataCreate(BaseModel):
    """创建设备数据"""

    device_id: str = Field(..., description="设备ID")
    data: Dict[str, Any] = Field(..., description="设备数据")
    sync_time: Optional[datetime] = Field(
        default_factory=datetime.now, description="同步时间"
    )


class DeviceDataQuery(BaseModel):
    """查询设备数据"""

    device_id: Optional[str] = Field(None, description="设备ID")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    data_type: Optional[str] = Field(None, description="数据类型")
    limit: int = Field(100, ge=1, le=1000, description="返回数量")


# ========== 路由文件中使用的额外Schema ==========


class DeviceBind(BaseModel):
    """绑定设备"""

    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., min_length=1, max_length=50, description="设备名称")
    device_type: str = Field(..., min_length=1, max_length=20, description="设备类型")
    device_brand: Optional[str] = Field(None, max_length=50, description="设备品牌")
    device_model: Optional[str] = Field(None, max_length=50, description="设备型号")
    firmware_version: Optional[str] = Field(None, max_length=20, description="固件版本")
    settings: Optional[Dict[str, Any]] = Field(None, description="设备设置")


class DeviceDataUpload(BaseModel):
    """上传设备数据"""

    device_id: str = Field(..., description="设备ID")
    data_type: Optional[str] = Field(None, description="数据类型")
    data_value: Optional[Dict[str, Any]] = Field(None, description="数据值")
    data_timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="数据时间戳"
    )
    upload_time: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="上传时间"
    )
    # 兼容旧 API 的字段
    heart_rate: Optional[int] = Field(None, description="心率(bpm)")
    steps: Optional[int] = Field(None, description="步数")
    calories: Optional[float] = Field(None, description="卡路里")
    distance: Optional[float] = Field(None, description="距离(km)")
    sleep_duration: Optional[float] = Field(None, description="睡眠时长(小时)")
    deep_sleep_duration: Optional[float] = Field(None, description="深度睡眠时长(小时)")
    systolic_pressure: Optional[int] = Field(None, description="收缩压(mmHg)")
    diastolic_pressure: Optional[int] = Field(None, description="舒张压(mmHg)")
    blood_oxygen: Optional[float] = Field(None, description="血氧(%)")
    body_temperature: Optional[float] = Field(None, description="体温(℃)")


class DeviceDataResponse(BaseModel):
    """设备数据响应"""

    data_id: str
    device_id: str
    user_id: str
    data_type: str
    data_value: Dict[str, Any]
    upload_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DeviceThresholdCreate(BaseModel):
    """创建设备阈值"""

    device_id: Union[str, int] = Field(..., description="设备ID")
    heart_rate_min: Optional[int] = Field(None, ge=30, le=200)
    heart_rate_max: Optional[int] = Field(None, ge=30, le=200)
    blood_pressure_systolic_min: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_systolic_max: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_diastolic_min: Optional[int] = Field(None, ge=40, le=130)
    blood_pressure_diastolic_max: Optional[int] = Field(None, ge=40, le=130)
    blood_oxygen_min: Optional[float] = Field(None, ge=70, le=100)
    temperature_min: Optional[float] = Field(None, ge=35, le=42)
    temperature_max: Optional[float] = Field(None, ge=35, le=42)
    steps_min: Optional[int] = Field(None, ge=0)
    steps_max: Optional[int] = Field(None, ge=0)
    sleep_duration_min: Optional[float] = Field(None, ge=0, le=24)
    alert_enabled: Optional[bool] = Field(None, description="是否启用预警")

    @field_validator("device_id", mode="before")
    @classmethod
    def validate_device_id(cls, v):
        """接受 int 或 str 类型的 device_id"""
        if isinstance(v, int):
            return str(v)
        return v


class DeviceThresholdUpdate(BaseModel):
    """更新设备阈值"""

    heart_rate_min: Optional[int] = Field(None, ge=30, le=200)
    heart_rate_max: Optional[int] = Field(None, ge=30, le=200)
    blood_pressure_systolic_min: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_systolic_max: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_diastolic_min: Optional[int] = Field(None, ge=40, le=130)
    blood_pressure_diastolic_max: Optional[int] = Field(None, ge=40, le=130)
    blood_oxygen_min: Optional[float] = Field(None, ge=70, le=100)
    temperature_min: Optional[float] = Field(None, ge=35, le=42)
    temperature_max: Optional[float] = Field(None, ge=35, le=42)
    steps_min: Optional[int] = Field(None, ge=0)
    steps_max: Optional[int] = Field(None, ge=0)
    sleep_duration_min: Optional[float] = Field(None, ge=0, le=24)
    alert_enabled: Optional[bool] = Field(None, description="是否启用预警")


class DeviceThresholdResponse(BaseModel):
    """设备阈值响应"""

    id: int
    device_id: str
    user_id: str
    heart_rate_min: Optional[int]
    heart_rate_max: Optional[int]
    blood_pressure_systolic_min: Optional[int]
    blood_pressure_systolic_max: Optional[int]
    blood_pressure_diastolic_min: Optional[int]
    blood_pressure_diastolic_max: Optional[int]
    blood_oxygen_min: Optional[float]
    temperature_min: Optional[float]
    temperature_max: Optional[float]
    steps_min: Optional[int]
    steps_max: Optional[int]
    sleep_duration_min: Optional[float]
    enabled: int
    alert_enabled: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

    @field_validator("alert_enabled", mode="before")
    @classmethod
    def convert_enabled_to_alert_enabled(cls, v):
        """将 enabled 转换为 alert_enabled"""
        if v is None:
            return None
        if isinstance(v, int):
            return v == 1
        return v


class DeviceStatusUpdate(BaseModel):
    """更新设备状态"""

    status: Optional[str] = Field(None, description="状态: active/inactive/offline")
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="电池电量")
    is_online: Optional[bool] = Field(None, description="是否在线")


class DeviceStatistics(BaseModel):
    """设备统计"""

    device_id: str
    data_type: str
    start_time: datetime
    end_time: datetime
    count: int
    avg: Optional[float]
    min: Optional[float]
    max: Optional[float]
    trend: Optional[str]


class DeviceAlert(BaseModel):
    """设备预警"""

    device_id: str
    alert_type: str
    alert_value: float
    threshold_value: float
    timestamp: datetime
