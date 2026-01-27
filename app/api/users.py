"""
用户API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User

router = APIRouter()


@router.post("/register", summary="用户注册")
async def register(user_data: dict, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.phone == user_data.get("phone")).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )
    
    # 创建用户
    user = User(
        phone=user_data.get("phone"),
        nickname=user_data.get("nickname"),
        password_hash=get_password_hash(user_data.get("password", "123456")),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "注册成功", "user_id": user.user_id}


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前登录用户信息"""
    return {
        "user_id": current_user.user_id,
        "phone": current_user.phone,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "created_at": current_user.created_at,
    }


@router.get("/{user_id}", summary="获取用户信息")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """根据用户ID获取用户信息"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "user_id": user.user_id,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "created_at": user.created_at,
    }


@router.put("/{user_id}", summary="更新用户信息")
async def update_user(
    user_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新允许的字段
    for field in ["nickname", "avatar", "email", "bio"]:
        if field in update_data:
            setattr(user, field, update_data[field])
    
    db.commit()
    db.refresh(user)
    
    return {"message": "更新成功"}
