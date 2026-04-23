"""
CheckIn Repository

签到数据访问层，使用 SQLAlchemy 2.x AsyncSession。
"""

from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkin import CheckIn
from app.repositories.base_repository import BaseRepository


class CheckInRepository(BaseRepository[CheckIn]):
    """签到 Repository"""

    model = CheckIn

    async def get_by_user_id(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> List[CheckIn]:
        """根据用户ID获取签到记录列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量

        Returns:
            签到记录列表
        """
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.checkin_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_date(
        self, user_id: str, checkin_date: str
    ) -> Optional[CheckIn]:
        """根据用户ID和日期获取签到记录

        Args:
            user_id: 用户ID
            checkin_date: 签到日期(YYYY-MM-DD)

        Returns:
            签到记录或None
        """
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.checkin_date == checkin_date,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_by_user(self, user_id: str, days: int = 30) -> List[CheckIn]:
        """获取用户最近N天的签到记录

        Args:
            user_id: 用户ID
            days: 天数

        Returns:
            签到记录列表
        """
        from datetime import datetime, timedelta

        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        stmt = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.checkin_date >= start_date,
            )
            .order_by(self.model.checkin_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: str, days: int = 30) -> int:
        """统计用户最近N天的签到次数

        Args:
            user_id: 用户ID
            days: 天数

        Returns:
            签到次数
        """
        from datetime import datetime, timedelta

        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.checkin_date >= start_date,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_streak(self, user_id: str) -> int:
        """计算用户当前连续签到天数

        Args:
            user_id: 用户ID

        Returns:
            连续签到天数
        """
        from datetime import datetime, timedelta

        today = datetime.utcnow().date()
        streak = 0

        for i in range(365):
            check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            stmt = (
                select(func.count())
                .select_from(self.model)
                .where(
                    self.model.user_id == user_id,
                    self.model.checkin_date == check_date,
                )
            )
            result = await self.db.execute(stmt)
            count = result.scalar_one()

            if count > 0:
                streak += 1
            else:
                break

        return streak
