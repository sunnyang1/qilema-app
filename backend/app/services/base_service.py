"""
服务基类

提供通用的CRUD操作和缓存管理机制
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.core.cache import cache_result, get_cached, invalidate_cache
from app.core.query_builder import QueryBuilder, paginate

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
        - 缓存命中时利用 Session.get() 优先查 identity map，避免重复 SQL 查询
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

        # 检查缓存
        cached_data = get_cached(cache_key)
        cache_exists = cached_data is not None

        # 修复：缓存命中时，优先使用 Session.get() 查 identity map，避免重复 SQL
        if cache_exists:
            result = db.get(cls.model_class, id_value)
            if result is not None:
                return result

        # 缓存未命中或 identity map 未命中，执行查询
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

    @classmethod
    def get_query_builder(cls, db: Session) -> QueryBuilder:
        """
        获取查询构建器

        Args:
            db: 数据库会话

        Returns:
            QueryBuilder: 配置好的查询构建器
        """
        return QueryBuilder(db.query(cls.model_class), cls.model_class)

    @classmethod
    def get_by_ids(
        cls, db: Session, ids: List[Any], pk_column: str = "id"
    ) -> List[ModelType]:
        """
        根据多个ID获取记录（批量查询优化）

        Args:
            db: 数据库会话
            ids: ID列表
            pk_column: 主键列名

        Returns:
            记录列表
        """
        if not ids:
            return []

        if hasattr(cls.model_class, pk_column):
            column = getattr(cls.model_class, pk_column)
            return db.query(cls.model_class).filter(column.in_(ids)).all()
        return []

    @classmethod
    def create_batch(
        cls, db: Session, records: List[Dict[str, Any]], batch_size: int = 1000
    ) -> List[ModelType]:
        """
        批量创建记录

        Args:
            db: 数据库会话
            records: 记录数据列表
            batch_size: 每批处理数量

        Returns:
            创建的记录列表
        """
        if not records:
            return []

        instances = []
        for i, data in enumerate(records):
            instance = cls.model_class(**data)
            db.add(instance)
            instances.append(instance)

            # 分批提交
            if (i + 1) % batch_size == 0:
                db.commit()
                for inst in instances[-batch_size:]:
                    db.refresh(inst)

        # 提交剩余
        if len(records) % batch_size != 0:
            db.commit()
            for inst in instances[len(records) - (len(records) % batch_size) :]:
                db.refresh(inst)

        # 缓存新记录
        for instance in instances:
            if hasattr(instance, "to_dict"):
                pk_value = getattr(instance, "id", None)
                if pk_value:
                    cache_key = f"{cls.cache_prefix}:id:{pk_value}"
                    cache_result(cache_key, instance.to_dict(), ttl=cls.cache_ttl)

        return instances

    @classmethod
    def update_batch(
        cls,
        db: Session,
        updates: List[Dict[str, Any]],
        pk_column: str = "id",
        batch_size: int = 1000,
    ) -> int:
        """
        批量更新记录

        Args:
            db: 数据库会话
            updates: 更新数据列表，每项包含 id 和更新字段
            pk_column: 主键列名
            batch_size: 每批处理数量

        Returns:
            更新的记录数
        """
        if not updates:
            return 0

        updated_count = 0
        pk_values = []

        for i, data in enumerate(updates):
            pk_value = data.get(pk_column)
            if not pk_value:
                continue

            instance = cls.get_by_id(db, pk_value, pk_column)
            if not instance:
                continue

            # 更新字段
            for field, value in data.items():
                if field != pk_column and hasattr(instance, field):
                    setattr(instance, field, value)

            # 更新时间戳
            if hasattr(instance, "updated_at"):
                instance.updated_at = datetime.utcnow()

            pk_values.append(pk_value)
            updated_count += 1

            # 分批提交
            if (i + 1) % batch_size == 0:
                db.commit()

        # 提交剩余
        if updates and len(updates) % batch_size != 0:
            db.commit()

        # 清除缓存
        for pk_value in pk_values:
            cls.invalidate_record_cache(pk_value, pk_column)

        return updated_count

    @classmethod
    def delete_batch(
        cls, db: Session, ids: List[Any], pk_column: str = "id", batch_size: int = 1000
    ) -> int:
        """
        批量删除记录

        Args:
            db: 数据库会话
            ids: ID列表
            pk_column: 主键列名
            batch_size: 每批处理数量

        Returns:
            删除的记录数
        """
        if not ids:
            return 0

        deleted_count = 0

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]

            if hasattr(cls.model_class, pk_column):
                column = getattr(cls.model_class, pk_column)
                result = (
                    db.query(cls.model_class)
                    .filter(column.in_(batch_ids))
                    .delete(synchronize_session=False)
                )
                deleted_count += result

                # 清除缓存
                for pk_value in batch_ids:
                    cls.invalidate_record_cache(pk_value, pk_column)

            db.commit()

        return deleted_count

    @classmethod
    def paginated_list(
        cls,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        order_by: str = None,
        order_desc: bool = True,
        **filters,
    ):
        """
        获取分页列表（使用 QueryBuilder）

        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页数量
            order_by: 排序字段
            order_desc: 是否降序
            **filters: 过滤条件

        Returns:
            PaginationResult: 分页结果
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

        return paginate(query, page, per_page)

    # ========== 异步方法变体 (Phase 1: 为 Phase 2 全面异步化做准备) ==========

    @classmethod
    async def aget_by_id(
        cls, db: Session, id_value: Any, pk_column: str = "id"
    ) -> Optional[ModelType]:
        """异步获取记录（兼容层，当前调用同步实现）"""
        return cls.get_by_id(db, id_value, pk_column)

    @classmethod
    async def aget_by_field(
        cls, db: Session, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """异步根据字段值获取单条记录"""
        return cls.get_by_field(db, field_name, field_value)

    @classmethod
    async def alist_records(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_desc: bool = True,
        **filters,
    ) -> List[ModelType]:
        """异步获取记录列表"""
        return cls.list_records(db, skip, limit, order_by, order_desc, **filters)

    @classmethod
    async def acreate_record(cls, db: Session, data: Dict[str, Any]) -> ModelType:
        """异步创建记录"""
        return cls.create_record(db, data)

    @classmethod
    async def aupdate_record(
        cls, db: Session, id_value: Any, data: Dict[str, Any], pk_column: str = "id"
    ) -> Optional[ModelType]:
        """异步更新记录"""
        return cls.update_record(db, id_value, data, pk_column)

    @classmethod
    async def adelete_record(
        cls, db: Session, id_value: Any, pk_column: str = "id"
    ) -> bool:
        """异步删除记录"""
        return cls.delete_record(db, id_value, pk_column)

    @classmethod
    async def aget_by_ids(
        cls, db: Session, ids: List[Any], pk_column: str = "id"
    ) -> List[ModelType]:
        """异步根据多个ID获取记录"""
        return cls.get_by_ids(db, ids, pk_column)

    @classmethod
    async def acount_records(cls, db: Session, **filters) -> int:
        """异步统计记录数量"""
        return cls.count_records(db, **filters)

    @staticmethod
    @contextmanager
    def transaction(db: Session):
        """
        事务管理上下文管理器

        Args:
            db: 数据库会话

        Usage:
            >>> with BaseService.transaction(db):
            ...     service.create_record(db, {...})
            ...     service.update_record(db, 1, {...})
        """
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
