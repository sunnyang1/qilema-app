"""
设备数据异常监测数据模型

记录生理数据异常事件,包括异常类型、严重程度、触发条件等
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class AnomalyTypeEnum(str, enum.Enum):
    """异常类型枚举"""
    HEART_RATE_HIGH = "heart_rate_high"          # 心率过高
    HEART_RATE_LOW = "heart_rate_low"            # 心率过低
    HEART_RATE_SUDDEN_CHANGE = "heart_rate_sudden_change"  # 心率骤变
    HEART_RATE_STOP = "heart_rate_stop"          # 心率骤停
    NO_ACTIVITY = "no_activity"                 # 连续无活动
    BLOOD_PRESSURE_HIGH = "blood_pressure_high"  # 血压过高
    BLOOD_PRESSURE_LOW = "blood_pressure_low"    # 血压过低
    BLOOD_OXYGEN_LOW = "blood_oxygen_low"        # 血氧过低
    TEMPERATURE_HIGH = "temperature_high"        # 体温过高
    TEMPERATURE_LOW = "temperature_low"          # 体温过低
    FALL_DETECTED = "fall_detected"             # 跌倒检测
    IRREGULAR_RHYTHM = "irregular_rhythm"        # 心律不齐


class SeverityLevel(str, enum.Enum):
    """严重程度枚举"""
    LOW = "low"              # 轻微:需要关注
    MEDIUM = "medium"        # 中等:需要提醒
    HIGH = "high"            # 严重:需要预警
    CRITICAL = "critical"    # 危急:需要立即救援


class AnomalyStatus(str, enum.Enum):
    """异常状态枚举"""
    PENDING = "pending"          # 待处理
    CONFIRMED = "confirmed"      # 已确认
    RESOLVED = "resolved"        # 已解决
    DISMISSED = "dismissed"      # 已忽略


class Anomaly(Base):
    """生理数据异常记录"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True, comment="异常记录ID")
    
    # 基本信息
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"),
                     nullable=False, index=True, comment="用户ID")
    device_id = Column(String(36), ForeignKey("devices.device_id", ondelete="SET NULL"),
                       nullable=True, comment="设备ID")

    # 异常信息
    anomaly_type = Column(SQLEnum(AnomalyTypeEnum), nullable=False, index=True, comment="异常类型")
    severity = Column(SQLEnum(SeverityLevel), nullable=False, index=True, comment="严重程度")
    status = Column(SQLEnum(AnomalyStatus), default=AnomalyStatus.PENDING, index=True, comment="异常状态")

    # 异常数据 (device_data_id 暂时注释,等待 DeviceData 模型实现)
    # device_data_id = Column(Integer, ForeignKey("device_data.id", ondelete="SET NULL"),
    #                         nullable=True, comment="设备数据ID")
    anomaly_value = Column(Float, nullable=True, comment="异常数值")
    threshold_value = Column(Float, nullable=True, comment="阈值参考")
    deviation_ratio = Column(Float, nullable=True, comment="偏离比例(%)")
    
    # 详细描述
    description = Column(Text, nullable=True, comment="异常描述")
    trigger_condition = Column(Text, nullable=True, comment="触发条件")
    
    # 时间信息
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), 
                         nullable=False, index=True, comment="检测时间")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="解决时间")
    
    # 处理信息
    action_taken = Column(Text, nullable=True, comment="采取的措施")
    sos_triggered = Column(Integer, ForeignKey("sos_requests.id", ondelete="SET NULL"),
                          nullable=True, comment="触发的SOS记录ID")

    # 元数据
    extra_metadata = Column(Text, nullable=True, comment="额外元数据(JSON格式)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")

    # 关联关系
    user = db_relationship("User", back_populates="anomalies")
    device = db_relationship("Device", back_populates="anomalies")
    # device_data = db_relationship("DeviceData", back_populates="anomalies")  # 等待 DeviceData 模型实现
    sos_request = db_relationship("SOSRequest", back_populates="anomalies")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "anomaly_type": self.anomaly_type.value if self.anomaly_type else None,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "device_data_id": self.device_data_id,
            "anomaly_value": self.anomaly_value,
            "threshold_value": self.threshold_value,
            "deviation_ratio": self.deviation_ratio,
            "description": self.description,
            "trigger_condition": self.trigger_condition,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "action_taken": self.action_taken,
            "sos_triggered": self.sos_triggered,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class HealthTrend(Base):
    """健康数据趋势分析"""
    __tablename__ = "health_trends"
    
    id = Column(Integer, primary_key=True, index=True, comment="趋势分析ID")
    
    # 基本信息
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), 
                     nullable=False, index=True, comment="用户ID")
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), 
                       nullable=True, comment="设备ID")
    
    # 趋势信息
    metric_type = Column(String(50), nullable=False, index=True, comment="指标类型(heart_rate/blood_pressure/etc)")
    period_type = Column(String(20), nullable=False, comment="周期类型(daily/weekly/monthly)")
    start_date = Column(DateTime, nullable=False, index=True, comment="开始日期")
    end_date = Column(DateTime, nullable=False, index=True, comment="结束日期")
    
    # 统计数据
    avg_value = Column(Float, nullable=False, comment="平均值")
    min_value = Column(Float, nullable=False, comment="最小值")
    max_value = Column(Float, nullable=False, comment="最大值")
    std_deviation = Column(Float, nullable=True, comment="标准差")
    
    # 趋势分析
    trend_direction = Column(String(10), nullable=True, comment="趋势方向(up/down/stable)")
    trend_percentage = Column(Float, nullable=True, comment="变化百分比")
    
    # 数据质量
    sample_count = Column(Integer, nullable=False, comment="样本数量")
    missing_count = Column(Integer, nullable=False, comment="缺失数据数量")
    quality_score = Column(Float, nullable=True, comment="数据质量分数(0-100)")
    
    # 建议
    insights = Column(Text, nullable=True, comment="分析洞察")
    recommendations = Column(Text, nullable=True, comment="健康建议")
    
    # 元数据
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), 
                          nullable=False, comment="生成时间")
    
    # 关联关系
    user = db_relationship("User", back_populates="health_trends")
    device = db_relationship("Device", back_populates="health_trends")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "metric_type": self.metric_type,
            "period_type": self.period_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "avg_value": self.avg_value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "std_deviation": self.std_deviation,
            "trend_direction": self.trend_direction,
            "trend_percentage": self.trend_percentage,
            "sample_count": self.sample_count,
            "missing_count": self.missing_count,
            "quality_score": self.quality_score,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


