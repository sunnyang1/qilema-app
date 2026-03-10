"""
查询构建器 (QueryBuilder)

提供统一的查询构建功能，支持分页、排序、过滤
"""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Query, Session

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
        # 使用 count() 更高效，避免获取完整记录
        return self.query.count() > 0

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
