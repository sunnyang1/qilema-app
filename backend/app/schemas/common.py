"""
通用响应Schema模块

定义API统一响应格式和响应工具函数
"""

from typing import Optional, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

# 泛型类型变量
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应模型

    所有API端点都应该返回这种格式，包括成功和失败响应。

    Attributes:
        code: 响应码（成功为200，错误为具体错误码）
        message: 响应消息
        data: 响应数据（成功时包含）
        timestamp: Unix时间戳
    """
    code: int = Field(
        default=200,
        description="响应码，200表示成功，其他值表示错误"
    )
    message: str = Field(
        default="success",
        description="响应消息"
    )
    data: Optional[T] = Field(
        default=None,
        description="响应数据，成功时包含"
    )
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="Unix时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {"id": 1, "name": "测试数据"},
                "timestamp": 1706534400
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型

    专门用于错误响应的格式化

    Attributes:
        code: 错误码（业务错误码或HTTP状态码）
        message: 错误消息
        detail: 详细错误信息（可选）
        timestamp: Unix时间戳
    """
    code: int = Field(
        description="错误码"
    )
    message: str = Field(
        description="错误消息"
    )
    detail: Optional[str] = Field(
        default=None,
        description="详细错误信息"
    )
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="Unix时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": 1001,
                "message": "该手机号已注册",
                "detail": None,
                "timestamp": 1706534400
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应模型（简化版）

    只包含成功状态的响应格式

    Attributes:
        message: 成功消息
        data: 响应数据（可选）
        timestamp: Unix时间戳
    """
    message: str = Field(
        default="success",
        description="成功消息"
    )
    data: Optional[T] = Field(
        default=None,
        description="响应数据"
    )
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="Unix时间戳"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功",
                "data": {"id": 1, "name": "测试数据"},
                "timestamp": 1706534400
            }
        }


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应模型

    用于返回分页数据

    Attributes:
        code: 响应码
        message: 响应消息
        data: 分页数据
            items: 数据列表
            total: 总数量
            page: 当前页码
            page_size: 每页大小
            total_pages: 总页数
        timestamp: Unix时间戳
    """
    code: int = 200
    message: str = "success"
    data: dict
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp())
    )


# ========== 响应构建工具函数 ==========

def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200
) -> dict:
    """构建成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 响应码（默认200）

    Returns:
        dict: 统一格式的成功响应
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp())
    }


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "success"
) -> dict:
    """构建分页响应

    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息

    Returns:
        dict: 统一格式的分页响应
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        },
        "timestamp": int(datetime.now().timestamp())
    }


def error_response(
    code: int,
    message: str,
    detail: Any = None
) -> dict:
    """构建错误响应

    Args:
        code: 错误码
        message: 错误消息
        detail: 详细错误信息

    Returns:
        dict: 统一格式的错误响应
    """
    return {
        "code": code,
        "message": message,
        "detail": detail,
        "timestamp": int(datetime.now().timestamp())
    }
