"""
设备数据异常监测API路由

提供异常检测、趋势分析、心脏健康分析等RESTful接口
使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, status
from sqlalchemy import desc

from app.api.dependencies import (
    AnomalyServiceDep,
    CurrentAdminDep,
    CurrentUserDep,
    DbSession,
)
from app.api.openapi_tags import TAG_CHECKIN_MONITOR
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from app.core.response_builder import ApiResponseBuilder
from app.models.anomaly import Anomaly
from app.schemas.anomaly import (
    AnomalyCreate,
    AnomalyDetectionConfig,
    AnomalyQuery,
    AnomalyResponse,
    AnomalyUpdate,
    TrendAnalysisRequest,
)

router = APIRouter(tags=[TAG_CHECKIN_MONITOR])


# ========== 异常记录管理 ==========


@router.post("", status_code=status.HTTP_201_CREATED)
def create_anomaly(
    anomaly_data: AnomalyCreate,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    创建异常记录

    一般由系统自动创建,也可手动创建异常记录
    """
    anomaly = service.create(anomaly_data)
    return ApiResponseBuilder.from_model(anomaly, AnomalyResponse, message="异常记录创建成功")


@router.post("/query")
def query_anomalies(
    query_params: AnomalyQuery,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    查询异常记录

    支持按类型、严重程度、状态、时间范围、设备筛选
    """
    anomalies = service.get_anomalies(query_params)
    return ApiResponseBuilder.from_model(anomalies, AnomalyResponse, message="获取异常记录成功")


@router.get("/statistics")
def get_anomaly_statistics(
    start_date: datetime,
    end_date: datetime,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取异常统计数据

    统计指定时间段内的异常数量、按类型分组、按严重程度分组等
    """
    statistics = service.get_anomaly_statistics(
        current_user.user_id, start_date, end_date
    )
    return ApiResponseBuilder.success(data=statistics, message="获取异常统计成功")


@router.put("/{anomaly_id}")
def update_anomaly(
    anomaly_id: int,
    update_data: AnomalyUpdate,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    更新异常记录

    更新异常状态、处理措施、解决时间等
    """
    anomaly = service.update_anomaly(anomaly_id, update_data)
    if not anomaly:
        raise NotFoundException("异常记录不存在")

    # 权限检查:只能更新自己的异常
    if anomaly.user_id != current_user.user_id:
        raise ForbiddenException("无权限操作")

    return ApiResponseBuilder.from_model(anomaly, AnomalyResponse, message="异常记录更新成功")


@router.patch("/{anomaly_id}/resolve")
def resolve_anomaly(
    anomaly_id: int,
    action_taken: str,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    标记异常为已解决

    记录处理措施并更新状态为已解决
    """
    update_data = AnomalyUpdate(
        status="resolved", action_taken=action_taken, resolved_at=datetime.utcnow()
    )

    anomaly = service.update_anomaly(anomaly_id, update_data)
    if not anomaly:
        raise NotFoundException("异常记录不存在")

    return ApiResponseBuilder.success(
        data={"anomaly_id": anomaly_id}, message="异常已标记为已解决"
    )


# ========== 趋势分析 ==========


@router.post("/trends/analyze")
def analyze_health_trend(
    request: TrendAnalysisRequest,
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
):
    """
    分析健康数据趋势

    计算指定时间段内某项指标的平均值、最大值、最小值、标准差和变化趋势
    """
    try:
        request.user_id = current_user.user_id
        trend = service.analyze_health_trend(request)

        if not trend:
            raise NotFoundException("未找到相关数据")

        return ApiResponseBuilder.success(data=trend, message="健康趋势分析成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))


@router.get("/trends/recent")
def get_recent_trends(
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
    metric_type: str = "heart_rate",
    period_type: str = "daily",
    days: int = 7,
):
    """
    获取最近的趋势分析

    快速获取最近N天的趋势分析数据
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()

    request = TrendAnalysisRequest(
        user_id=current_user.user_id,
        metric_type=metric_type,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
    )

    trend = service.analyze_health_trend(request)

    if not trend:
        raise NotFoundException("未找到趋势数据")

    return ApiResponseBuilder.success(data=trend, message="获取最近趋势成功")


# ========== 心脏健康分析 ==========


@router.get("/heart-health/analysis")
def analyze_heart_health(
    service: AnomalyServiceDep,
    current_user: CurrentUserDep,
    device_id: int = None,
):
    """
    心脏健康分析

    基于心率数据进行心脏健康评估,包括静息心率、心率变异性、心律不齐检测等
    """
    try:
        analysis = service.analyze_heart_health(current_user.user_id, device_id)
        return ApiResponseBuilder.success(data=analysis, message="心脏健康分析成功")
    except ValueError as e:
        raise ValidationException(detail=str(e))


# ========== 异常检测配置 ==========


@router.post("/config")
def set_anomaly_detection_config(
    config: AnomalyDetectionConfig,
    db: DbSession,
    current_user: CurrentUserDep,
):
    """
    设置异常检测配置

    自定义心率、血压、血氧等指标的阈值和告警规则
    """
    # 将配置保存到用户设置中(示例实现)
    # 实际应该保存到专门的配置表
    # user_config_key = f"anomaly_detection_config_{current_user.user_id}"

    # 简化实现:只返回配置信息
    # 实际应该保存到数据库
    return ApiResponseBuilder.success(data=config.dict(), message="异常检测配置已更新")


@router.get("/config")
def get_anomaly_detection_config(
    db: DbSession,
    current_user: CurrentUserDep,
):
    """
    获取异常检测配置

    返回当前的异常检测阈值和告警规则
    """
    # 简化实现:返回默认配置
    # 实际应该从数据库读取
    return ApiResponseBuilder.success(
        data={
            "user_id": current_user.user_id,
            "heart_rate_min": 50,
            "heart_rate_max": 110,
            "heart_rate_sudden_change_threshold": 30,
            "no_activity_threshold": 12,
            "enable_auto_sos": True,
            "enable_notification": True,
            "alert_cooldown_minutes": 30,
        },
        message="获取异常检测配置成功",
    )


# ========== 管理员接口 ==========


@router.get("/admin/all")
def get_all_anomalies(
    admin: CurrentAdminDep,  # 添加管理员权限检查
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    severity: str = None,
):
    """
    获取所有异常记录(管理员接口)

    支持筛选和分页
    """
    query = db.query(Anomaly)

    if status:
        query = query.filter(Anomaly.status == status)

    if severity:
        query = query.filter(Anomaly.severity == severity)

    anomalies = (
        query.order_by(desc(Anomaly.detected_at)).offset(skip).limit(limit).all()
    )

    return ApiResponseBuilder.success(
        data={
            "total": len(anomalies),
            "anomalies": [AnomalyResponse.from_orm(a) for a in anomalies],
        },
        message="获取所有异常记录成功",
    )


@router.get("/admin/pending-critical")
def get_pending_critical_anomalies(
    admin: CurrentAdminDep,  # 添加管理员权限检查
    db: DbSession,
):
    """
    获取待处理的危急异常(管理员接口)

    用于监控需要立即处理的危急异常
    """
    critical_anomalies = (
        db.query(Anomaly)
        .filter(Anomaly.severity == "critical", Anomaly.status == "pending")
        .order_by(desc(Anomaly.detected_at))
        .limit(20)
        .all()
    )

    return ApiResponseBuilder.success(
        data={
            "count": len(critical_anomalies),
            "anomalies": [AnomalyResponse.from_orm(a) for a in critical_anomalies],
        },
        message="获取危急异常成功",
    )


@router.post("/admin/{anomaly_id}/dismiss")
def dismiss_anomaly(
    admin: CurrentAdminDep,  # 添加管理员权限检查
    anomaly_id: int,
    reason: str,
    db: DbSession,
):
    """
    忽略异常(管理员接口)

    管理员可以忽略误报的异常
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise NotFoundException("异常记录不存在")

    anomaly.status = "dismissed"
    anomaly.action_taken = f"管理员忽略: {reason}"
    db.commit()

    return ApiResponseBuilder.success(data={"anomaly_id": anomaly_id}, message="异常已忽略")
