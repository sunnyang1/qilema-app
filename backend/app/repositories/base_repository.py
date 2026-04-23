"""
Repository 基类

提供通用的异步 CRUD 操作，与 SQLAlchemy 2.x AsyncSession 集成。
"""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """异步 Repository 基类

    用法:
        class UserRepository(BaseRepository[User]):
            model = User

        repo = UserRepository(db_session)
        user = await repo.get_by_id(1)
    """

    model: Type[ModelT]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelT]:
        """根据主键获取记录

        Args:
            id: 主键值

        Returns:
            记录对象或 None
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: List[Any]) -> List[ModelT]:
        """根据多个主键批量获取记录

        Args:
            ids: 主键值列表

        Returns:
            记录对象列表
        """
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[ModelT]:
        """根据字段值获取单条记录

        Args:
            field_name: 字段名
            field_value: 字段值

        Returns:
            记录对象或 None
        """
        if not hasattr(self.model, field_name):
            return None
        column = getattr(self.model, field_name)
        stmt = select(self.model).where(column == field_value)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        **filters,
    ) -> tuple[List[ModelT], int]:
        """分页查询记录列表

        Args:
            offset: 跳过数量
            limit: 限制数量
            order_by: 排序字段名
            order_desc: 是否降序
            **filters: 过滤条件

        Returns:
            (记录列表, 总数量)
        """
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        # 应用过滤条件
        for field_name, field_value in filters.items():
            if field_value is not None and hasattr(self.model, field_name):
                condition = getattr(self.model, field_name) == field_value
                stmt = stmt.where(condition)
                count_stmt = count_stmt.where(condition)

        # 排序
        if order_by and hasattr(self.model, order_by):
            from sqlalchemy import asc, desc

            order_column = getattr(self.model, order_by)
            if order_desc:
                stmt = stmt.order_by(desc(order_column))
            else:
                stmt = stmt.order_by(asc(order_column))

        # 分页
        stmt = stmt.offset(offset).limit(limit)

        # 执行查询
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        return items, total

    async def create(self, **data) -> ModelT:
        """创建记录

        Args:
            **data: 记录数据

        Returns:
            创建的记录对象
        """
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def save(self, instance: ModelT) -> ModelT:
        """保存记录（新增或更新）

        Args:
            instance: 记录对象

        Returns:
            保存后的记录对象
        """
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, id: Any, **data) -> Optional[ModelT]:
        """更新记录

        Args:
            id: 主键值
            **data: 更新数据

        Returns:
            更新后的记录对象或 None
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        # 更新时间戳
        if hasattr(instance, "updated_at"):
            from datetime import datetime

            instance.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, id: Any) -> bool:
        """删除记录

        Args:
            id: 主键值

        Returns:
            是否成功删除
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.db.delete(instance)
        await self.db.flush()
        return True

    async def delete_by_ids(self, ids: List[Any]) -> int:
        """批量删除记录

        Args:
            ids: 主键值列表

        Returns:
            删除的记录数
        """
        if not ids:
            return 0
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(stmt)
        return result.rowcount or 0

    async def count(self, **filters) -> int:
        """统计记录数量

        Args:
            **filters: 过滤条件

        Returns:
            记录数量
        """
        stmt = select(func.count()).select_from(self.model)

        for field_name, field_value in filters.items():
            if field_value is not None and hasattr(self.model, field_name):
                stmt = stmt.where(getattr(self.model, field_name) == field_value)

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def exists(self, id: Any) -> bool:
        """检查记录是否存在

        Args:
            id: 主键值

        Returns:
            是否存在
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
