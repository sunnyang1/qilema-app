"""
SOS求救相关的Schema验证
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.core.schemas import BaseSchema


class SOSRequestCreate(BaseModel):
    """创建SOS求救请求"""

    user_id: str = Field(..., description="用户ID")
    device_id: Optional[str] = Field(None, description="设备ID")
    sos_type: Optional[str] = Field(None, description="SOS类型: manual/auto/device")
    trigger_type: Optional[str] = Field(None, description="触发类型: manual/auto/health")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    address: Optional[str] = Field(None, max_length=255, description="地址描述")
    location_description: Optional[str] = Field(
        None, max_length=200, description="位置描述"
    )
    location_accuracy: Optional[float] = Field(None, description="定位精度(米)")
    emergency_reason: Optional[str] = Field(None, description="紧急原因描述")
    health_data: Optional[Dict[str, Any]] = Field(None, description="健康数据")
    severity: str = Field("high", description="严重程度: low/medium/high/critical")


class SOSRequestUpdate(BaseModel):
    """更新SOS求救请求"""

    status: Optional[str] = Field(None, description="状态: pending/responding/resolved")
    responder_notes: Optional[str] = Field(None, max_length=500, description="救援人员备注")


class SOSRequestResponse(BaseSchema):
    """SOS求救请求响应"""

    sos_id: str
    user_id: str
    device_id: Optional[str]
    trigger_type: str
    status: str
    latitude: Optional[str]
    longitude: Optional[str]
    location_description: Optional[str]
    health_data: Optional[Dict[str, Any]]
    severity: str
    auto_dispatch: int
    emergency_center_notified: int
    contacts_notified: Optional[Dict[str, Any]]
    responder_notes: Optional[str]
    triggered_at: datetime
    responded_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, sos_request) -> "SOSRequestResponse":
        """从SosRequest ORM对象转换为SOSRequestResponse"""
        return cls(
            sos_id=sos_request.sos_id,
            user_id=sos_request.user_id,
            device_id=sos_request.device_id,
            trigger_type=sos_request.trigger_type,
            status=sos_request.status,
            latitude=sos_request.latitude,
            longitude=sos_request.longitude,
            location_description=sos_request.location_description,
            health_data=sos_request.health_data,
            severity=sos_request.severity,
            auto_dispatch=sos_request.auto_dispatch,
            emergency_center_notified=sos_request.emergency_center_notified,
            contacts_notified=sos_request.contacts_notified,
            responder_notes=sos_request.responder_notes,
            triggered_at=sos_request.triggered_at,
            responded_at=sos_request.responded_at,
            resolved_at=sos_request.resolved_at,
            created_at=sos_request.created_at,
        )


class SOSLocationUpdate(BaseModel):
    """SOS位置更新"""

    sos_id: Optional[str] = Field(None, description="SOS请求ID")
    sos_request_id: Optional[int] = Field(None, description="SOS请求ID(备用)")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    location_description: Optional[str] = Field(
        None, max_length=200, description="位置描述"
    )
    location_accuracy: Optional[float] = Field(None, description="定位精度(米)")
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )


class SOSCancelRequest(BaseModel):
    """SOS取消请求"""

    sos_id: Optional[str] = Field(None, description="SOS请求ID")
    sos_request_id: Optional[int] = Field(None, description="SOS请求ID(备用)")
    cancel_reason: Optional[str] = Field(None, max_length=500, description="取消原因")
    reason: Optional[str] = Field(None, max_length=500, description="取消原因(备用)")
    confirm_code: Optional[str] = Field(None, description="确认码")
    cancelled_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="取消时间"
    )


class SOSStatusUpdateRequest(BaseModel):
    """SOS状态更新请求"""

    sos_id: Optional[str] = Field(None, description="SOS请求ID")
    status: str = Field(..., description="状态: pending/rescuing/resolved/cancelled")
    status_change_reason: Optional[str] = Field(
        None, max_length=255, description="状态变更原因"
    )
    ambulance_contact: Optional[str] = Field(None, max_length=50, description="救护车联系方式")
    ambulance_eta: Optional[int] = Field(None, description="救护车预计到达时间(分钟)")
    responder_notes: Optional[str] = Field(None, max_length=500, description="救援人员备注")
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )
