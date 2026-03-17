"""
查询构建器 (QueryBuilder)

提供统一的查询构建功能，支持分页、排序、过滤
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from sqlalchemy import asc, desc, func, distinct
from sqlalchemy.orm import Query, Session, joinedload, selectinload

T = TypeVar("T")


class QueryBuilder:
    """
    查询构建器

    提供统一的查询构建功能：
    - 分页
    - 排序
    - 过滤条件
    - 动态条件构建

    使用示例:
        >>> query = db.query(User)
        >>> builder = QueryBuilder(query)
        >>> result = (
        ...     builder.filter(status='active')
        ...     .order_by('created_at', desc=True)
        ...     .paginate(page=1, per_page=20)
        ...     .execute()
        ... )
    """

    def __init__(self, query: Query, model_class: Optional[Type] = None):
        """
        初始化查询构建器

        Args:
            query: SQLAlchemy Query 对象
            model_class: 模型类（用于获取字段）
        """
        self.query = query
        self.model_class = model_class
        self._filters: List[Callable] = []
        self._order_by: Optional[str] = None
        self._order_desc: bool = True
        self._offset: Optional[int] = None
        self._limit: Optional[int] = None

    def filter(self, **conditions: Any) -> "QueryBuilder":
        """
        添加过滤条件

        Args:
            **conditions: 字段名=值的过滤条件

        Returns:
            QueryBuilder: 自身，支持链式调用

        Example:
            >>> builder.filter(status='active', age=25)
        """
        for field_name, value in conditions.items():
            if value is not None and self.model_class:
                if hasattr(self.model_class, field_name):
                    column = getattr(self.model_class, field_name)
                    self.query = self.query.filter(column == value)
        return self

    def filter_by(self, **conditions: Any) -> "QueryBuilder":
        """
        使用 filter_by 添加过滤条件（更宽松的匹配）

        Args:
            **conditions: 字段名=值的过滤条件

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self.query = self.query.filter_by(
            **{k: v for k, v in conditions.items() if v is not None}
        )
        return self

    def where(self, condition: Any) -> "QueryBuilder":
        """
        添加原始 SQLAlchemy 过滤条件

        Args:
            condition: SQLAlchemy 条件表达式

        Returns:
            QueryBuilder: 自身，支持链式调用

        Example:
            >>> builder.where(User.age > 18)
        """
        self.query = self.query.filter(condition)
        return self

    def where_in(self, field_name: str, values: List[Any]) -> "QueryBuilder":
        """
        添加 IN 条件

        Args:
            field_name: 字段名
            values: 值列表

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        if values and self.model_class and hasattr(self.model_class, field_name):
            column = getattr(self.model_class, field_name)
            self.query = self.query.filter(column.in_(values))
        return self

    def where_like(self, field_name: str, pattern: str) -> "QueryBuilder":
        """
        添加 LIKE 条件

        Args:
            field_name: 字段名
            pattern: 匹配模式（如 '%keyword%'）

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        if pattern and self.model_class and hasattr(self.model_class, field_name):
            column = getattr(self.model_class, field_name)
            self.query = self.query.filter(column.like(pattern))
        return self

    def where_between(
        self,
        field_name: str,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
    ) -> "QueryBuilder":
        """
        添加 BETWEEN 条件

        Args:
            field_name: 字段名
            min_value: 最小值
            max_value: 最大值

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        if self.model_class and hasattr(self.model_class, field_name):
            column = getattr(self.model_class, field_name)
            if min_value is not None:
                self.query = self.query.filter(column >= min_value)
            if max_value is not None:
                self.query = self.query.filter(column <= max_value)
        return self

    def order_by(self, field: str, order_desc: bool = False) -> "QueryBuilder":
        """
        设置排序

        Args:
            field: 排序字段名
            order_desc: 是否降序

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self._order_by = field
        self._order_desc = order_desc

        if self.model_class and hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            if order_desc:
                self.query = self.query.order_by(desc(column))
            else:
                self.query = self.query.order_by(asc(column))
        return self

    def paginate(self, page: int = 1, per_page: int = 20) -> "QueryBuilder":
        """
        设置分页

        Args:
            page: 页码（从1开始）
            per_page: 每页数量

        Returns:
            QueryBuilder: 自身，支持链式调用

        Raises:
            ValueError: 当 page < 1 或 per_page <= 0 时
        """
        if page < 1:
            raise ValueError(f"page 必须 >= 1，当前值: {page}")
        if per_page <= 0:
            raise ValueError(f"per_page 必须 > 0，当前值: {per_page}")

        self._offset = (page - 1) * per_page
        self._limit = per_page
        self.query = self.query.offset(self._offset).limit(self._limit)
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """
        设置偏移量

        Args:
            offset: 偏移量

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self._offset = offset
        self.query = self.query.offset(offset)
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """
        设置限制数量

        Args:
            limit: 限制数量

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self._limit = limit
        self.query = self.query.limit(limit)
        return self

    def join(self, *entities: Any, **kwargs: Any) -> "QueryBuilder":
        """
        添加 JOIN

        Args:
            *entities: 要 JOIN 的实体
            **kwargs: JOIN 参数

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self.query = self.query.join(*entities, **kwargs)
        return self

    def options(self, *args: Any) -> "QueryBuilder":
        """
        添加查询选项（如 eager load）

        Args:
            *args: 查询选项

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self.query = self.query.options(*args)
        return self

    def execute(self) -> List[T]:
        """
        执行查询

        Returns:
            List[T]: 查询结果列表
        """
        return self.query.all()

    def first(self) -> Optional[T]:
        """
        获取第一条记录

        Returns:
            Optional[T]: 第一条记录或 None
        """
        return self.query.first()

    def one(self) -> T:
        """
        获取唯一记录（不存在或有多个时抛出异常）

        Returns:
            T: 唯一记录

        Raises:
            NoResultFound: 没有找到记录
            MultipleResultsFound: 找到多个记录
        """
        return self.query.one()

    def one_or_none(self) -> Optional[T]:
        """
        获取唯一记录或 None

        Returns:
            Optional[T]: 唯一记录或 None
        """
        return self.query.one_or_none()

    def count(self) -> int:
        """
        获取记录数

        Returns:
            int: 记录数
        """
        return self.query.count()

    def exists(self) -> bool:
        """
        检查是否有记录

        Returns:
            bool: 是否有记录
        """
        # 使用 exists() 更高效，避免获取完整记录
        from sqlalchemy.sql import exists as sa_exists
        return self.query.session.query(
            sa_exists().where(self.query.whereclause)
        ).scalar() if self.query.whereclause else self.query.count() > 0

    def group_by(self, *field_names: str) -> "QueryBuilder":
        """
        添加 GROUP BY 条件

        Args:
            *field_names: 字段名列表

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        columns = []
        for field_name in field_names:
            if self.model_class and hasattr(self.model_class, field_name):
                columns.append(getattr(self.model_class, field_name))
        if columns:
            self.query = self.query.group_by(*columns)
        return self

    def distinct(self, *field_names: str) -> "QueryBuilder":
        """
        添加 DISTINCT 条件

        Args:
            *field_names: 字段名列表（可选，为空时对整个查询去重）

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        if field_names and self.model_class:
            columns = [
                getattr(self.model_class, f) for f in field_names
                if hasattr(self.model_class, f)
            ]
            if columns:
                self.query = self.query.distinct(*columns)
        else:
            self.query = self.query.distinct()
        return self

    def with_entities(self, *entities: Any) -> "QueryBuilder":
        """
        指定查询的实体/列

        Args:
            *entities: 要查询的实体或列

        Returns:
            QueryBuilder: 自身，支持链式调用
        """
        self.query = self.query.with_entities(*entities)
        return self

    def eager_load(self, *relations: str) -> "QueryBuilder":
        """
        添加 eager loading（自动选择 joinedload 或 selectinload）

        Args:
            *relations: 关联关系属性名列表

        Returns:
            QueryBuilder: 自身，支持链式调用

        Example:
            >>> builder.eager_load("emergency_contacts", "health_record")
        """
        if not self.model_class:
            return self

        for relation in relations:
            if hasattr(self.model_class, relation):
                rel_attr = getattr(self.model_class, relation)
                # 根据关系类型选择合适的加载策略
                # 多对一/一对一使用 joinedload，一对多使用 selectinload
                prop = getattr(rel_attr, 'property', None)
                if prop and hasattr(prop, 'uselist'):
                    if prop.uselist:
                        self.query = self.query.options(selectinload(rel_attr))
                    else:
                        self.query = self.query.options(joinedload(rel_attr))
                else:
                    self.query = self.query.options(joinedload(rel_attr))
        return self

    def only_columns(self, *column_names: str) -> "QueryBuilder":
        """
        只查询指定列（优化大数据量查询）

        Args:
            *column_names: 列名列表

        Returns:
            QueryBuilder: 自身，支持链式调用

        Example:
            >>> builder.only_columns("id", "name", "phone")
        """
        if self.model_class:
            columns = [
                getattr(self.model_class, c) for c in column_names
                if hasattr(self.model_class, c)
            ]
            if columns:
                self.query = self.query.with_entities(*columns)
        return self

    def aggregate(self, agg_func: str, field_name: str, label: str = None) -> "QueryBuilder":
        """
        添加聚合函数

        Args:
            agg_func: 聚合函数名 ('count', 'sum', 'avg', 'min', 'max')
            field_name: 字段名
            label: 结果标签（别名）

        Returns:
            QueryBuilder: 自身，支持链式调用

        Example:
            >>> builder.aggregate('count', 'id', 'total')
            >>> builder.aggregate('sum', 'amount', 'total_amount')
        """
        if not self.model_class or not hasattr(self.model_class, field_name):
            return self

        column = getattr(self.model_class, field_name)
        func_map = {
            'count': func.count,
            'sum': func.sum,
            'avg': func.avg,
            'min': func.min,
            'max': func.max,
        }

        if agg_func in func_map:
            agg_column = func_map[agg_func](column)
            if label:
                agg_column = agg_column.label(label)
            self.query = self.query.with_entities(agg_column)

        return self

    def scalar(self) -> Optional[Any]:
        """
        获取标量值

        Returns:
            Optional[Any]: 标量值
        """
        return self.query.scalar()

    def get_query(self) -> Query:
        """
        获取原始 Query 对象

        Returns:
            Query: SQLAlchemy Query 对象
        """
        return self.query


