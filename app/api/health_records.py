"""
健康档案API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.health_record import HealthRecord

router = APIRouter()


@router.post("/", summary="创建健康档案")
async def create_health_record(
    record_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建健康档案"""
    health_record = HealthRecord(
        user_id=current_user.user_id,
        **record_data
    )
    db.add(health_record)
    db.commit()
    db.refresh(health_record)
    
    return {
        "message": "健康档案创建成功",
        "record_id": health_record.record_id
    }


@router.get("/", summary="获取健康档案列表")
async def get_health_records(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户健康档案列表"""
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.user_id
    ).order_by(HealthRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": len(records),
        "health_records": records
    }


@router.get("/{record_id}", summary="获取健康档案详情")
async def get_health_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取健康档案详情"""
    record = db.query(HealthRecord).filter(
        HealthRecord.record_id == record_id,
        HealthRecord.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康档案不存在"
        )
    
    return record


@router.put("/{record_id}", summary="更新健康档案")
async def update_health_record(
    record_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新健康档案"""
    record = db.query(HealthRecord).filter(
        HealthRecord.record_id == record_id,
        HealthRecord.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康档案不存在"
        )
    
    # 更新允许的字段
    for field in ["medical_history", "medications", "allergies", "blood_type", "emergency_notes"]:
        if field in update_data:
            setattr(record, field, update_data[field])
    
    db.commit()
    db.refresh(record)
    
    return {"message": "健康档案更新成功"}


@router.delete("/{record_id}", summary="删除健康档案")
async def delete_health_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除健康档案"""
    record = db.query(HealthRecord).filter(
        HealthRecord.record_id == record_id,
        HealthRecord.user_id == current_user.user_id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="健康档案不存在"
        )
    
    db.delete(record)
    db.commit()
    
    return {"message": "健康档案删除成功"}
