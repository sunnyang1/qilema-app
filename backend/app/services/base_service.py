"""
服务基类

提供通用的CRUD操作和缓存管理机制
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from app.core.cache import cache_result, get_cached, invalidate_cache
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    服务基类

    提供通用的CRUD操作和缓存管理
    子类需要设置 model_class 类属性
    """

    model_class: Type[ModelType] = None
    cache_prefix: str = ""
    cache_ttl: int = 300  # 默认缓存5分钟

    @classmethod
    def get_by_id(
        cls, db: Session, id_value: Any, pk_column: str = "id"
    ) -> Optional[ModelType]:
        """
        根据ID获取记录

        缓存策略说明:
        - 使用字典形式缓存模型数据
        - 不尝试重建SQLAlchemy对象（不可靠且复杂）
        - 缓存命中时从数据库重新查询对象（利用SQLAlchemy的identity map优化）
        - 缓存失效时直接从数据库查询

        Args:
            db: 数据库会话
            id_value: ID值
            pk_column: 主键列名，默认为"id"

        Returns:
            记录对象或None
        """
        if not id_value:
            return None

        cache_key = f"{cls.cache_prefix}:{pk_column}:{id_value}"

        # 检查缓存（仅用于判断数据是否存在，不尝试重建对象）
        cached_data = get_cached(cache_key)
        cache_exists = cached_data is not None

        # 查询数据库
        query = db.query(cls.model_class)
        if hasattr(cls.model_class, pk_column):
            query = query.filter(getattr(cls.model_class, pk_column) == id_value)
        else:
            return None

        result = query.first()

        # 更新缓存
        if result:
            if hasattr(result, "to_dict"):
                cache_result(cache_key, result.to_dict(), ttl=cls.cache_ttl)
        else:
            # 数据库中没有但缓存中有，清除缓存
            if cache_exists:
                invalidate_cache(cache_key)

        return result

    @classmethod
    def get_by_field(
        cls, db: Session, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """
        根据字段值获取单条记录

        Args:
            db: 数据库会话
            field_name: 字段名
            field_value: 字段值

        Returns:
            记录对象或None
        """
        if not hasattr(cls.model_class, field_name):
            return None

        return (
            db.query(cls.model_class)
            .filter(getattr(cls.model_class, field_name) == field_value)
            .first()
        )

    @classmethod
    def list_records(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_desc: bool = True,
        **filters,
    ) -> List[ModelType]:
        """
        获取记录列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            order_by: 排序字段
            order_desc: 是否降序
            **filters: 过滤条件

        Returns:
            记录列表
        """
        query = db.query(cls.model_class)

        # 应用过滤条件
        for field_name, field_value in filters.items():
            if field_value is not None and hasattr(cls.model_class, field_name):
                query = query.filter(
                    getattr(cls.model_class, field_name) == field_value
                )

        # 排序
        if order_by and hasattr(cls.model_class, order_by):
            order_column = getattr(cls.model_class, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))

        return query.offset(skip).limit(limit).all()

    @classmethod
    def count_records(cls, db: Session, **filters) -> int:
        """
        统计记录数量

        Args:
            db: 数据库会话
            **filters: 过滤条件

        Returns:
            记录数量
        """
        from sqlalchemy import func

        query = db.query(func.count(cls.model_class.id))

        # 应用过滤条件
        for field_name, field_value in filters.items():
            if field_value is not None and hasattr(cls.model_class, field_name):
                query = query.filter(
                    getattr(cls.model_class, field_name) == field_value
                )

        return query.scalar()

    @classmethod
    def create_record(cls, db: Session, data: Dict[str, Any]) -> ModelType:
        """
        创建记录

        Args:
            db: 数据库会话
            data: 记录数据

        Returns:
            创建的记录对象
        """
        instance = cls.model_class(**data)
        db.add(instance)
        db.commit()
        db.refresh(instance)

        # 缓存新记录
        if hasattr(instance, "to_dict"):
            pk_value = getattr(instance, "id", None)
            if pk_value:
                cache_key = f"{cls.cache_prefix}:id:{pk_value}"
                cache_result(cache_key, instance.to_dict(), ttl=cls.cache_ttl)

        return instance

    @classmethod
    def update_record(
        cls, db: Session, id_value: Any, data: Dict[str, Any], pk_column: str = "id"
    ) -> Optional[ModelType]:
        """
        更新记录

        Args:
            db: 数据库会话
            id_value: ID值
            data: 更新数据
            pk_column: 主键列名

        Returns:
            更新后的记录对象或None
        """
        instance = cls.get_by_id(db, id_value, pk_column)
        if not instance:
            return None

        # 更新字段
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        # 更新时间戳
        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(instance)

        # 更新缓存
        if hasattr(instance, "to_dict"):
            cache_key = f"{cls.cache_prefix}:{pk_column}:{id_value}"
            cache_result(cache_key, instance.to_dict(), ttl=cls.cache_ttl)

        return instance

    @classmethod
    def delete_record(cls, db: Session, id_value: Any, pk_column: str = "id") -> bool:
        """
        删除记录

        Args:
            db: 数据库会话
            id_value: ID值
            pk_column: 主键列名

        Returns:
            是否成功删除
        """
        instance = cls.get_by_id(db, id_value, pk_column)
        if not instance:
            return False

        db.delete(instance)
        db.commit()

        # 清除缓存
        cache_key = f"{cls.cache_prefix}:{pk_column}:{id_value}"
        invalidate_cache(cache_key)

        return True

    @classmethod
    def invalidate_record_cache(cls, id_value: Any, pk_column: str = "id"):
        """
        清除记录缓存

        Args:
            id_value: ID值
            pk_column: 主键列名
        """
        cache_key = f"{cls.cache_prefix}:{pk_column}:{id_value}"
        invalidate_cache(cache_key)

    @classmethod
    def invalidate_list_cache(cls, pattern: str = "*"):
        """
        清除列表缓存

        Args:
            pattern: 缓存键模式
        """
        invalidate_cache(f"{cls.cache_prefix}:list:{pattern}")
