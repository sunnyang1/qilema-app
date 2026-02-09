"""
健康数据报告API路由

提供健康趋势分析、综合报告、异常检测等RESTful接口
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User
from app.services.health_report_service import HealthReportService, ReportPeriod

router = APIRouter(prefix="/api/health-reports", tags=["健康报告"])


# ========== 请求/响应模型 ==========

class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""
    metric_type: str = Field(..., description="指标类型: heart_rate/blood_pressure/blood_oxygen/steps/sleep")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    period: ReportPeriod = Field(default=ReportPeriod.DAY, description="统计周期")


class PeriodComparisonRequest(BaseModel):
    """时期对比请求"""
    metric_type: str = Field(..., description="指标类型")
    current_start: date = Field(..., description="当前时期开始")
    current_end: date = Field(..., description="当前时期结束")
    previous_start: date = Field(..., description="对比时期开始")
    previous_end: date = Field(..., description="对比时期结束")


class TrendAnalysisResponse(BaseModel):
    """趋势分析响应"""
    metric_type: str
    period: str
    date_range: dict
    data_points: List[dict]
    statistics: Optional[dict]
    trend: str
    thresholds: dict
    anomalies: List[dict]
    total_readings: int


class ComprehensiveReportResponse(BaseModel):
    """综合健康报告响应"""
    report_id: str
    user_id: str
    report_type: str
    report_date: str
    period: dict
    overall_health_score: float
    health_level: str
    metrics: dict
    suggestions: List[str]
    user_profile: dict
    generated_at: str


class AnomalyReportResponse(BaseModel):
    """异常检测报告响应"""
    report_period: str
    start_date: str
    end_date: str
    total_anomalies: int
    severity_distribution: dict
    anomalies: List[dict]
    summary: str


class DailySummaryResponse(BaseModel):
    """每日健康摘要响应"""
    date: str
    user_id: str
    metrics: dict
    daily_score: float
    health_status: str


class PeriodComparisonResponse(BaseModel):
    """时期对比响应"""
    metric_type: str
    current_period: dict
    previous_period: dict
    changes: dict


# ========== API端点 ==========

@router.post("/trend-analysis", response_model=TrendAnalysisResponse)
def get_trend_analysis(
    request: TrendAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取健康数据趋势分析
    
    分析指定健康指标在时间段内的趋势、统计值、异常点
    """
    if request.start_date > request.end_date:
        raise ValidationException("开始日期不能晚于结束日期")
    
    result = HealthReportService.get_trend_analysis(
        db,
        user_id=current_user.user_id,
        metric_type=request.metric_type,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period
    )
    
    return TrendAnalysisResponse(**result)


@router.get("/comprehensive", response_model=ComprehensiveReportResponse)
def get_comprehensive_report(
    report_date: date = Query(default_factory=date.today, description="报告日期"),
    period: ReportPeriod = Query(default=ReportPeriod.WEEK, description="报告周期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取综合健康报告
    
    生成包含心率、血压、步数、睡眠等多项指标的综合健康报告
    """
    result = HealthReportService.get_comprehensive_report(
        db,
        user_id=current_user.user_id,
        report_date=report_date,
        period=period
    )
    
    return ComprehensiveReportResponse(**result)


@router.get("/anomalies", response_model=AnomalyReportResponse)
def get_anomaly_report(
    days: int = Query(default=7, ge=1, le=90, description="查询天数"),
    severity: Optional[str] = Query(default=None, description="严重程度筛选: high/medium/low"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取异常检测报告
    
    查询指定天数内的健康数据异常，支持按严重程度筛选
    """
    result = HealthReportService.get_anomaly_report(
        db,
        user_id=current_user.user_id,
        days=days,
        severity=severity
    )
    
    return AnomalyReportResponse(**result)


@router.post("/compare-periods", response_model=PeriodComparisonResponse)
def compare_periods(
    request: PeriodComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    对比两个时期的数据
    
    对比当前时期和上一时期的数据变化，计算变化百分比
    """
    result = HealthReportService.compare_periods(
        db,
        user_id=current_user.user_id,
        metric_type=request.metric_type,
        current_start=request.current_start,
        current_end=request.current_end,
        previous_start=request.previous_start,
        previous_end=request.previous_end
    )
    
    return PeriodComparisonResponse(**result)


@router.get("/daily-summary/{summary_date}", response_model=DailySummaryResponse)
def get_daily_summary(
    summary_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取每日健康摘要
    
    返回指定日期的健康数据摘要，包括步数、心率、睡眠等
    """
    result = HealthReportService.get_daily_summary(
        db,
        user_id=current_user.user_id,
        summary_date=summary_date
    )
    
    return DailySummaryResponse(**result)


@router.get("/daily-summary", response_model=DailySummaryResponse)
def get_today_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取今日健康摘要
    
    快捷接口，返回今天的健康数据摘要
    """
    result = HealthReportService.get_daily_summary(
        db,
        user_id=current_user.user_id,
        summary_date=date.today()
    )
    
    return DailySummaryResponse(**result)


@router.get("/metrics/available")
def get_available_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取可用的健康指标列表
    
    返回系统支持的所有健康指标类型及其说明
    """
    return {
        "metrics": [
            {
                "type": "heart_rate",
                "name": "心率",
                "unit": "bpm",
                "description": "每分钟心跳次数",
                "normal_range": "60-100 bpm"
            },
            {
                "type": "blood_pressure",
                "name": "血压",
                "unit": "mmHg",
                "description": "收缩压/舒张压",
                "normal_range": "90-140/60-90 mmHg"
            },
            {
                "type": "blood_oxygen",
                "name": "血氧饱和度",
                "unit": "%",
                "description": "血液中氧气含量百分比",
                "normal_range": "95-100%"
            },
            {
                "type": "body_temperature",
                "name": "体温",
                "unit": "℃",
                "description": "体表或体内温度",
                "normal_range": "36.0-37.3℃"
            },
            {
                "type": "steps",
                "name": "步数",
                "unit": "步",
                "description": "每日行走步数",
                "normal_range": "6000-20000步"
            },
            {
                "type": "sleep",
                "name": "睡眠",
                "unit": "小时",
                "description": "睡眠时长",
                "normal_range": "6-10小时"
            }
        ]
    }


@router.get("/thresholds/default")
def get_default_thresholds(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取默认健康阈值
    
    返回系统默认的健康指标阈值范围
    """
    return {
        "thresholds": HealthReportService.DEFAULT_THRESHOLDS
    }
