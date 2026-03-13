"""
预警相关的Schema验证
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AlertSettingCreate(BaseModel):
    """创建预警配置"""

    checkin_threshold_hours: int = Field(24, description="未签到阈值(小时)")

    @field_validator("checkin_threshold_hours")
    @classmethod
    def validate_threshold(cls, v):
        """验证预警阈值"""
        if v < 6 or v > 168:
            raise ValueError("预警阈值必须是6到168之间的整数")
        return v

    checkin_enabled: bool = Field(True, description="启用未签到预警")
    abnormal_enabled: bool = Field(True, description="启用生理异常预警")
    enable_notification: bool = Field(True, description="启用通知")
    heart_rate_min: Optional[int] = Field(None, ge=30, le=200, description="心率最小值")
    heart_rate_max: Optional[int] = Field(None, ge=30, le=200, description="心率最大值")
    blood_pressure_systolic_min: Optional[int] = Field(
        None, ge=60, le=200, description="收缩压最小值"
    )
    blood_pressure_systolic_max: Optional[int] = Field(
        None, ge=60, le=200, description="收缩压最大值"
    )
    blood_pressure_diastolic_min: Optional[int] = Field(
        None, ge=40, le=130, description="舒张压最小值"
    )
    blood_pressure_diastolic_max: Optional[int] = Field(
        None, ge=40, le=130, description="舒张压最大值"
    )
    blood_oxygen_min: Optional[float] = Field(None, ge=70, le=100, description="血氧最小值")
    notification_channels: Optional[List[str]] = Field(None, description="通知渠道")
    emergency_contact_notify: bool = Field(True, description="通知紧急联系人")
    auto_resolve: bool = Field(True, description="自动解决")

    @field_validator("notification_channels", mode="before")
    @classmethod
    def parse_notification_channels(cls, v):
        """解析通知渠道,支持字符串和列表两种格式"""
        if v is None:
            return None
        if isinstance(v, str):
            channels = v.split(",") if v else None
            # 验证通知渠道
            valid_channels = {"push", "sms", "email"}
            if channels:
                for ch in channels:
                    if ch not in valid_channels:
                        raise ValueError(f"通知渠道必须是以下之一: {', '.join(valid_channels)}")
            return channels
        # 如果是列表,也要验证
        if isinstance(v, list):
            valid_channels = {"push", "sms", "email"}
            for ch in v:
                if ch not in valid_channels:
                    raise ValueError(f"通知渠道必须是以下之一: {', '.join(valid_channels)}")
        return v


class AlertSettingUpdate(BaseModel):
    """更新预警配置"""

    checkin_threshold_hours: Optional[int] = Field(None, ge=1, le=168)
    checkin_enabled: Optional[bool] = None
    abnormal_enabled: Optional[bool] = None
    enable_notification: Optional[bool] = None
    heart_rate_min: Optional[int] = Field(None, ge=30, le=200)
    heart_rate_max: Optional[int] = Field(None, ge=30, le=200)
    blood_pressure_systolic_min: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_systolic_max: Optional[int] = Field(None, ge=60, le=200)
    blood_pressure_diastolic_min: Optional[int] = Field(None, ge=40, le=130)
    blood_pressure_diastolic_max: Optional[int] = Field(None, ge=40, le=130)
    blood_oxygen_min: Optional[float] = Field(None, ge=70, le=100)
    notification_channels: Optional[List[str]] = None
    emergency_contact_notify: Optional[bool] = None
    auto_resolve: Optional[bool] = None


class AlertSettingResponse(BaseModel):
    """预警配置响应"""

    id: int
    user_id: str
    checkin_enabled: bool
    checkin_threshold_hours: int
    abnormal_enabled: bool
    enable_notification: bool
    heart_rate_min: Optional[int]
    heart_rate_max: Optional[int]
    blood_pressure_systolic_min: Optional[int]
    blood_pressure_systolic_max: Optional[int]
    blood_pressure_diastolic_min: Optional[int]
    blood_pressure_diastolic_max: Optional[int]
    blood_oxygen_min: Optional[float]
    notification_channels: Optional[List[str]]
    emergency_contact_notify: bool
    auto_resolve: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AlertCreate(BaseModel):
    """创建预警"""

    user_id: str = Field(..., description="用户ID")
    alert_type: str = Field(..., description="预警类型")
    severity: str = Field("medium", description="严重程度")
    trigger_time: datetime = Field(default_factory=datetime.now, description="触发时间")
    trigger_reason: Optional[str] = Field(None, description="触发原因")
    missed_days: Optional[int] = Field(None, description="未签到天数")
    threshold_hours: Optional[int] = Field(None, description="阈值小时数")
    abnormal_data: Optional[dict] = Field(None, description="异常数据")


class AlertResolveRequest(BaseModel):
    """解决预警请求"""

    resolved_reason: Optional[str] = Field(None, description="解决原因")
    resolve_note: Optional[str] = Field(None, description="解决备注")


class AlertResponse(BaseModel):
    """预警响应"""

    alert_id: str
    user_id: str
    alert_type: int
    trigger_time: datetime
    status: int
    last_checkin_time: Optional[datetime]
    abnormal_data: Optional[dict]
    notification_sent: Optional[List[dict]]
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
