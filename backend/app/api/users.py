"""
用户API路由

使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUserDep, UserServiceDep
from app.api.openapi_tags import TAG_USER_SETTINGS
from app.core.config import settings
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.response_builder import ApiResponseBuilder
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserUpdate

router = APIRouter(tags=[TAG_USER_SETTINGS])


def _require_self_or_admin(current_user: User, target_user_id: str) -> None:
    if current_user.user_id == target_user_id:
        return
    if current_user.user_id in settings.ADMIN_USER_IDS:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权访问该用户",
    )


@router.post("/register", summary="用户注册")
async def register(
    user_data: UserRegisterRequest,
    service: UserServiceDep,
):
    """用户注册（与 /auth/register 使用相同校验模型）"""
    try:
        user = service.create(user_data.model_dump())
        return ApiResponseBuilder.success(
            data={"user_id": user.user_id}, message="注册成功"
        )
    except ValueError as e:
        if "已注册" in str(e):
            raise UserAlreadyExistsException(phone=user_data.phone)
        raise


@router.get("/me", summary="获取当前用户信息")
async def get_user_me(current_user: CurrentUserDep):
    """获取当前登录用户信息"""
    return ApiResponseBuilder.success(data=current_user.to_dict())


@router.get("/{user_id}", summary="获取用户信息")
async def get_user(
    user_id: str,
    current_user: CurrentUserDep,
    service: UserServiceDep,
):
    """根据用户ID获取用户信息（本人或管理员）"""
    _require_self_or_admin(current_user, user_id)
    user = service.get_by_id(user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)

    return ApiResponseBuilder.success(data=user.to_dict())


@router.put("/{user_id}", summary="更新用户信息")
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: CurrentUserDep,
    service: UserServiceDep,
):
    """更新用户信息（本人或管理员）"""
    _require_self_or_admin(current_user, user_id)
    try:
        user = service.update(user_id, update_data.model_dump(exclude_unset=True))
        return ApiResponseBuilder.success(data=user.to_dict(), message="更新成功")
    except ValueError as e:
        if "不存在" in str(e):
            raise UserNotFoundException(user_id=user_id)
        raise
