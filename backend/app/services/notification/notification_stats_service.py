"""
通知统计服务

负责通知相关的统计查询
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.notification_model import Notification
from app.schemas.notification import (
    NotificationChannelEnum,
    NotificationStatistics,
    NotificationStatusEnum,
    NotificationTypeEnum,
)


class NotificationStatsService:
    """
    通知统计服务

    负责通知相关的统计查询：
    - 通知发送统计
    - 按类型、渠道、状态统计
    - 未读数量统计
    - 时间范围统计

    使用示例:
        >>> service = NotificationStatsService()
        >>> stats = service.get_statistics(db, user_id, start_date, end_date)
        >>> count = service.get_unread_count(db, user_id)
    """

    def __init__(self):
        """初始化统计服务"""
        pass

    def get_statistics(
        self,
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> NotificationStatistics:
        """
        获取通知统计数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            NotificationStatistics: 统计结果
        """
        notifications = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.created_at >= start_date,
                Notification.created_at <= end_date,
            )
            .all()
        )

        # 统计总数
        total_sent = len(
            [n for n in notifications if n.status == NotificationStatusEnum.SENT]
        )
        total_delivered = len(
            [n for n in notifications if n.status == NotificationStatusEnum.DELIVERED]
        )
        total_read = len([n for n in notifications if n.read_at is not None])
        total_failed = len(
            [n for n in notifications if n.status == NotificationStatusEnum.FAILED]
        )

        # 按类型统计
        checkin_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.CHECKIN
            ]
        )
        alert_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.ALERT
            ]
        )
        sos_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.SOS
            ]
        )
        system_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.SYSTEM
            ]
        )
        health_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.HEALTH
            ]
        )
        device_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.DEVICE
            ]
        )
        reminder_count = len(
            [
                n
                for n in notifications
                if n.notification_type == NotificationTypeEnum.REMINDER
            ]
        )

        # 未读数量
        unread_count = len([n for n in notifications if n.read_at is None])

        return NotificationStatistics(
            user_id=user_id,
            stat_date=start_date.strftime("%Y-%m-%d"),
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_read=total_read,
            total_failed=total_failed,
            unread_count=unread_count,
            checkin_count=checkin_count,
            alert_count=alert_count,
            sos_count=sos_count,
            system_count=system_count,
            health_count=health_count,
            device_count=device_count,
            reminder_count=reminder_count,
        )

    def get_unread_count(self, db: Session, user_id: str) -> int:
        """
        获取未读通知数量

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            int: 未读通知数量
        """
        count = (
            db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
            .scalar()
        )
        return count or 0

    def get_count_by_status(
        self,
        db: Session,
        user_id: str,
        status: NotificationStatusEnum,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        获取指定状态的通知数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 通知状态
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            int: 通知数量
        """
        query = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.status == status,
        )

        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)

        return query.scalar() or 0

    def get_count_by_type(
        self,
        db: Session,
        user_id: str,
        notification_type: NotificationTypeEnum,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        获取指定类型的通知数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            notification_type: 通知类型
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            int: 通知数量
        """
        query = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.notification_type == notification_type,
        )

        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)

        return query.scalar() or 0

    def get_count_by_channel(
        self,
        db: Session,
        user_id: str,
        channel: NotificationChannelEnum,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        获取指定渠道的通知数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            channel: 通知渠道
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            int: 通知数量
        """
        query = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.channel == channel,
        )

        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)

        return query.scalar() or 0

    def get_daily_statistics(
        self,
        db: Session,
        user_id: str,
        days: int = 7,
    ) -> List[Dict[str, any]]:
        """
        获取每日通知统计

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 统计天数，默认7天

        Returns:
            list: 每日统计数据列表
        """
        from datetime import timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # 按日期分组统计
        results = (
            db.query(
                func.date(Notification.created_at).label("date"),
                func.count(Notification.id).label("total"),
                func.sum(
                    func.case(
                        (Notification.status == NotificationStatusEnum.SENT, 1),
                        else_=0,
                    )
                ).label("sent"),
                func.sum(
                    func.case(
                        (Notification.status == NotificationStatusEnum.DELIVERED, 1),
                        else_=0,
                    )
                ).label("delivered"),
                func.sum(
                    func.case(
                        (Notification.status == NotificationStatusEnum.FAILED, 1),
                        else_=0,
                    )
                ).label("failed"),
                func.sum(
                    func.case((Notification.read_at.isnot(None), 1), else_=0)
                ).label("read"),
            )
            .filter(
                Notification.user_id == user_id,
                Notification.created_at >= start_date,
                Notification.created_at <= end_date,
            )
            .group_by(func.date(Notification.created_at))
            .order_by(func.date(Notification.created_at))
            .all()
        )

        return [
            {
                "date": str(result.date),
                "total": result.total,
                "sent": result.sent or 0,
                "delivered": result.delivered or 0,
                "failed": result.failed or 0,
                "read": result.read or 0,
            }
            for result in results
        ]

    def get_channel_statistics(
        self,
        db: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Dict[str, int]]:
        """
        获取各渠道的通知统计

        Args:
            db: 数据库会话
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            dict: 各渠道统计数据
        """
        query = db.query(
            Notification.channel,
            func.count(Notification.id).label("total"),
            func.sum(
                func.case(
                    (Notification.status == NotificationStatusEnum.SENT, 1),
                    else_=0,
                )
            ).label("sent"),
            func.sum(
                func.case(
                    (Notification.status == NotificationStatusEnum.DELIVERED, 1),
                    else_=0,
                )
            ).label("delivered"),
            func.sum(
                func.case(
                    (Notification.status == NotificationStatusEnum.FAILED, 1),
                    else_=0,
                )
            ).label("failed"),
        ).filter(Notification.user_id == user_id)

        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)

        results = query.group_by(Notification.channel).all()

        return {
            result.channel: {
                "total": result.total,
                "sent": result.sent or 0,
                "delivered": result.delivered or 0,
                "failed": result.failed or 0,
            }
            for result in results
        }
