"""
设备相关的Schema验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


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

    @field_validator('device_type')
    @classmethod
    def validate_device_type(cls, v):
        """验证设备类型"""
        valid_types = ['smartwatch', 'smartband', 'health_monitor', 'other']
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

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """验证状态"""
        if v is not None and v not in ['active', 'inactive', 'offline']:
            raise ValueError('状态必须是: active, inactive, 或 offline')
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
    sync_time: Optional[datetime] = Field(default_factory=datetime.now, description="同步时间")


class DeviceDataQuery(BaseModel):
    """查询设备数据"""
    device_id: str = Field(..., description="设备ID")
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
    data_type: str = Field(..., description="数据类型")
    data_value: Dict[str, Any] = Field(..., description="数据值")
    upload_time: Optional[datetime] = Field(default_factory=datetime.now, description="上传时间")


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
    device_id: str = Field(..., description="设备ID")
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
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DeviceStatusUpdate(BaseModel):
    """更新设备状态"""
    status: str = Field(..., description="状态: active/inactive/offline")
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="电池电量")


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

