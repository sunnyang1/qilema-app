"""
Token相关的Schema
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token数据"""
    user_id: Optional[str] = None
