"""
消息通知API路由

提供通知发送、查询、管理等RESTful接口
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse, NotificationQuery, NotificationStatistics,
    SendNotificationRequest, BatchSendNotificationRequest, MarkAsReadRequest,
    NotificationPreferenceCreate, NotificationPreferenceResponse, NotificationPreferenceUpdate,
    NotificationTemplateCreate, NotificationTemplateResponse, NotificationTemplateUpdate,
    NotificationStatsQuery
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["消息通知"])
notification_service = NotificationService()


# ========== 通知发送 ==========

@router.post("/send", response_model=NotificationResponse)
def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发送通知
    
    根据通知偏好设置,选择合适的通知渠道发送通知
    """
    # 验证用户ID是否为当前用户
    if request.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权发送给其他用户")
    
    notification = notification_service.send_notification(db, request)
    if not notification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="发送通知失败")
    
    return notification


@router.post("/batch-send", response_model=List[NotificationResponse])
def batch_send_notification(
    request: BatchSendNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量发送通知
    
    向多个用户发送相同的通知
    """
    notifications = notification_service.batch_send_notification(db, request)
    return notifications


# ========== 通知查询和管理 ==========

@router.get("/list", response_model=List[NotificationResponse])
def get_notifications(
    query_params: NotificationQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    查询通知记录
    
    支持按类型、渠道、状态、时间范围、是否未读等条件筛选
    """
    # 验证用户ID是否为当前用户
    if query_params.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看其他用户的通知")
    
    notifications = notification_service.get_notifications(db, query_params)
    return notifications


@router.post("/mark-as-read")
def mark_as_read(
    request: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记通知为已读
    
    批量标记指定的通知为已读
    """
    # 验证通知所有权
    from app.models.notification import Notification
    notifications = db.query(Notification).filter(Notification.id.in_(request.notification_ids)).all()
    
    for notification in notifications:
        if notification.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权标记其他用户的通知")
    
    count = notification_service.mark_as_read(db, request.notification_ids)
    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取未读通知数量
    """
    count = notification_service.get_unread_count(db, current_user.user_id)
    return {"unread_count": count}


@router.get("/statistics")
def get_notification_statistics(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知统计数据
    
    统计指定时间段内的通知发送、送达、阅读等数据
    """
    statistics = notification_service.get_statistics(db, current_user.user_id, start_date, end_date)
    return statistics


# ========== 通知偏好管理 ==========

@router.post("/preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_preference(
    preference_data: NotificationPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建通知偏好设置
    """
    # 验证用户ID是否为当前用户
    if preference_data.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权设置其他用户的偏好")
    
    preference = notification_service.create_preference(db, preference_data)
    return preference


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_preference(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知偏好设置
    """
    preference = notification_service.get_preference(db, current_user.user_id)
    if not preference:
        # 返回默认设置
        from app.schemas.notification import NotificationPreferenceCreate
        default_preference = NotificationPreferenceCreate(user_id=current_user.user_id)
        preference = notification_service.create_preference(db, default_preference)
    
    return preference


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_preference(
    update_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新通知偏好设置
    """
    preference = notification_service.update_preference(db, current_user.user_id, update_data)
    if not preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知偏好设置不存在")
    
    return preference


# ========== 通知模板管理 ==========

@router.post("/templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建通知模板
    
    一般由系统管理员创建
    """
    template = notification_service.create_template(db, template_data)
    return template


@router.get("/templates/{template_code}", response_model=NotificationTemplateResponse)
def get_template(
    template_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知模板
    """
    template = notification_service.get_template(db, template_code)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知模板不存在")
    
    return template


# ========== 管理员接口 ==========

@router.get("/admin/statistics")
def get_admin_statistics(
    start_date: datetime,
    end_date: datetime,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """
    获取全局通知统计数据
    
    管理员接口,统计全局或指定用户的通知数据
    """
    # 验证管理员权限
    # 这里应该添加管理员权限验证逻辑
    if user_id:
        statistics = notification_service.get_statistics(db, user_id, start_date, end_date)
    else:
        # 全局统计需要实现
        from app.schemas.notification import NotificationStatistics as NotificationStatsSchema
        statistics = NotificationStatsSchema(
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
            reminder_count=0
        )
    
    return statistics