class ActivityPattern(Base):
    """活动模式分析"""
    __tablename__ = "activity_patterns"
    
    id = Column(Integer, primary_key=True, index=True, comment="活动模式ID")
    
    # 基本信息
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), 
                     nullable=False, index=True, comment="用户ID")
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), 
                       nullable=True, comment="设备ID")
    
    # 模式信息
    analysis_date = Column(DateTime, nullable=False, index=True, comment="分析日期")
    period_type = Column(String(20), nullable=False, comment="周期类型(daily/weekly)")
    
    # 活动统计
    total_steps = Column(Integer, nullable=False, comment="总步数")
    active_minutes = Column(Integer, nullable=False, comment="活跃时长(分钟)")
    sedentary_minutes = Column(Integer, nullable=False, comment="久坐时长(分钟)")
    sleep_hours = Column(Float, nullable=True, comment="睡眠时长(小时)")
    calories_burned = Column(Float, nullable=True, comment="消耗卡路里")
    
    # 模式识别
    peak_activity_hours = Column(String(100), nullable=True, comment="活跃时段")
    inactive_periods = Column(Text, nullable=True, comment="不活跃时间段(JSON)")
    
    # 异常检测
    is_inactive = Column(Integer, server_default="0", comment="是否异常无活动(0否/1是)")
    inactive_hours = Column(Integer, nullable=True, comment="无活动持续时长(小时)")
    activity_score = Column(Float, nullable=True, comment="活跃度评分(0-100)")
    
    # 建议
    activity_insights = Column(Text, nullable=True, comment="活动分析洞察")
    improvement_suggestions = Column(Text, nullable=True, comment="改善建议")
    
    # 元数据
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), 
                          nullable=False, comment="生成时间")
    
    # 关联关系
    user = db_relationship("User", back_populates="activity_patterns")
    device = db_relationship("Device", back_populates="activity_patterns")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "period_type": self.period_type,
            "total_steps": self.total_steps,
            "active_minutes": self.active_minutes,
            "sedentary_minutes": self.sedentary_minutes,
            "sleep_hours": self.sleep_hours,
            "calories_burned": self.calories_burned,
            "peak_activity_hours": self.peak_activity_hours,
            "inactive_periods": self.inactive_periods,
            "is_inactive": self.is_inactive,
            "inactive_hours": self.inactive_hours,
            "activity_score": self.activity_score,
            "activity_insights": self.activity_insights,
            "improvement_suggestions": self.improvement_suggestions,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }