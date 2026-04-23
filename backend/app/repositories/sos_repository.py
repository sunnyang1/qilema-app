"""
SOS Repository

SOS 请求数据访问层，使用 SQLAlchemy 2.x AsyncSession。
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sos_request import SOSRequest
from app.repositories.base_repository import BaseRepository


class SOSRepository(BaseRepository[SOSRequest]):
    """SOS 请求 Repository"""

    model = SOSRequest

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[SOSRequest]:
        """根据用户ID获取SOS记录列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            SOS记录列表
        """
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.trigger_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_sos_id_and_user(
        self, sos_id: str, user_id: str
    ) -> Optional[SOSRequest]:
        """根据SOS ID和用户ID获取记录

        Args:
            sos_id: SOS ID
            user_id: 用户ID

        Returns:
            SOS记录或None
        """
        stmt = select(self.model).where(
            self.model.id == sos_id, self.model.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_by_user(self, user_id: str) -> List[SOSRequest]:
        """获取用户待处理的SOS记录

        Args:
            user_id: 用户ID

        Returns:
            待处理SOS记录列表
        """
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == "pending",
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, sos_id: int, status: str, **extra_fields
    ) -> Optional[SOSRequest]:
        """更新SOS状态

        Args:
            sos_id: SOS记录ID
            status: 新状态
            **extra_fields: 额外更新字段

        Returns:
            更新后的记录或None
        """
        instance = await self.get_by_id(sos_id)
        if not instance:
            return None

        instance.status = status
        for field, value in extra_fields.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        await self.db.flush()
        await self.db.refresh(instance)
        return instance
