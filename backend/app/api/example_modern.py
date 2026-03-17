"""
FastAPI 0.135.x + SQLAlchemy 2.x 现代化 API 示例

展示如何正确使用：
1. Annotated[..., Depends(...)] 模式
2. SQLAlchemy 2.x 风格的模型定义
"""

from typing import Annotated, List, Optional

from app.api.dependencies import (
    DbSession,
    UserServiceDep,
)
from app.schemas.user import UserResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/example", tags=["示例"])


# ========== Pydantic v2 Schema 示例 ==========


class UserCreateRequest(BaseModel):
    """创建用户请求 (Pydantic v2 风格)"""
    
    phone: str = Field(
        ..., 
        pattern=r"^1[3-9]\d{9}$",  # Pydantic v2: regex -> pattern
        description="手机号",
        examples=["13800138000"]  # Pydantic v2: example -> examples
    )
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=20, 
        description="密码"
    )
    nickname: Optional[str] = Field(
        None, 
        max_length=50, 
        description="昵称"
    )
    
    # Pydantic v2: Config 类改为 model_config
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone": "13800138000",
                "password": "secure_password",
                "nickname": "张三"
            }
        }
    }


class UserListResponse(BaseModel):
    """用户列表响应"""
    
    items: List[UserResponse]
    total: int
    page: int
    per_page: int
    
    model_config = {"from_attributes": True}  # Pydantic v2: orm_mode -> from_attributes


# ========== FastAPI 0.135.x 路由示例 ==========


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="获取用户列表 (Annotated 模式示例)",
)
async def list_users(
    # 使用 Annotated[..., Depends(...)] 模式 - FastAPI 0.135.x 推荐
    db: DbSession,
    user_service: UserServiceDep,
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
    keyword: Annotated[Optional[str], Query(description="搜索关键词")] = None,
):
    """
    获取用户列表 - 展示 Annotated[..., Depends(...)] 模式
    
    Args:
        db: 数据库会话（通过 Annotated 依赖注入）
        user_service: 用户服务（通过 Annotated 依赖注入）
        page: 页码
        per_page: 每页数量
        keyword: 搜索关键词
    
    Returns:
        UserListResponse: 用户列表响应
    """
    # 使用 BaseService 的分页方法
    pagination = user_service.paginated_list(
        db=db,
        page=page,
        per_page=per_page,
        order_by="created_at",
        order_desc=True,
    )
    
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in pagination.items],
        total=pagination.total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="获取单个用户 (Annotated 模式示例)",
)
async def get_user(
    user_id: Annotated[str, Field(description="用户ID")],
    db: DbSession,
    user_service: UserServiceDep,
):
    """
    获取单个用户信息
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        user_service: 用户服务
    
    Returns:
        UserResponse: 用户详情
    """
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # Pydantic v2: from_orm -> model_validate
    return UserResponse.model_validate(user)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    summary="创建用户 (Annotated 模式示例)",
)
async def create_user(
    request: UserCreateRequest,
    db: DbSession,
    user_service: UserServiceDep,
):
    """
    创建新用户
    
    Args:
        request: 创建用户请求
        db: 数据库会话
        user_service: 用户服务
    
    Returns:
        UserResponse: 创建的用户
    """
    # 检查手机号是否已存在
    existing = user_service.get_by_phone(db, request.phone)
    if existing:
        raise HTTPException(status_code=400, detail="手机号已存在")
    
    # 创建用户
    user = user_service.create_user(
        db=db,
        phone=request.phone,
        password=request.password,
        nickname=request.nickname,
    )
    
    return UserResponse.model_validate(user)


# ========== 传统模式 vs 新模式的对比 ==========

# 传统模式（仍然支持但不推荐）:
# @router.get("/users-old")
# async def list_users_old(
#     db: Session = Depends(get_db),
#     page: int = Query(1, ge=1),
# ):
#     ...

# 新模式（FastAPI 0.135.x 推荐）:
# @router.get("/users-new")
# async def list_users_new(
#     db: Annotated[Session, Depends(get_db)],
#     page: Annotated[int, Query(ge=1)] = 1,
# ):
#     ...

# 使用预定义的 Annotated 类型（最简洁）:
# @router.get("/users-best")
# async def list_users_best(
#     db: DbSession,  # 即 Annotated[Session, Depends(get_db)]
#     page: Annotated[int, Query(ge=1)] = 1,
# ):
#     ...
