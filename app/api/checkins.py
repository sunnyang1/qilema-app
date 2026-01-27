"""
签到API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.checkin import CheckIn

router = APIRouter()


@router.post("/", summary="签到")
async def create_checkin(
    location: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """完成签到"""
    # 检查今天是否已签到
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_checkin = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.user_id,
        CheckIn.created_at >= today_start
    ).first()
    
    if existing_checkin:
        return {
            "message": "今日已签到",
            "checkin_time": existing_checkin.created_at,
            "status": "already_checked_in"
        }
    
    # 创建签到记录
    checkin = CheckIn(
        user_id=current_user.user_id,
        location=location,
        status="completed"
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    
    return {
        "message": "签到成功",
        "checkin_time": checkin.created_at,
        "status": "success"
    }


@router.get("/", summary="获取签到记录")
async def get_checkins(
    skip: int = 0,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户签到记录"""
    checkins = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.user_id
    ).order_by(CheckIn.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": len(checkins),
        "checkins": checkins
    }


@router.get("/stats", summary="获取签到统计")
async def get_checkin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到统计数据"""
    # 获取最近30天的签到记录
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_checkins = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.user_id,
        CheckIn.created_at >= thirty_days_ago
    ).all()
    
    # 获取最后签到时间
    last_checkin = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.user_id
    ).order_by(CheckIn.created_at.desc()).first()
    
    return {
        "total_checkins": len(recent_checkins),
        "last_checkin_time": last_checkin.created_at if last_checkin else None,
        "checkin_rate": f"{len(recent_checkins)/30*100:.1f}%"
    }


@router.get("/{checkin_id}", summary="获取签到详情")
async def get_checkin(
    checkin_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到详情"""
    checkin = db.query(CheckIn).filter(
        CheckIn.checkin_id == checkin_id,
        CheckIn.user_id == current_user.user_id
    ).first()
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="签到记录不存在"
        )
    
    return checkin
