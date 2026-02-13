"""
设备异常相关的Schema验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.core.schemas import BaseSchema


class AnomalyTypeEnum(str, Enum):
    """异常类型枚举"""
    HEART_RATE_HIGH = "heart_rate_high"
    HEART_RATE_LOW = "heart_rate_low"
    BLOOD_PRESSURE_HIGH = "blood_pressure_high"
    BLOOD_PRESSURE_LOW = "blood_pressure_low"
    BLOOD_OXYGEN_LOW = "blood_oxygen_low"
    TEMPERATURE_HIGH = "temperature_high"
    FALL_DETECTED = "fall_detected"
    INACTIVITY_LONG = "inactivity_long"
    IRREGULAR_PATTERN = "irregular_pattern"


class SeverityLevel(str, Enum):
    """严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyStatus(str, Enum):
    """异常状态枚举"""
    PENDING = "pending"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class AnomalyCreate(BaseModel):
    """创建异常记录"""
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    anomaly_type: str = Field(..., description="异常类型")
    severity: str = Field(..., description="严重程度")
    detected_at: datetime = Field(default_factory=datetime.now, description="检测时间")
    anomaly_data: Optional[Dict[str, Any]] = Field(None, description="异常数据")
    threshold_value: Optional[float] = Field(None, description="阈值")
    actual_value: Optional[float] = Field(None, description="实际值")


class AnomalyUpdate(BaseModel):
    """更新异常记录"""
    status: Optional[str] = None
    notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class AnomalyQuery(BaseModel):
    """查询异常记录"""
    user_id: str = Field(..., description="用户ID")
    anomaly_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class AnomalyStatistics(BaseModel):
    """异常统计"""
    user_id: str
    total_anomalies: int
    by_type: Optional[Dict[str, int]] = None
    by_severity: Optional[Dict[str, int]] = None
    recent_critical: int


class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class HealthTrendResponse(BaseModel):
    """健康趋势响应"""
    user_id: str
    data_type: str
    start_date: datetime
    end_date: datetime
    data_points: List[Dict[str, Any]]
    average: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    trend: Optional[str] = None


class ActivityAnalysisRequest(BaseModel):
    """活动分析请求"""
    user_id: str = Field(..., description="用户ID")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ActivityPatternResponse(BaseModel):
    """活动模式响应"""
    user_id: str
    start_date: datetime
    end_date: datetime
    active_hours: List[Dict[str, Any]]
    sleep_hours: List[Dict[str, Any]]
    exercise_hours: List[Dict[str, Any]]
    average_daily_activity: float
    activity_patterns: List[str]


class AnomalyDetectionConfig(BaseModel):
    """异常检测配置"""
    heart_rate_min: Optional[float] = Field(None, ge=0, le=200)
    heart_rate_max: Optional[float] = Field(None, ge=0, le=200)
    blood_pressure_min: Optional[float] = Field(None, ge=0, le=200)
    blood_pressure_max: Optional[float] = Field(None, ge=0, le=200)
    blood_oxygen_min: Optional[float] = Field(None, ge=70, le=100)
    inactivity_threshold_minutes: Optional[int] = Field(None, ge=0)


class HeartHealthAnalysis(BaseModel):
    """心脏健康分析"""
    user_id: str
    average_heart_rate: float
    min_heart_rate: float
    max_heart_rate: float
    resting_heart_rate: Optional[float] = None
    heart_rate_variability: Optional[float] = None
    abnormal_beats: int
    abnormal_periods: List[Dict[str, Any]]
