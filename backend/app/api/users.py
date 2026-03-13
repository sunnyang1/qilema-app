"""
用户API路由

使用 ApiResponseBuilder 统一构建响应
"""

from app.api.dependencies import get_user_service
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.response_builder import ApiResponseBuilder
from app.core.security import get_current_user
from app.models.user import User
from app.services.user_service import UserService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/register", summary="用户注册")
async def register(
    user_data: dict,
    service: UserService = Depends(get_user_service),
):
    """用户注册"""
    try:
        user = service.create(user_data)
        return ApiResponseBuilder.success(
            data={"user_id": user.user_id}, message="注册成功"
        )
    except ValueError as e:
        if "已注册" in str(e):
            raise UserAlreadyExistsException(phone=user_data.get("phone"))
        raise


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return ApiResponseBuilder.success(data=current_user.to_dict())


@router.get("/{user_id}", summary="获取用户信息")
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    """根据用户ID获取用户信息"""
    user = service.get_by_id(user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)

    return ApiResponseBuilder.success(data=user.to_dict())


@router.put("/{user_id}", summary="更新用户信息")
async def update_user(
    user_id: str,
    update_data: dict,
    service: UserService = Depends(get_user_service),
):
    """更新用户信息"""
    try:
        user = service.update(user_id, update_data)
        return ApiResponseBuilder.success(data=user.to_dict(), message="更新成功")
    except ValueError as e:
        if "不存在" in str(e):
            raise UserNotFoundException(user_id=user_id)
        raise
