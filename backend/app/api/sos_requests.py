"""
SOS紧急求助API路由

使用 ApiResponseBuilder 统一构建响应
"""
from fastapi import APIRouter, Depends
from app.core.exceptions import ValidationException, NotFoundException
from app.core.response_builder import ApiResponseBuilder
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.sos_request import SOSRequest

router = APIRouter(tags=["SOS紧急求助"])


@router.post("/", summary="发起SOS求助")
async def create_sos(
    latitude: float,
    longitude: float,
    address: Optional[str] = None,
    emergency_reason: Optional[str] = None,
    call_120: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发起SOS紧急求助"""
    sos_request = SOSRequest(
        user_id=current_user.user_id,
        latitude=latitude,
        longitude=longitude,
        address=address,
        emergency_reason=emergency_reason,
        call_120=call_120,
        status="pending"
    )
    db.add(sos_request)
    db.commit()
    db.refresh(sos_request)

    return ApiResponseBuilder.success(
        data={"sos_id": sos_request.id, "status": sos_request.status},
        message="SOS求助已发送"
    )


@router.get("/", summary="获取SOS记录")
async def get_sos_requests(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户SOS求助记录"""
    sos_requests = db.query(SOSRequest).filter(
        SOSRequest.user_id == current_user.user_id
    ).order_by(SOSRequest.created_at.desc()).offset(skip).limit(limit).all()

    return ApiResponseBuilder.success(
        data={"total": len(sos_requests), "sos_requests": sos_requests},
        message="获取SOS记录成功"
    )


@router.get("/{sos_id}", summary="获取SOS详情")
async def get_sos(
    sos_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取SOS求助详情"""
    sos = db.query(SOSRequest).filter(
        SOSRequest.sos_id == sos_id,
        SOSRequest.user_id == current_user.user_id
    ).first()

    if not sos:
        raise NotFoundException("SOS记录不存在")

    return ApiResponseBuilder.success(data=sos, message="获取SOS详情成功")


@router.put("/{sos_id}/cancel", summary="取消SOS求助")
async def cancel_sos(
    sos_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消SOS求助"""
    sos = db.query(SOSRequest).filter(
        SOSRequest.sos_id == sos_id,
        SOSRequest.user_id == current_user.user_id
    ).first()

    if not sos:
        raise NotFoundException("SOS记录不存在")

    if sos.status != "pending":
        raise ValidationException("只能取消待处理的SOS求助")

    sos.status = "cancelled"
    db.commit()

    return ApiResponseBuilder.success(message="SOS求助已取消")


@router.put("/{sos_id}/resolve", summary="解决SOS求助")
async def resolve_sos(
    sos_id: str,
    resolution: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记SOS求助已解决"""
    sos = db.query(SOSRequest).filter(
        SOSRequest.sos_id == sos_id,
        SOSRequest.user_id == current_user.user_id
    ).first()

    if not sos:
        raise NotFoundException("SOS记录不存在")

    sos.status = "resolved"
    sos.resolution = resolution
    db.commit()

    return ApiResponseBuilder.success(message="SOS求助已标记为解决")
