"""
签到相关的Schema验证
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.schemas import BaseSchema


class CheckInCreate(BaseModel):
    """创建签到"""

    user_id: Optional[str] = Field(None, description="用户ID")
    latitude: Optional[str] = Field(None, description="纬度")
    longitude: Optional[str] = Field(None, description="经度")
    checkin_method: str = Field("manual", description="签到方式: manual/auto")
    notes: Optional[str] = Field(None, max_length=200, description="备注信息")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        """验证纬度"""
        if v is not None:
            try:
                lat = float(v)
            except (ValueError, TypeError):
                raise ValueError("经纬度必须是有效的数字")
            else:
                if lat < -90 or lat > 90:
                    raise ValueError("纬度必须在-90到90之间")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        """验证经度"""
        if v is not None:
            try:
                lon = float(v)
            except (ValueError, TypeError):
                raise ValueError("经纬度必须是有效的数字")
            else:
                if lon < -180 or lon > 180:
                    raise ValueError("经度必须在-180到180之间")
        return v

    @field_validator("checkin_method")
    @classmethod
    def validate_checkin_method(cls, v):
        """验证签到方式"""
        if v not in ["manual", "auto"]:
            raise ValueError("签到方式必须是 manual 或 auto")
        return v


class CheckInResponse(BaseSchema):
    """签到响应"""

    id: int
    user_id: str
    checkin_time: datetime
    checkin_date: str
    latitude: Optional[str]
    longitude: Optional[str]
    checkin_method: str
    notes: Optional[str]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, checkin) -> "CheckInResponse":
        """从CheckIn ORM对象转换为CheckInResponse"""
        return cls(
            id=checkin.id,
            user_id=checkin.user_id,
            checkin_time=checkin.checkin_time,
            checkin_date=checkin.checkin_date,
            latitude=checkin.latitude,
            longitude=checkin.longitude,
            checkin_method=checkin.checkin_method,
            notes=checkin.notes,
        )


class CheckInDateQuery(BaseModel):
    """查询签到日期"""

    user_id: Optional[str] = Field(None, description="用户ID")
    date: Optional[str] = Field(None, description="日期 YYYY-MM-DD")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    offset: int = Field(0, ge=0, description="偏移量")
    limit: int = Field(20, ge=1, le=100, description="返回数量")

    @field_validator("date", "start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v):
        """验证日期格式"""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("日期格式必须是 YYYY-MM-DD")
        return v


class CheckInStats(BaseModel):
    """签到统计"""

    user_id: str
    total_checkins: int
    this_month: int
    this_week: int
    today: bool
    consecutive_days: int
    last_checkin_date: Optional[str]


class CheckInStatsResponse(BaseModel):
    """签到统计响应"""

    total_checkins: int
    current_streak: int
    longest_streak: int
    checkin_rate: float


class CheckInHistoryResponse(BaseModel):
    """签到历史响应"""

    total_count: int
    checkins: List[CheckInResponse]


class CheckInStatusResponse(BaseModel):
    """签到状态响应"""

    is_checked_in: bool
    checkin_time: Optional[datetime]

    model_config = {"from_attributes": True}
