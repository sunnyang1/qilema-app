"""
SOS紧急求助API路由 (Phase 2 异步化)

使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
使用 AsyncSession + Repository 模式实现真正的异步数据库操作
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter

from app.api.dependencies import AsyncDbSession, CurrentUserDep
from app.api.openapi_tags import TAG_SOS
from app.core.exceptions import NotFoundException, ValidationException
from app.core.limiter import SOS_LIMIT, STANDARD_LIMIT, limiter
from app.core.message_queue import MessageQueue
from app.core.response_builder import ApiResponseBuilder
from app.repositories.sos_repository import SOSRepository

router = APIRouter(tags=[TAG_SOS])


@router.post("/", summary="发起SOS求助")
@limiter.limit(SOS_LIMIT)
async def create_sos(
    latitude: float,
    longitude: float,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
    address: Optional[str] = None,
    emergency_reason: Optional[str] = None,
    call_120: bool = False,
):
    """发起SOS紧急求助（真正异步）"""
    repo = SOSRepository(db)

    sos_request = await repo.create(
        user_id=current_user.user_id,
        latitude=latitude,
        longitude=longitude,
        address=address,
        emergency_reason=emergency_reason,
        call_120=call_120,
        status="pending",
    )
    await db.commit()

    # Phase 3: 异步发布 SOS 触发事件，通知 Worker 处理
    # API 立即返回 200，通知发送由 Worker 异步执行
    queue = MessageQueue()
    await queue.publish(
        MessageQueue.STREAM_SOS,
        "sos.triggered",
        {
            "user_id": current_user.user_id,
            "sos_id": sos_request.id,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
            },
            "emergency_reason": emergency_reason,
            "call_120": call_120,
            "triggered_at": datetime.utcnow().isoformat(),
        },
    )

    return ApiResponseBuilder.success(
        data={"sos_id": sos_request.id, "status": sos_request.status},
        message="SOS求助已发送，通知正在处理中",
    )


@router.get("/", summary="获取SOS记录")
@limiter.limit(STANDARD_LIMIT)
async def get_sos_requests(
    current_user: CurrentUserDep,
    db: AsyncDbSession,
    skip: int = 0,
    limit: int = 50,
):
    """获取用户SOS求助记录（真正异步）"""
    repo = SOSRepository(db)
    sos_requests = await repo.get_by_user_id(
        user_id=current_user.user_id, skip=skip, limit=limit
    )

    return ApiResponseBuilder.success(
        data={"total": len(sos_requests), "sos_requests": sos_requests},
        message="获取SOS记录成功",
    )


@router.get("/{sos_id}", summary="获取SOS详情")
@limiter.limit(STANDARD_LIMIT)
async def get_sos(
    sos_id: str,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """获取SOS求助详情（真正异步）"""
    repo = SOSRepository(db)
    sos = await repo.get_by_sos_id_and_user(sos_id=sos_id, user_id=current_user.user_id)

    if not sos:
        raise NotFoundException("SOS记录不存在")

    return ApiResponseBuilder.success(data=sos, message="获取SOS详情成功")


@router.put("/{sos_id}/cancel", summary="取消SOS求助")
@limiter.limit(STANDARD_LIMIT)
async def cancel_sos(
    sos_id: str,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """取消SOS求助（真正异步）"""
    repo = SOSRepository(db)
    sos = await repo.get_by_sos_id_and_user(sos_id=sos_id, user_id=current_user.user_id)

    if not sos:
        raise NotFoundException("SOS记录不存在")

    if sos.status != "pending":
        raise ValidationException("只能取消待处理的SOS求助")

    await repo.update_status(sos.id, status="cancelled")
    await db.commit()

    return ApiResponseBuilder.success(message="SOS求助已取消")


@router.put("/{sos_id}/resolve", summary="解决SOS求助")
@limiter.limit(STANDARD_LIMIT)
async def resolve_sos(
    sos_id: str,
    resolution: dict,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """标记SOS求助已解决（真正异步）"""
    repo = SOSRepository(db)
    sos = await repo.get_by_sos_id_and_user(sos_id=sos_id, user_id=current_user.user_id)

    if not sos:
        raise NotFoundException("SOS记录不存在")

    await repo.update(sos.id, status="resolved", resolution=resolution)
    await db.commit()

    return ApiResponseBuilder.success(message="SOS求助已标记为解决")
