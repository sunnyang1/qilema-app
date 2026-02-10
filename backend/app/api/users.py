"""
用户API路由

使用 ApiResponseBuilder 统一构建响应
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException
)
from app.core.response_builder import ApiResponseBuilder
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", summary="用户注册")
async def register(user_data: dict, db: Session = Depends(get_db)):
    """用户注册"""
    # 使用 UserService 创建用户
    try:
        user = UserService.create_user(db, user_data)
        return ApiResponseBuilder.success(
            data={"user_id": user.user_id},
            message="注册成功"
        )
    except ValueError as e:
        raise UserAlreadyExistsException(phone=user_data.get("phone"))


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前登录用户信息"""
    return ApiResponseBuilder.success(data=current_user.to_dict())


@router.get("/{user_id}", summary="获取用户信息")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """根据用户ID获取用户信息"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)

    return ApiResponseBuilder.success(data=user.to_dict())


@router.put("/{user_id}", summary="更新用户信息")
async def update_user(
    user_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    try:
        user = UserService.update_user(db, user_id, update_data)
        return ApiResponseBuilder.success(
            data=user.to_dict(),
            message="更新成功"
        )
    except ValueError:
        raise UserNotFoundException(user_id=user_id)
