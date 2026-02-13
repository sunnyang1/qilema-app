"""
基础Schema抽象类

提供统一的 ORM 对象到 Pydantic Schema 的转换功能
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Type, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T', bound=BaseModel)
M = TypeVar('M')


class BaseSchema(BaseModel, ABC, Generic[T]):
    """
    Schema基类 - 提供统一的ORM对象转换功能

    所有Response Schema都应该继承此类并实现from_orm方法

    Usage:
        class UserResponse(BaseSchema[UserResponse]):
            user_id: str
            phone: str

            @classmethod
            def from_orm(cls, user: User) -> "UserResponse":
                return cls(
                    user_id=str(user.id),
                    phone=user.phone
                )
    """

    model_config = {"from_attributes": True}

    @classmethod
    @abstractmethod
    def from_orm(cls: Type[T], obj: M) -> T:
        """
        从ORM对象转换为Schema实例

        Args:
            obj: ORM对象（如 SQLAlchemy 模型实例）

        Returns:
            T: Schema实例

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现from_orm方法")

    @classmethod
    def from_orm_list(cls: Type[T], objects: List[M]) -> List[T]:
        """
        从ORM对象列表转换为Schema实例列表

        Args:
            objects: ORM对象列表

        Returns:
            List[T]: Schema实例列表
        """
        return [cls.from_orm(obj) for obj in objects]

    @classmethod
    def safe_from_orm(cls: Type[T], obj: Any, default: Any = None) -> Any:
        """
        安全地从ORM对象转换为Schema实例

        如果转换失败，返回默认值

        Args:
            obj: ORM对象
            default: 转换失败时的默认值

        Returns:
            Schema实例或默认值
        """
        try:
            if obj is None:
                return default
            return cls.from_orm(obj)
        except Exception:
            return default


class TimestampMixin(BaseModel):
    """
    时间戳混入类 - 提供标准的时间字段
    """

    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = {"from_attributes": True}


class PaginationResponse(BaseModel):
    """
    分页响应基类
    """

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码", ge=1)
    page_size: int = Field(..., description="每页记录数", ge=1, le=100)
    total_pages: int = Field(..., description="总页数", ge=1)


class ListResponse(Generic[T], BaseModel):
    """
    通用列表响应
    """

    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页记录数")


class SuccessResponse(BaseModel):
    """
    通用成功响应
    """

    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorResponse(BaseModel):
    """
    通用错误响应
    """

    success: bool = Field(False, description="是否成功")
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[dict] = Field(None, description="错误详情")
