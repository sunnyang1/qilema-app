"""
用户相关的Pydantic Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from app.core.schemas import BaseSchema


class UserRegister(BaseModel):
    """用户注册"""
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$', description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    verify_code: Optional[str] = Field(None, description="验证码")


class UserLogin(BaseModel):
    """用户登录"""
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$', description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")


class UserResponse(BaseSchema):
    """用户响应"""
    user_id: str
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    email: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, user) -> "UserResponse":
        """从User ORM对象转换为UserResponse"""
        return cls(
            user_id=str(user.id),
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            email=user.email,
            bio=user.bio,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    email: Optional[str] = Field(None, description="邮箱")
    bio: Optional[str] = Field(None, max_length=200, description="个人简介")

    model_config = {"from_attributes": True}
