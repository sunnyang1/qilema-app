"""
设备管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.device import Device

router = APIRouter()


@router.post("/", summary="绑定设备")
async def create_device(
    device_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """绑定智能设备"""
    # 检查设备是否已被绑定
    existing_device = db.query(Device).filter(
        Device.device_id == device_data.get("device_id")
    ).first()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该设备已被绑定"
        )
    
    device = Device(
        user_id=current_user.user_id,
        **device_data
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return {
        "message": "设备绑定成功",
        "device": device
    }


@router.get("/", summary="获取设备列表")
async def get_devices(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户设备列表"""
    devices = db.query(Device).filter(
        Device.user_id == current_user.user_id
    ).order_by(Device.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": len(devices),
        "devices": devices
    }


@router.get("/{device_id}", summary="获取设备详情")
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取设备详情"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == current_user.user_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    return device


@router.put("/{device_id}", summary="更新设备信息")
async def update_device(
    device_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新设备信息"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == current_user.user_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 更新允许的字段
    for field in ["device_name", "device_type", "firmware_version", "status", "settings"]:
        if field in update_data:
            setattr(device, field, update_data[field])
    
    db.commit()
    db.refresh(device)
    
    return {"message": "设备信息更新成功"}


@router.delete("/{device_id}", summary="解绑设备")
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解绑设备"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == current_user.user_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    db.delete(device)
    db.commit()
    
    return {"message": "设备解绑成功"}


@router.post("/{device_id}/sync", summary="同步设备数据")
async def sync_device_data(
    device_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """同步设备数据"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == current_user.user_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 更新设备状态和数据
    device.last_sync_time = datetime.now()
    device.data = data
    
    db.commit()
    db.refresh(device)
    
    return {
        "message": "设备数据同步成功",
        "last_sync_time": device.last_sync_time
    }
