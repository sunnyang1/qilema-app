"""
紧急联系人相关的Schema验证
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmergencyContactCreate(BaseModel):
    """创建紧急联系人"""
    user_id: str = Field(..., description="用户ID")
    contact_name: str = Field(..., min_length=1, max_length=50, description="联系人姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="联系电话")
    relationship: str = Field(..., max_length=20, description="关系")
    is_primary: bool = Field(False, description="是否主要联系人")
    priority: int = Field(0, ge=0, le=100, description="优先级")
    notes: Optional[str] = Field(None, max_length=200, description="备注")


class EmergencyContactUpdate(BaseModel):
    """更新紧急联系人"""
    contact_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=11, max_length=20)
    relationship: Optional[str] = Field(None, max_length=20)
    is_primary: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=200)


class EmergencyContactResponse(BaseModel):
    """紧急联系人响应"""
    id: int
    user_id: str
    contact_name: str
    phone: str
    relationship: str
    is_primary: int
    priority: int
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
