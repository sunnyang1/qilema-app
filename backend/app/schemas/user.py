"""
用户相关的Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from app.core.schemas import BaseSchema
from app.models.user import BloodTypeEnum, GenderEnum
from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    """用户注册"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    verify_code: Optional[str] = Field(None, description="验证码")


class UserLogin(BaseModel):
    """用户登录"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")


class UserResponse(BaseSchema):
    """用户响应（排除敏感字段）"""

    user_id: str
    phone: str
    nickname: Optional[str]
    gender: GenderEnum
    birth_date: Optional[datetime]
    blood_type: BloodTypeEnum
    height: Optional[int]
    weight: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_sign_in: Optional[datetime]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, user) -> "UserResponse":
        """从 User ORM 对象转换为 UserResponse"""
        return cls.model_validate(user)


class UserRegisterRequest(BaseModel):
    """用户注册请求（增强版）"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    verify_code: Optional[str] = Field(None, description="验证码")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度至少6位")
        if len(v) > 20:
            raise ValueError("密码长度最多20位")
        # 可以添加更多密码强度检查
        return v


class UserUpdate(BaseModel):
    """更新用户信息"""

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[GenderEnum] = Field(None, description="性别")
    birth_date: Optional[datetime] = Field(None, description="出生日期")
    blood_type: Optional[BloodTypeEnum] = Field(None, description="血型")
    height: Optional[int] = Field(None, ge=0, le=300, description="身高(cm)")
    weight: Optional[int] = Field(None, ge=0, le=500, description="体重(kg)")

    model_config = {"from_attributes": True}
