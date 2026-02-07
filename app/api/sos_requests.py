"""
SOS紧急求助API路由
"""
from fastapi import APIRouter, Depends
from app.core.exceptions import ValidationException, NotFoundException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.sos_request import SOSRequest

router = APIRouter()


@router.post("/", summary="发起SOS求助")
async def create_sos(
    location: dict,
    message: Optional[str] = None,
    notify_contacts: bool = True,
    notify_120: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发起SOS紧急求助"""
    sos_request = SOSRequest(
        user_id=current_user.user_id,
        location=location,
        message=message,
        status="pending",
        notify_contacts=notify_contacts,
        notify_120=notify_120
    )
    db.add(sos_request)
    db.commit()
    db.refresh(sos_request)
    
    return {
        "message": "SOS求助已发送",
        "sos_id": sos_request.sos_id,
        "status": sos_request.status
    }


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
    
    return {
        "total": len(sos_requests),
        "sos_requests": sos_requests
    }


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

    return sos


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
    
    return {"message": "SOS求助已取消"}


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

    return {"message": "SOS求助已标记为解决"}
