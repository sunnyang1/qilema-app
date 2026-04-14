"""
消息通知API路由

提供通知发送、查询、管理等RESTful接口
使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
"""

from datetime import datetime
from typing import Optional

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from fastapi import APIRouter, status

from app.api.dependencies import CurrentAdminDep, CurrentUserDep, NotificationServiceDep
from app.api.openapi_tags import TAG_NOTIFICATION
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from app.core.response_builder import ApiResponseBuilder
from app.schemas.notification import (
    BatchSendNotificationRequest,
    MarkAsReadRequest,
    NotificationPreferenceCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationQuery,
    NotificationResponse,
    NotificationStatistics,
    NotificationTemplateCreate,
    NotificationTemplateResponse,
    SendNotificationRequest,
)

router = APIRouter(tags=[TAG_NOTIFICATION])


# ========== 通知发送 ==========


@router.post("/send")
def send_notification(
    request: SendNotificationRequest,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    发送通知

    根据通知偏好设置,选择合适的通知渠道发送通知
    """
    # 验证用户ID是否为当前用户
    if request.user_id != current_user.user_id:
        raise ForbiddenException("无权发送给其他用户")

    notification = service.send_notification(request)
    if not notification:
        raise ValidationException("发送通知失败")

    return ApiResponseBuilder.from_model(
        notification, NotificationResponse, message="通知发送成功"
    )


@router.post("/batch-send")
def batch_send_notification(
    request: BatchSendNotificationRequest,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    批量发送通知

    向多个用户发送相同的通知
    """
    notifications = service.batch_send_notification(request)
    return ApiResponseBuilder.from_model(
        notifications, NotificationResponse, message="批量发送通知成功"
    )


# ========== 通知查询和管理 ==========


@router.get("/list")
def get_notifications(
    query_params: NotificationQuery,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    查询通知记录

    支持按类型、渠道、状态、时间范围、是否未读等条件筛选
    """
    # 验证用户ID是否为当前用户
    if query_params.user_id != current_user.user_id:
        raise ForbiddenException("无权查看其他用户的通知")

    notifications = service.get_notifications(query_params)
    return ApiResponseBuilder.from_model(
        notifications, NotificationResponse, message="获取通知列表成功"
    )


@router.post("/mark-as-read")
def mark_as_read(
    request: MarkAsReadRequest,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    标记通知为已读

    批量标记指定的通知为已读
    """
    # 验证通知所有权
    from app.models.notification_model import Notification

    notifications = (
        service.db.query(Notification)
        .filter(Notification.id.in_(request.notification_ids))
        .all()
    )

    for notification in notifications:
        if notification.user_id != current_user.user_id:
            raise ForbiddenException("无权标记其他用户的通知")

    count = service.mark_as_read(request.notification_ids)
    return ApiResponseBuilder.success(
        data={"count": count}, message=f"已标记 {count} 条通知为已读"
    )


@router.get("/unread-count")
def get_unread_count(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取未读通知数量
    """
    count = service.get_unread_count(current_user.user_id)
    return ApiResponseBuilder.success(
        data={"unread_count": count}, message="获取未读通知数量成功"
    )


@router.get("/statistics")
def get_notification_statistics(
    start_date: datetime,
    end_date: datetime,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取通知统计数据

    统计指定时间段内的通知发送、送达、阅读等数据
    """
    statistics = service.get_statistics(current_user.user_id, start_date, end_date)
    return ApiResponseBuilder.success(data=statistics, message="获取通知统计成功")


@router.get("/daily-statistics")
def get_daily_statistics(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    days: int = 7,
):
    """
    获取每日通知统计

    返回最近 N 天的通知统计数据
    """
    statistics = service.get_daily_statistics(current_user.user_id, days)
    return ApiResponseBuilder.success(data=statistics, message="获取每日统计成功")


@router.get("/channel-statistics")
def get_channel_statistics(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """
    获取各渠道通知统计

    统计各通知渠道的发送情况
    """
    statistics = service.get_channel_statistics(
        current_user.user_id, start_date, end_date
    )
    return ApiResponseBuilder.success(data=statistics, message="获取渠道统计成功")


# ========== 通知偏好管理 ==========


@router.post("/preferences", status_code=status.HTTP_201_CREATED)
def create_preference(
    preference_data: NotificationPreferenceCreate,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    创建通知偏好设置
    """
    # 验证用户ID是否为当前用户
    if preference_data.user_id != current_user.user_id:
        raise ForbiddenException("无权设置其他用户的偏好")

    preference = service.create_preference(preference_data)
    return ApiResponseBuilder.from_model(
        preference, NotificationPreferenceResponse, message="通知偏好创建成功"
    )


@router.get("/preferences")
def get_preference(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取通知偏好设置
    """
    preference = service.get_preference(current_user.user_id)
    if not preference:
        # 返回默认设置
        default_preference = NotificationPreferenceCreate(user_id=current_user.user_id)
        preference = service.create_preference(default_preference)

    return ApiResponseBuilder.from_model(
        preference, NotificationPreferenceResponse, message="获取通知偏好成功"
    )


@router.put("/preferences")
def update_preference(
    update_data: NotificationPreferenceUpdate,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    更新通知偏好设置
    """
    preference = service.update_preference(current_user.user_id, update_data)
    if not preference:
        raise NotFoundException("通知偏好设置不存在")

    return ApiResponseBuilder.from_model(
        preference, NotificationPreferenceResponse, message="通知偏好更新成功"
    )


# ========== 通知模板管理 ==========


@router.post("/templates", status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: NotificationTemplateCreate,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    创建通知模板

    一般由系统管理员创建
    """
    template = service.create_template(template_data)
    return ApiResponseBuilder.from_model(
        template, NotificationTemplateResponse, message="通知模板创建成功"
    )


@router.get("/templates/{template_code}")
def get_template(
    template_code: str,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取通知模板
    """
    template = service.get_template(template_code)
    if not template:
        raise NotFoundException("通知模板不存在")

    return ApiResponseBuilder.from_model(
        template, NotificationTemplateResponse, message="获取通知模板成功"
    )


@router.get("/templates")
def list_templates(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    notification_type: Optional[str] = None,
    channel: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """
    列出通知模板

    支持按类型、渠道、是否激活筛选
    """
    templates = service.list_templates(notification_type, channel, is_active)
    return ApiResponseBuilder.success(data=templates, message="获取模板列表成功")


@router.post("/templates/{template_code}/render")
def render_template(
    template_code: str,
    data: dict,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    渲染通知模板

    使用提供的变量数据渲染模板
    """
    rendered = service.render_template(template_code, data)
    if not rendered:
        raise NotFoundException("通知模板不存在")

    return ApiResponseBuilder.success(data=rendered, message="模板渲染成功")


# ========== 熔断器管理 ==========


@router.get("/circuit-breaker/{channel}")
def get_circuit_breaker_state(
    channel: str,
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
):
    """
    获取熔断器状态

    查看指定通知渠道的熔断器状态
    """
    state = service.get_circuit_breaker_state(channel)
    return ApiResponseBuilder.success(data=state, message="获取熔断器状态成功")


@router.post("/circuit-breaker/reset")
def reset_circuit_breaker(
    service: NotificationServiceDep,
    current_user: CurrentUserDep,
    channel: Optional[str] = None,
):
    """
    重置熔断器

    重置指定渠道或所有渠道的熔断器状态
    """
    service.reset_circuit_breaker(channel)
    message = f"熔断器已重置（渠道: {channel}）" if channel else "所有熔断器已重置"
    return ApiResponseBuilder.success(message=message)


# ========== 管理员接口 ==========


@router.get("/admin/statistics")
def get_admin_statistics(
    admin: CurrentAdminDep,  # 添加管理员权限检查
    service: NotificationServiceDep,
    start_date: datetime,
    end_date: datetime,
    user_id: Optional[str] = None,
):
    """
    获取全局通知统计数据

    管理员接口,统计全局或指定用户的通知数据
    """
    if user_id:
        statistics = service.get_statistics(user_id, start_date, end_date)
    else:
        # 全局统计需要实现
        statistics = NotificationStatistics(
            user_id="",
            stat_date=start_date.strftime("%Y-%m-%d"),
            total_sent=0,
            total_delivered=0,
            total_read=0,
            total_failed=0,
            unread_count=0,
            checkin_count=0,
            alert_count=0,
            sos_count=0,
            system_count=0,
            health_count=0,
            device_count=0,
            reminder_count=0,
        )

    return ApiResponseBuilder.success(data=statistics, message="获取通知统计成功")
