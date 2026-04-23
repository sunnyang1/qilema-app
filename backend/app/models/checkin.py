"""
签到打卡数据模型 (SQLAlchemy 2.x)

记录用户的每日签到记录,用于确认用户安全状态
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base_mixin import BaseModelMixin

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class CheckIn(Base, BaseModelMixin):
    """签到记录表 (SQLAlchemy 2.x)"""

    __tablename__ = "checkins"

    # 复合索引: 用户ID + 签到日期(确保每天只能签到一次)
    __table_args__ = (
        Index("ix_checkins_user_date", "user_id", "checkin_date", unique=True),
        Index(
            "idx_checkins_user_created", "user_id", desc("created_at")
        ),  # For user checkin history queries (DESC for recent first)
        Index("idx_checkins_status", "status"),  # For filtering by status
    )

    # 主键
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )

    # 外键关联用户
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 签到时间戳
    checkin_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # 签到日期(用于快速查询某天的签到状态)
    checkin_date: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )  # 格式: YYYY-MM-DD

    # 签到位置(可选)
    latitude: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # 签到方式: 'manual'手动签到, 'auto'自动签到(智能设备)
    checkin_method: Mapped[str] = mapped_column(
        String(10), nullable=False, default="manual"
    )

    # 状态: 'active', 'missed', 'late' 等
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 备注信息
    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # 关联用户 - CheckIn.user is frequently accessed, use lazy='joined' for immediate loading
    user: Mapped["User"] = relationship(
        "User", back_populates="checkins", lazy="joined"
    )

    @validates("checkin_date")
    def validate_checkin_date(self, key: str, date: str) -> str:
        """验证签到日期格式 (YYYY-MM-DD)"""
        if not date:
            raise ValueError("签到日期不能为空")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise ValueError(f"无效的日期格式: {date}, 期望格式: YYYY-MM-DD")
        return date

    @validates("checkin_method")
    def validate_checkin_method(self, key: str, method: str) -> str:
        """验证签到方式"""
        valid_methods = {"manual", "auto", "device", "app"}
        if method not in valid_methods:
            raise ValueError(f"无效的签到方式: {method}, 必须是: {valid_methods}")
        return method

    @validates("status")
    def validate_status(self, key: str, status: str) -> str:
        """验证签到状态"""
        valid_statuses = {"active", "missed", "late", "early", "disabled"}
        if status not in valid_statuses:
            raise ValueError(f"无效的状态: {status}, 必须是: {valid_statuses}")
        return status

    @validates("notes")
    def validate_notes(self, key: str, notes: Optional[str]) -> Optional[str]:
        """验证备注长度"""
        if notes and len(notes) > 200:
            raise ValueError("备注长度不能超过200个字符")
        return notes

    def __repr__(self) -> str:
        return (
            f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.checkin_date})>"
        )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """转换为字典格式"""
        return super().to_dict(exclude=exclude, include=include)
