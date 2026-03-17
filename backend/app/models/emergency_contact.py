"""
紧急联系人SQLAlchemy模型 (SQLAlchemy 2.x)
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class EmergencyContact(Base, BaseModelMixin):
    """紧急联系人模型 (SQLAlchemy 2.x)"""

    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    contact_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="联系人姓名"
    )
    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="联系人电话"
    )
    relation: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="与用户关系"
    )
    is_primary: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="是否主要联系人"
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="通知优先级"
    )
    notify_channels: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True, comment="通知渠道"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="emergency_contacts")

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """转换为字典"""
        return super().to_dict(exclude=exclude, include=include)
