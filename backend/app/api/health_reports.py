"""
健康数据报告API路由

提供健康趋势分析、综合报告、异常检测等RESTful接口
使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.api.dependencies import CurrentActiveUserDep, HealthReportServiceDep
from app.api.openapi_tags import TAG_HEALTH_RECORD
from app.core.exceptions import ValidationException
from app.core.response_builder import ApiResponseBuilder
from app.services.health_report_service import ReportPeriod

router = APIRouter(tags=[TAG_HEALTH_RECORD])


# ========== 请求/响应模型 ==========


class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""

    metric_type: str = Field(
        ..., description="指标类型: heart_rate/blood_pressure/blood_oxygen/steps/sleep"
    )
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


# ========== API端点 ==========


@router.post("/trend-analysis")
def get_trend_analysis(
    request: TrendAnalysisRequest,
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
):
    """
    获取健康数据趋势分析

    分析指定健康指标在时间段内的趋势、统计值、异常点
    """
    if request.start_date > request.end_date:
        raise ValidationException("开始日期不能晚于结束日期")

    result = service.get_trend_analysis(
        user_id=current_user.user_id,
        metric_type=request.metric_type,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
    )

    return ApiResponseBuilder.success(data=result, message="获取趋势分析成功")


@router.get("/comprehensive")
def get_comprehensive_report(
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
    report_date: date = Query(default_factory=date.today, description="报告日期"),
    period: ReportPeriod = Query(default=ReportPeriod.WEEK, description="报告周期"),
):
    """
    获取综合健康报告

    生成包含心率、血压、步数、睡眠等多项指标的综合健康报告
    """
    result = service.get_comprehensive_report(
        user_id=current_user.user_id, report_date=report_date, period=period
    )

    return ApiResponseBuilder.success(data=result, message="获取综合健康报告成功")


@router.get("/anomalies")
def get_anomaly_report(
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
    days: int = Query(default=7, ge=1, le=90, description="查询天数"),
    severity: Optional[str] = Query(
        default=None, description="严重程度筛选: high/medium/low"
    ),
):
    """
    获取异常检测报告

    查询指定天数内的健康数据异常，支持按严重程度筛选
    """
    result = service.get_anomaly_report(
        user_id=current_user.user_id, days=days, severity=severity
    )

    return ApiResponseBuilder.success(data=result, message="获取异常检测报告成功")


@router.post("/compare-periods")
def compare_periods(
    request: PeriodComparisonRequest,
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
):
    """
    对比两个时期的数据

    对比当前时期和上一时期的数据变化，计算变化百分比
    """
    result = service.compare_periods(
        user_id=current_user.user_id,
        metric_type=request.metric_type,
        current_start=request.current_start,
        current_end=request.current_end,
        previous_start=request.previous_start,
        previous_end=request.previous_end,
    )

    return ApiResponseBuilder.success(data=result, message="时期对比成功")


@router.get("/daily-summary/{summary_date}")
def get_daily_summary(
    summary_date: date,
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
):
    """
    获取每日健康摘要

    返回指定日期的健康数据摘要，包括步数、心率、睡眠等
    """
    result = service.get_daily_summary(
        user_id=current_user.user_id, summary_date=summary_date
    )

    return ApiResponseBuilder.success(data=result, message="获取每日健康摘要成功")


@router.get("/daily-summary")
def get_today_summary(
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
):
    """
    获取今日健康摘要

    快捷接口，返回今天的健康数据摘要
    """
    result = service.get_daily_summary(
        user_id=current_user.user_id, summary_date=date.today()
    )

    return ApiResponseBuilder.success(data=result, message="获取今日健康摘要成功")


@router.get("/metrics/available")
def get_available_metrics(current_user: CurrentActiveUserDep):
    """
    获取可用的健康指标列表

    返回系统支持的所有健康指标类型及其说明
    """
    return ApiResponseBuilder.success(
        data={
            "metrics": [
                {
                    "type": "heart_rate",
                    "name": "心率",
                    "unit": "bpm",
                    "description": "每分钟心跳次数",
                    "normal_range": "60-100 bpm",
                },
                {
                    "type": "blood_pressure",
                    "name": "血压",
                    "unit": "mmHg",
                    "description": "收缩压/舒张压",
                    "normal_range": "90-140/60-90 mmHg",
                },
                {
                    "type": "blood_oxygen",
                    "name": "血氧饱和度",
                    "unit": "%",
                    "description": "血液中氧气含量百分比",
                    "normal_range": "95-100%",
                },
                {
                    "type": "body_temperature",
                    "name": "体温",
                    "unit": "℃",
                    "description": "体表或体内温度",
                    "normal_range": "36.0-37.3℃",
                },
                {
                    "type": "steps",
                    "name": "步数",
                    "unit": "步",
                    "description": "每日行走步数",
                    "normal_range": "6000-20000步",
                },
                {
                    "type": "sleep",
                    "name": "睡眠",
                    "unit": "小时",
                    "description": "睡眠时长",
                    "normal_range": "6-10小时",
                },
            ]
        },
        message="获取可用健康指标列表成功",
    )


@router.get("/thresholds/default")
def get_default_thresholds(
    current_user: CurrentActiveUserDep,
    service: HealthReportServiceDep,
):
    """
    获取默认健康阈值

    返回系统默认的健康指标阈值范围
    """
    return ApiResponseBuilder.success(
        data={"thresholds": service.DEFAULT_THRESHOLDS},
        message="获取默认健康阈值成功",
    )
