"""
User Repository

用户数据访问层，使用 SQLAlchemy 2.x AsyncSession。
"""

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户 Repository"""

    model = User

    async def get_by_user_id(self, user_id: str) -> Optional[User]:
        """根据用户ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户

        Args:
            email: 邮箱地址

        Returns:
            用户对象或None
        """
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户

        Args:
            phone: 手机号

        Returns:
            用户对象或None
        """
        stmt = select(self.model).where(self.model.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否已注册

        Args:
            email: 邮箱地址

        Returns:
            是否已存在
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.email == email)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0

    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否已注册

        Args:
            phone: 手机号

        Returns:
            是否已存在
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.phone == phone)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0

    async def list_active(self, skip: int = 0, limit: int = 50) -> List[User]:
        """获取活跃用户列表

        Args:
            skip: 跳过数量
            limit: 限制数量

        Returns:
            用户列表
        """
        stmt = (
            select(self.model)
            .where(self.model.is_active.is_(True))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