class PaginationResult:
    """
    分页结果
    """

    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        per_page: int,
    ):
        if per_page <= 0:
            raise ValueError(f"per_page 必须 > 0，当前值: {per_page}")
        if page < 1:
            raise ValueError(f"page 必须 >= 1，当前值: {page}")

        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            Dict: 分页结果字典
        """
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "pages": self.pages,
            "has_prev": self.has_prev,
            "has_next": self.has_next,
        }


def paginate(
    query: Query,
    page: int = 1,
    per_page: int = 20,
) -> PaginationResult:
    """
    便捷的查询分页函数

    Args:
        query: SQLAlchemy Query 对象
        page: 页码
        per_page: 每页数量

    Returns:
        PaginationResult: 分页结果

    Raises:
        ValueError: 当 page < 1 或 per_page <= 0 时
    """
    if page < 1:
        raise ValueError(f"page 必须 >= 1，当前值: {page}")
    if per_page <= 0:
        raise ValueError(f"per_page 必须 > 0，当前值: {per_page}")

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return PaginationResult(items, total, page, per_page)


class BatchQueryBuilder:
    """
    批量查询构建器

    用于高效处理大批量数据查询，支持分批获取

    Example:
        >>> batch = BatchQueryBuilder(db.query(User), batch_size=1000)
        >>> for records in batch.iter_batches():
        ...     process_records(records)
    """

    def __init__(self, query: Query, batch_size: int = 1000):
        """
        初始化批量查询构建器

        Args:
            query: SQLAlchemy Query 对象
            batch_size: 每批数量
        """
        self.query = query
        self.batch_size = batch_size
        self._total = None

    def iter_batches(self):
        """
        分批迭代查询结果

        Yields:
            List[T]: 每批记录列表
        """
        offset = 0
        while True:
            batch = self.query.offset(offset).limit(self.batch_size).all()
            if not batch:
                break
            yield batch
            offset += self.batch_size

    def iter_records(self):
        """
        逐条迭代查询结果（内部使用分批）

        Yields:
            T: 单条记录
        """
        for batch in self.iter_batches():
            for record in batch:
                yield record

    @property
    def total(self) -> int:
        """
        获取总记录数（缓存）

        Returns:
            int: 总记录数
        """
        if self._total is None:
            self._total = self.query.count()
        return self._total

    def __iter__(self):
        """使对象可迭代"""
        return iter(self.iter_records())


def query_to_dict(
    query: Query,
    model_class: Type = None,
    include_relations: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    将查询构建器的配置转换为字典（用于缓存键生成）

    Args:
        query: 查询对象
        model_class: 模型类
        include_relations: 包含的关联关系

    Returns:
        Dict: 查询配置字典
    """
    return {
        "model": model_class.__name__ if model_class else None,
        "str": str(query.statement.compile(compile_kwargs={"literal_binds": True})),
        "relations": include_relations or [],
    }
