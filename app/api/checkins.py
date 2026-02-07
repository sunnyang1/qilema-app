"""
签到打卡API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.exceptions import (
    AlreadyCheckedInException,
    ValidationException
)
from app.models.user import User
from app.schemas.checkin import (
    CheckInCreate,
    CheckInResponse,
    CheckInHistoryResponse,
    CheckInStatsResponse,
    CheckInStatusResponse,
    CheckInDateQuery
)
from app.services.checkin_service import CheckInService


router = APIRouter(prefix="/checkins", tags=["签到打卡"])


@router.post("/", response_model=CheckInResponse)
async def create_checkin(
    checkin_data: CheckInCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建签到记录

    - **latitude**: 纬度(可选)
    - **longitude**: 经度(可选)
    - **checkin_method**: 签到方式(manual/auto)
    - **notes**: 备注信息
    """
    try:
        checkin = CheckInService.create_checkin(db, current_user.user_id, checkin_data)

        # TODO: 发送签到成功通知给紧急联系人
        # await send_checkin_notification(current_user.user_id, checkin)

        return CheckInResponse(
            id=checkin.id,
            user_id=checkin.user_id,
            checkin_time=checkin.checkin_time,
            checkin_date=checkin.checkin_date,
            latitude=checkin.latitude,
            longitude=checkin.longitude,
            checkin_method=checkin.checkin_method,
            notes=checkin.notes
        )
    except ValueError as e:
        if "已签到" in str(e):
            raise AlreadyCheckedInException(message=str(e))
        raise ValidationException(message=str(e))


@router.get("/history", response_model=CheckInHistoryResponse)
async def get_checkin_history(
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户签到历史记录

    - **days**: 查询天数(1-365)
    - **start_date**: 开始日期(可选)
    - **end_date**: 结束日期(可选)
    """
    try:
        # 转换日期字符串
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        checkins = CheckInService.get_user_checkins(
            db,
            current_user.user_id,
            days=days,
            start_date=start,
            end_date=end
        )

        return CheckInHistoryResponse(
            total_count=len(checkins),
            checkins=[
                CheckInResponse(
                    id=c.id,
                    user_id=c.user_id,
                    checkin_time=c.checkin_time,
                    checkin_date=c.checkin_date,
                    latitude=c.latitude,
                    longitude=c.longitude,
                    checkin_method=c.checkin_method,
                    notes=c.notes
                ) for c in checkins
            ]
        )
    except ValueError as e:
        raise ValidationException(message=f"日期格式错误: {str(e)}")


@router.get("/stats", response_model=CheckInStatsResponse)
async def get_checkin_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户签到统计信息

    - **days**: 统计天数(1-365)

    返回信息包括:
    - total_checkins: 总签到次数
    - current_streak: 当前连续签到天数
    - longest_streak: 最长连续签到天数
    - checkin_rate: 签到率(%)
    """
    stats = CheckInService.get_checkin_stats(db, current_user.user_id, days)
    return stats


@router.post("/status", response_model=CheckInStatusResponse)
async def get_checkin_status(
    query: CheckInDateQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询指定日期的签到状态

    - **date**: 日期(YYYY-MM-DD)

    返回:
    - is_checked_in: 是否已签到
    - checkin_time: 签到时间(如果已签到)
    """
    try:
        target_date = date.fromisoformat(query.date)
        status = CheckInService.get_checkin_status(db, current_user.user_id, target_date)
        return status
    except ValueError as e:
        raise ValidationException(message=f"日期格式错误: {str(e)}")


@router.get("/today", response_model=CheckInStatusResponse)
async def get_today_checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取今天的签到状态

    返回:
    - is_checked_in: 今天是否已签到
    - checkin_time: 签到时间(如果已签到)
    """
    status = CheckInService.get_checkin_status(db, current_user.user_id)
    return status
