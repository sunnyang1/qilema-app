"""
签到打卡API路由 (Phase 2 异步化)

使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
使用 AsyncSession + CheckInRepository 实现真正的异步数据库操作
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.api.dependencies import AsyncDbSession, CurrentUserDep
from app.api.openapi_tags import TAG_CHECKIN_MONITOR
from app.core.exceptions import AlreadyCheckedInException, ValidationException
from app.core.limiter import STANDARD_LIMIT, limiter
from app.core.message_queue import MessageQueue
from app.core.response_builder import ApiResponseBuilder
from app.repositories.checkin_repository import CheckInRepository
from app.schemas.checkin import CheckInCreate, CheckInDateQuery, CheckInResponse

router = APIRouter(tags=[TAG_CHECKIN_MONITOR])


@router.post("/")
@limiter.limit(STANDARD_LIMIT)
async def create_checkin(
    checkin_data: CheckInCreate,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """
    创建签到记录（真正异步）

    - **latitude**: 纬度(可选)
    - **longitude**: 经度(可选)
    - **checkin_method**: 签到方式(manual/auto)
    - **notes**: 备注信息
    """
    repo = CheckInRepository(db)

    # 检查今天是否已签到
    today_str = date.today().isoformat()
    existing = await repo.get_by_user_and_date(current_user.user_id, today_str)
    if existing:
        raise AlreadyCheckedInException(message="今日已签到")

    checkin = await repo.create(
        user_id=current_user.user_id,
        checkin_time=datetime.utcnow(),
        checkin_date=today_str,
        latitude=checkin_data.latitude,
        longitude=checkin_data.longitude,
        checkin_method=checkin_data.checkin_method or "manual",
        notes=checkin_data.notes,
    )
    await db.commit()

    return ApiResponseBuilder.from_model(checkin, CheckInResponse, message="签到成功")


@router.get("/history")
@limiter.limit(STANDARD_LIMIT)
async def get_checkin_history(
    current_user: CurrentUserDep,
    db: AsyncDbSession,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
):
    """
    获取用户签到历史记录（真正异步）

    - **days**: 查询天数(1-365)
    - **start_date**: 开始日期(可选)
    - **end_date**: 结束日期(可选)
    """
    repo = CheckInRepository(db)
    checkins = await repo.get_recent_by_user(current_user.user_id, days=days)
    return ApiResponseBuilder.from_model(checkins, CheckInResponse, message="获取签到历史成功")


@router.get("/stats")
@limiter.limit(STANDARD_LIMIT)
async def get_checkin_stats(
    current_user: CurrentUserDep,
    db: AsyncDbSession,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
):
    """
    获取用户签到统计信息（真正异步）

    - **days**: 统计天数(1-365)

    返回信息包括:
    - total_checkins: 总签到次数
    - current_streak: 当前连续签到天数
    - longest_streak: 最长连续签到天数
    - checkin_rate: 签到率(%)
    """
    repo = CheckInRepository(db)
    total = await repo.count_by_user(current_user.user_id, days=days)
    streak = await repo.get_streak(current_user.user_id)

    stats = {
        "total_checkins": total,
        "current_streak": streak,
        "longest_streak": streak,  # TODO: 计算历史最长
        "checkin_rate": round(total / days * 100, 2),
    }
    return ApiResponseBuilder.success(data=stats, message="获取签到统计成功")


@router.post("/status")
@limiter.limit(STANDARD_LIMIT)
async def get_checkin_status(
    query: CheckInDateQuery,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """
    查询指定日期的签到状态（真正异步）

    - **date**: 日期(YYYY-MM-DD)

    返回:
    - is_checked_in: 是否已签到
    - checkin_time: 签到时间(如果已签到)
    """
    try:
        target_date = date.fromisoformat(query.date)
        repo = CheckInRepository(db)
        checkin = await repo.get_by_user_and_date(
            current_user.user_id, target_date.isoformat()
        )

        status = {
            "is_checked_in": checkin is not None,
            "checkin_time": checkin.checkin_time.isoformat() if checkin else None,
        }
        return ApiResponseBuilder.success(data=status, message="获取签到状态成功")
    except ValueError as e:
        raise ValidationException(message=f"日期格式错误: {str(e)}")


@router.get("/today")
@limiter.limit(STANDARD_LIMIT)
async def get_today_checkin_status(
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """
    获取今天的签到状态（真正异步）

    返回:
    - is_checked_in: 今天是否已签到
    - checkin_time: 签到时间(如果已签到)
    """
    repo = CheckInRepository(db)
    checkin = await repo.get_by_user_and_date(
        current_user.user_id, date.today().isoformat()
    )

    status = {
        "is_checked_in": checkin is not None,
        "checkin_time": checkin.checkin_time.isoformat() if checkin else None,
    }
    return ApiResponseBuilder.success(data=status, message="获取今日签到状态成功")
