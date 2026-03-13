"""
模型基类Mixin模块

提供统一的to_dict、from_dict、to_schema方法，统一所有模型的序列化行为
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel


class BaseModelMixin:
    """
    模型基类Mixin

    为所有SQLAlchemy模型提供统一的序列化和反序列化方法

    使用示例:
        >>> from app.models.base_mixin import BaseModelMixin
        >>>
        >>> class User(Base, BaseModelMixin):
        ...     __tablename__ = "users"
        ...     id = Column(Integer, primary_key=True)
        ...     name = Column(String(50))
        ...
        >>> user = User(name="张三")
        >>> user.to_dict()
        {'id': None, 'name': '张三'}
        >>>
        >>> # 排除敏感字段
        >>> user.to_dict(exclude=['password'])
        {'id': None, 'name': '张三'}
        >>>
        >>> # 转换为Pydantic Schema
        >>> schema = user.to_schema(UserSchema)
    """

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        将模型转换为字典

        自动处理以下类型:
        - datetime -> ISO格式字符串
        - date -> ISO格式字符串
        - Enum -> 枚举值
        - None -> None

        Args:
            exclude: 要排除的字段列表
            include: 只包含的字段列表（优先级高于exclude）

        Returns:
            Dict[str, Any]: 模型数据的字典表示
        """
        exclude = exclude or []

        # 默认排除的字段（SQLAlchemy内部属性）
        default_exclude = {"_sa_instance_state"}
        exclude_set = set(exclude) | default_exclude

        result = {}

        for key in dir(self):
            # 跳过私有属性和方法
            if key.startswith("_"):
                continue

            # 如果只包含指定字段
            if include is not None and key not in include:
                continue

            # 如果字段在排除列表中
            if key in exclude_set:
                continue

            # 获取属性值
            try:
                value = getattr(self, key)
            except AttributeError:
                continue

            # 跳过方法和类属性
            if callable(value):
                continue

            # 转换值
            result[key] = self._convert_value(value)

        return result

    def _convert_value(self, value: Any) -> Any:
        """
        转换值为可序列化的格式

        Args:
            value: 原始值

        Returns:
            Any: 转换后的值
        """
        if value is None:
            return None

        # 处理datetime
        if isinstance(value, datetime):
            return value.isoformat()

        # 处理date
        if isinstance(value, date) and not isinstance(value, datetime):
            return value.isoformat()

        # 处理Enum
        if isinstance(value, Enum):
            return value.value

        # 其他类型直接返回
        return value

    def to_schema(self, schema_class: Type[BaseModel]) -> BaseModel:
        """
        将模型转换为Pydantic Schema

        Args:
            schema_class: Pydantic Schema类

        Returns:
            BaseModel: Schema实例

        示例:
            >>> user = db.query(User).first()
            >>> user_schema = user.to_schema(UserResponseSchema)
        """
        data = self.to_dict()
        return schema_class.model_validate(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModelMixin":
        """
        从字典创建模型实例

        自动将ISO格式日期字符串转换为datetime/date对象

        Args:
            data: 包含模型数据的字典

        Returns:
            BaseModelMixin: 模型实例

        示例:
            >>> data = {"id": 1, "name": "张三", "created_at": "2024-01-15T10:30:00"}
            >>> user = User.from_dict(data)
        """
        instance = cls.__new__(cls)

        for key, value in data.items():
            # 尝试将ISO格式日期字符串转换为datetime/date
            converted_value = cls._parse_datetime_value(value)
            setattr(instance, key, converted_value)

        return instance

    @staticmethod
    def _parse_datetime_value(value: Any) -> Any:
        """
        解析可能的日期时间字符串

        Args:
            value: 原始值

        Returns:
            Any: 解析后的值或原始值
        """
        if not isinstance(value, str):
            return value

        # 尝试解析datetime格式 (2024-01-15T10:30:00 或 2024-01-15T10:30:00+00:00)
        datetime_formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]

        for fmt in datetime_formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # 尝试解析date格式 (2024-01-15)
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass

        # 无法解析，返回原始值
        return value


# 为了保持向后兼容，提供一个简化的函数版本
def model_to_dict(
    model: Any, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    将任意模型转换为字典（工具函数）

    Args:
        model: 模型实例
        exclude: 要排除的字段
        include: 只包含的字段

    Returns:
        Dict[str, Any]: 字典表示
    """
    if hasattr(model, "to_dict") and callable(getattr(model, "to_dict")):
        return model.to_dict(exclude=exclude, include=include)

    # 对于没有to_dict方法的对象，尝试直接读取属性
    result = {}
    exclude_set = set(exclude or [])

    for key in dir(model):
        if key.startswith("_"):
            continue
        if include is not None and key not in include:
            continue
        if key in exclude_set:
            continue

        try:
            value = getattr(model, key)
            if not callable(value):
                result[key] = value
        except AttributeError:
            continue

    return result
