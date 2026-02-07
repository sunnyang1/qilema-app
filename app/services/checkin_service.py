"""
签到打卡业务逻辑服务
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.checkin import CheckIn
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.checkin import (
    CheckInCreate,
    CheckInResponse,
    CheckInStatsResponse,
    CheckInStatusResponse
)
from app.core.cache import get_cached, cache_result, invalidate_cache


class CheckInService:
    """签到服务类"""

    @staticmethod
    def create_checkin(db: Session, user_id: str, checkin_data: CheckInCreate) -> CheckIn:
        """
        创建签到记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            checkin_data: 签到数据
            
        Returns:
            创建的签到记录
            
        Raises:
            ValueError: 当天已签到
        """
        # 获取当前日期
        today = date.today().strftime('%Y-%m-%d')
        
        # 检查今天是否已经签到
        existing_checkin = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.checkin_date == today
            )
        ).first()
        
        if existing_checkin:
            raise ValueError("今天已经签到过了")
        
        # 创建签到记录
        db_checkin = CheckIn(
            user_id=user_id,
            checkin_time=datetime.utcnow(),
            checkin_date=today,
            latitude=checkin_data.latitude,
            longitude=checkin_data.longitude,
            checkin_method=checkin_data.checkin_method,
            notes=checkin_data.notes
        )
        
        db.add(db_checkin)
        db.commit()
        db.refresh(db_checkin)
        
        # 失效相关缓存
        invalidate_cache(f"checkin:list:{user_id}:*")
        invalidate_cache(f"checkin:status:{user_id}:*")
        invalidate_cache(f"checkin:stats:{user_id}:*")
        
        return db_checkin

    @staticmethod
    def get_user_checkins(
        db: Session, 
        user_id: str, 
        days: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CheckIn]:
        """
        获取用户签到历史记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数(默认30天)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            签到记录列表
        """
        # 尝试从缓存获取（缓存10分钟）
        cache_key = f"checkin:list:{user_id}:{days}:{start_date or ''}:{end_date or ''}"
        cached_checkins = get_cached(cache_key)
        if cached_checkins:
            # 缓存命中
            return cached_checkins

        if start_date is None:
            start_date = date.today() - timedelta(days=days)
        if end_date is None:
            end_date = date.today()

        checkins = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.checkin_date >= start_date.strftime('%Y-%m-%d'),
                CheckIn.checkin_date <= end_date.strftime('%Y-%m-%d')
            )
        ).order_by(desc(CheckIn.checkin_date)).all()

        # 缓存结果（1小时）
        cache_result(cache_key, checkins, ttl=3600)

        return checkins

    @staticmethod
    def get_checkin_stats(db: Session, user_id: str, days: int = 30) -> CheckInStatsResponse:
        """
        获取用户签到统计信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 统计天数(默认30天)

        Returns:
            签到统计信息
        """
        # 尝试从缓存获取（缓存30分钟）
        cache_key = f"checkin:stats:{user_id}:{days}"
        cached_stats = get_cached(cache_key)
        if cached_stats:
            return cached_stats

        # 计算总签到次数
        total_checkins = db.query(func.count(CheckIn.id)).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.checkin_date >= (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
            )
        ).scalar()

        # 计算当前连续签到天数
        current_streak = CheckInService._calculate_streak(db, user_id, from_date=date.today())

        # 计算最长连续签到天数
        longest_streak = CheckInService._calculate_longest_streak(db, user_id, days)

        # 计算签到率
        checkin_rate = (total_checkins / days) * 100 if days > 0 else 0

        stats = CheckInStatsResponse(
            total_checkins=total_checkins,
            current_streak=current_streak,
            longest_streak=longest_streak,
            checkin_rate=round(checkin_rate, 2)
        )

        # 缓存结果（30分钟）
        cache_result(cache_key, stats, ttl=1800)

        return stats

    @staticmethod
    def get_checkin_status(db: Session, user_id: str, target_date: Optional[date] = None) -> CheckInStatusResponse:
        """
        查询指定日期的签到状态

        Args:
            db: 数据库会话
            user_id: 用户ID
            target_date: 目标日期(默认今天)

        Returns:
            签到状态
        """
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime('%Y-%m-%d')

        # 尝试从缓存获取（缓存10分钟）
        cache_key = f"checkin:status:{user_id}:{date_str}"
        cached_status = get_cached(cache_key)
        if cached_status:
            return cached_status

        checkin = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.checkin_date == date_str
            )
        ).first()

        status = CheckInStatusResponse(
            is_checked_in=bool(checkin),
            checkin_time=checkin.checkin_time if checkin else None
        )

        # 缓存结果（10分钟）
        cache_result(cache_key, status, ttl=600)

        return status

    @staticmethod
    def get_emergency_contacts_for_notification(db: Session, user_id: str) -> List[EmergencyContact]:
        """
        获取用户的紧急联系人(用于签到通知)
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            紧急联系人列表
        """
        # 尝试从缓存获取（缓存10分钟）
        cache_key = f"checkin:contacts:{user_id}"
        cached_contacts = get_cached(cache_key)
        if cached_contacts:
            return cached_contacts

        contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).order_by(EmergencyContact.priority).all()

        # 缓存结果（10分钟）
        cache_result(cache_key, contacts, ttl=600)

        return contacts

    @staticmethod
    def _calculate_streak(db: Session, user_id: str, from_date: date) -> int:
        """
        计算从指定日期开始的连续签到天数
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            from_date: 起始日期
            
        Returns:
            连续签到天数
        """
        streak = 0
        current_date = from_date
        
        while True:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 查询该日期的签到记录
            checkin = db.query(CheckIn).filter(
                and_(
                    CheckIn.user_id == user_id,
                    CheckIn.checkin_date == date_str
                )
            ).first()
            
            if checkin:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
            
            # 防止无限循环,最多查询365天
            if streak >= 365:
                break
        
        return streak

    @staticmethod
    def _calculate_longest_streak(db: Session, user_id: str, days: int) -> int:
        """
        计算指定天数内的最长连续签到天数
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数
            
        Returns:
            最长连续签到天数
        """
        # 获取指定天数内的所有签到记录
        checkins = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.checkin_date >= (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
            )
        ).order_by(CheckIn.checkin_date).all()
        
        if not checkins:
            return 0
        
        # 提取签到日期列表
        checkin_dates = sorted([c.checkin_date for c in checkins])
        
        longest_streak = 1
        current_streak = 1
        
        # 遍历签到日期,计算最长连续签到
        for i in range(1, len(checkin_dates)):
            prev_date = datetime.strptime(checkin_dates[i-1], '%Y-%m-%d').date()
            curr_date = datetime.strptime(checkin_dates[i], '%Y-%m-%d').date()
            
            if (curr_date - prev_date).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return longest_streak
