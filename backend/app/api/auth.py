"""
认证API路由

使用 ApiResponseBuilder 统一构建响应
"""

import asyncio
import time
from collections import defaultdict
from typing import Dict

from app.core.database import get_db
from app.core.response_builder import ApiResponseBuilder
from app.core.security import create_access_token, get_current_user, verify_password
from app.models.user import User
from app.schemas.user import UserRegisterRequest
from app.services.user_service import UserService
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()

# 简单的内存速率限制器（生产环境应使用 Redis）
_login_attempts: Dict[str, list] = defaultdict(list)
_lock = asyncio.Lock()


async def check_rate_limit(
    identifier: str, max_attempts: int = 5, window_seconds: int = 60
) -> bool:
    """
    检查是否超过速率限制

    Args:
        identifier: 唯一标识符（如 IP 地址）
        max_attempts: 最大尝试次数
        window_seconds: 时间窗口（秒）

    Returns:
        bool: True 表示允许，False 表示超过限制
    """
    async with _lock:
        now = time.time()
        # 移除时间窗口外的记录
        _login_attempts[identifier] = [
            attempt_time
            for attempt_time in _login_attempts[identifier]
            if now - attempt_time < window_seconds
        ]
        # 检查是否超过限制
        if len(_login_attempts[identifier]) >= max_attempts:
            return False
        # 记录此次尝试
        _login_attempts[identifier].append(now)
        return True


@router.post("/login", summary="用户登录")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    用户登录（使用 OAuth2 密码流）

    速率限制：每个 IP 每分钟最多 5 次尝试
    """
    # 应用速率限制
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(client_ip, max_attempts=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录尝试过于频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )

    # 查找用户
    user = db.query(User).filter(User.phone == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.user_id})

    return ApiResponseBuilder.success(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.user_id,
                "phone": user.phone,
                "nickname": user.nickname,
                "gender": user.gender.value if user.gender else None,
                "blood_type": user.blood_type.value if user.blood_type else None,
                "height": user.height,
                "weight": user.weight,
            },
        },
        message="登录成功",
    )


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    return UserService(db)


@router.post("/register", summary="用户注册")
async def register(
    user_data: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
):
    """用户注册"""
    # UserRegisterRequest 已经通过 Pydantic 进行了字段验证
    # 包括：phone 格式、密码长度、name 必填等

    # 将 Pydantic 模型转换为字典传递给 UserService
    user_dict = user_data.model_dump()

    # 使用 UserService 创建用户
    try:
        user = service.create(user_dict)
        return ApiResponseBuilder.success(
            data={"user_id": user.user_id}, message="注册成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", summary="刷新访问令牌")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """刷新访问令牌"""
    # 创建新的访问令牌
    access_token = create_access_token(data={"sub": current_user.user_id})

    return ApiResponseBuilder.success(
        data={"access_token": access_token, "token_type": "bearer"},
        message="令牌刷新成功",
    )


@router.post("/logout", summary="用户登出")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，可以将令牌加入黑名单
    # 这里只是返回成功响应
    return ApiResponseBuilder.success(message="登出成功")


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    # 立即将 User 对象转换为字典，避免 FastAPI 序列化时出现循环引用
    user_dict = {
        "user_id": str(current_user.user_id),
        "phone": str(current_user.phone),
        "nickname": current_user.nickname,
        "gender": current_user.gender.value if current_user.gender else None,
        "blood_type": (
            current_user.blood_type.value if current_user.blood_type else None
        ),
        "height": current_user.height,
        "weight": current_user.weight,
        "birth_date": (
            current_user.birth_date.isoformat() if current_user.birth_date else None
        ),
        "created_at": (
            current_user.created_at.isoformat() if current_user.created_at else None
        ),
    }

    response_data = {
        "code": 200,
        "message": "success",
        "data": user_dict,
        "timestamp": int(time.time()),
    }
    return JSONResponse(
        content=response_data, media_type="application/json; charset=utf-8"
    )
