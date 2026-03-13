"""
签到打卡业务逻辑服务
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from app.core.cache import cache_result, get_cached
from app.core.cache_config import CacheConfig
from app.core.interfaces import ICheckInService
from app.models.checkin import CheckIn
from app.models.emergency_contact import EmergencyContact
from app.schemas.checkin import (
    CheckInCreate,
    CheckInStatsResponse,
    CheckInStatusResponse,
)
from app.services.base_service import BaseService
from sqlalchemy import and_, func
from sqlalchemy.orm import Session


class CheckInService(BaseService[CheckIn], ICheckInService):
    """
    签到服务类 - 实例方法模式

    提供签到记录的创建、查询、统计等功能

    Attributes:
        db: 数据库会话
        model_class: 签到模型类
        cache_prefix: 缓存前缀
        cache_ttl: 缓存过期时间（秒）
    """

    model_class = CheckIn
    cache_prefix = CacheConfig.PREFIX_CHECKIN
    cache_ttl = CacheConfig.TTL_CHECKIN_LIST

    def __init__(self, db: Session):
        """
        初始化签到服务

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========== 创建方法 ==========

    def create(self, user_id: str, checkin_data: CheckInCreate) -> CheckIn:
        """
        创建签到记录

        Args:
            user_id: 用户ID
            checkin_data: 签到数据

        Returns:
            创建的签到记录

        Raises:
            ValueError: 当天已签到
        """
        # 获取当前日期
        today = date.today().strftime("%Y-%m-%d")

        try:
            # 创建签到记录（依赖数据库唯一约束防止并发）
            db_checkin = CheckIn(
                user_id=user_id,
                checkin_time=datetime.utcnow(),
                checkin_date=today,
                latitude=checkin_data.latitude,
                longitude=checkin_data.longitude,
                checkin_method=checkin_data.checkin_method,
                notes=checkin_data.notes,
            )

            self.db.add(db_checkin)
            self.db.commit()
            self.db.refresh(db_checkin)

            # 失效相关缓存
            self.invalidate_list_cache(f"{user_id}:*")

            return db_checkin

        except Exception as e:
            self.db.rollback()

            # 捕获唯一约束违反错误
            error_msg = str(e).lower()
            if "unique" in error_msg or "ix_checkins_user_date" in error_msg:
                raise ValueError("今天已经签到过了")

            # 重新抛出其他错误
            raise

    # ========== 查询方法 ==========

    def get_user_checkins(
        self,
        user_id: str,
        days: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[CheckIn]:
        """
        获取用户签到历史记录

        Args:
            user_id: 用户ID
            days: 查询天数(默认30天)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            签到记录列表
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=days)
        if end_date is None:
            end_date = date.today()

        # 使用 BaseService 的列表查询方法
        return self.list_records(
            self.db, user_id=user_id, order_by="checkin_date", order_desc=True
        )

    def get_checkin_status(
        self, user_id: str, target_date: Optional[date] = None
    ) -> CheckInStatusResponse:
        """
        查询指定日期的签到状态

        Args:
            user_id: 用户ID
            target_date: 目标日期(默认今天)

        Returns:
            签到状态
        """
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")

        checkin = (
            self.db.query(CheckIn)
            .filter(and_(CheckIn.user_id == user_id, CheckIn.checkin_date == date_str))
            .first()
        )

        return CheckInStatusResponse(
            is_checked_in=bool(checkin),
            checkin_time=checkin.checkin_time if checkin else None,
        )

    def check_today_checked_in(self, user_id: str) -> bool:
        """
        检查今天是否已签到

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否已签到
        """
        today = date.today().strftime("%Y-%m-%d")
        checkin = (
            self.db.query(CheckIn)
            .filter(and_(CheckIn.user_id == user_id, CheckIn.checkin_date == today))
            .first()
        )
        return bool(checkin)

    # ========== 统计方法 ==========

    def get_checkin_stats(self, user_id: str, days: int = 30) -> CheckInStatsResponse:
        """
        获取用户签到统计信息

        Args:
            user_id: 用户ID
            days: 统计天数(默认30天)

        Returns:
            签到统计信息
        """
        # 尝试从缓存获取
        cache_key = CacheConfig.make_key(
            CacheConfig.PREFIX_CHECKIN_STATS, user_id, days
        )
        cached_stats = get_cached(cache_key)
        if cached_stats:
            return cached_stats

        # 计算总签到次数
        total_checkins = (
            self.db.query(func.count(CheckIn.id))
            .filter(
                and_(
                    CheckIn.user_id == user_id,
                    CheckIn.checkin_date
                    >= (date.today() - timedelta(days=days)).strftime("%Y-%m-%d"),
                )
            )
            .scalar()
        )

        # 计算当前连续签到天数
        current_streak = self._calculate_streak(user_id, from_date=date.today())

        # 计算最长连续签到天数
        longest_streak = self._calculate_longest_streak(user_id, days)

        # 计算签到率
        checkin_rate = (total_checkins / days) * 100 if days > 0 else 0

        stats = CheckInStatsResponse(
            total_checkins=total_checkins,
            current_streak=current_streak,
            longest_streak=longest_streak,
            checkin_rate=round(checkin_rate, 2),
        )

        # 缓存结果
        cache_result(cache_key, stats, ttl=CacheConfig.TTL_CHECKIN_STATS)

        return stats

    # ========== 紧急联系人 ==========

    def get_emergency_contacts_for_notification(
        self, user_id: str
    ) -> List[EmergencyContact]:
        """
        获取用户的紧急联系人(用于签到通知)

        Args:
            user_id: 用户ID

        Returns:
            紧急联系人列表
        """
        return (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == user_id)
            .order_by(EmergencyContact.priority)
            .all()
        )

    # ========== 私有辅助方法 ==========

    def _calculate_streak(self, user_id: str, from_date: date) -> int:
        """
        计算从指定日期开始的连续签到天数

        Args:
            user_id: 用户ID
            from_date: 起始日期

        Returns:
            连续签到天数
        """
        streak = 0
        current_date = from_date

        while True:
            date_str = current_date.strftime("%Y-%m-%d")

            checkin = (
                self.db.query(CheckIn)
                .filter(
                    and_(CheckIn.user_id == user_id, CheckIn.checkin_date == date_str)
                )
                .first()
            )

            if checkin:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

            if streak >= 365:
                break

        return streak

    def _calculate_longest_streak(self, user_id: str, days: int) -> int:
        """
        计算指定天数内的最长连续签到天数

        Args:
            user_id: 用户ID
            days: 查询天数

        Returns:
            最长连续签到天数
        """
        # 获取指定天数内的所有签到记录
        checkins = (
            self.db.query(CheckIn)
            .filter(
                and_(
                    CheckIn.user_id == user_id,
                    CheckIn.checkin_date
                    >= (date.today() - timedelta(days=days)).strftime("%Y-%m-%d"),
                )
            )
            .order_by(CheckIn.checkin_date)
            .all()
        )

        if not checkins:
            return 0

        # 提取签到日期列表
        checkin_dates = sorted([c.checkin_date for c in checkins])

        longest_streak = 1
        current_streak = 1

        # 遍历签到日期,计算最长连续签到
        for i in range(1, len(checkin_dates)):
            prev_date = datetime.strptime(checkin_dates[i - 1], "%Y-%m-%d").date()
            curr_date = datetime.strptime(checkin_dates[i], "%Y-%m-%d").date()

            if (curr_date - prev_date).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak

    # ========== 向后兼容的适配器方法 ==========

    def create_checkin(self, user_id: str, checkin_data: CheckInCreate) -> CheckIn:
        """向后兼容：创建签到记录"""
        return self.create(user_id, checkin_data)
