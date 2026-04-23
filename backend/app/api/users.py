"""
用户API路由 (Phase 2 异步化)

使用 ApiResponseBuilder 统一构建响应
使用 Annotated 依赖注入模式 (FastAPI 0.135.x)
使用 AsyncSession + UserRepository 实现真正的异步数据库操作
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import AsyncDbSession, CurrentUserDep
from app.api.openapi_tags import TAG_USER_SETTINGS
from app.core.config import settings
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.limiter import STANDARD_LIMIT, STRICT_LIMIT, limiter
from app.core.prometheus_metrics import BusinessMetrics
from app.core.response_builder import ApiResponseBuilder
from app.models.user import User
from app.repositories.user_repository import UserRepository
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
@limiter.limit(STRICT_LIMIT)
async def register(
    user_data: UserRegisterRequest,
    db: AsyncDbSession,
):
    """用户注册（真正异步）"""
    repo = UserRepository(db)

    # 检查邮箱或手机号是否已注册
    if user_data.email:
        existing = await repo.get_by_email(user_data.email)
        if existing:
            raise UserAlreadyExistsException(phone=user_data.phone)

    user = await repo.create(
        user_id=User.generate_user_id(),
        email=user_data.email,
        phone=user_data.phone,
        name=user_data.name,
        is_active=True,
    )
    await db.commit()

    # 记录业务指标
    BusinessMetrics.record_user_registration("success")

    return ApiResponseBuilder.success(data={"user_id": user.user_id}, message="注册成功")


@router.get("/me", summary="获取当前用户信息")
@limiter.limit(STANDARD_LIMIT)
async def get_user_me(current_user: CurrentUserDep):
    """获取当前登录用户信息"""
    return ApiResponseBuilder.success(data=current_user.to_dict())


@router.get("/{user_id}", summary="获取用户信息")
@limiter.limit(STANDARD_LIMIT)
async def get_user(
    user_id: str,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """根据用户ID获取用户信息（本人或管理员，真正异步）"""
    _require_self_or_admin(current_user, user_id)
    repo = UserRepository(db)
    user = await repo.get_by_user_id(user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)

    return ApiResponseBuilder.success(data=user.to_dict())


@router.put("/{user_id}", summary="更新用户信息")
@limiter.limit(STANDARD_LIMIT)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: CurrentUserDep,
    db: AsyncDbSession,
):
    """更新用户信息（本人或管理员，真正异步）"""
    _require_self_or_admin(current_user, user_id)
    repo = UserRepository(db)

    user = await repo.get_by_user_id(user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(user, field):
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return ApiResponseBuilder.success(data=user.to_dict(), message="更新成功")
