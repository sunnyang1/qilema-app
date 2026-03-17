"""
签到打卡数据模型 (SQLAlchemy 2.x)

记录用户的每日签到记录,用于确认用户安全状态
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class CheckIn(Base, BaseModelMixin):
    """签到记录表 (SQLAlchemy 2.x)"""

    __tablename__ = "checkins"

    # 复合索引: 用户ID + 签到日期(确保每天只能签到一次)
    __table_args__ = (
        Index("ix_checkins_user_date", "user_id", "checkin_date", unique=True),
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

    # 备注信息
    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # 关联用户
    user: Mapped["User"] = relationship("User", back_populates="checkins")

    def __repr__(self) -> str:
        return (
            f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.checkin_date})>"
        )

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """转换为字典格式"""
        return super().to_dict(exclude=exclude, include=include)
