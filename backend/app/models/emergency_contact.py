"""
紧急联系人SQLAlchemy模型
"""

from typing import List, Optional

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship as db_relationship


class EmergencyContact(Base, BaseModelMixin):
    """紧急联系人模型"""

    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )
    user_id = Column(
        String(36), ForeignKey("users.user_id"), nullable=False, index=True
    )
    name = Column(String(50), nullable=False, comment="联系人姓名")
    phone = Column(String(20), nullable=False, comment="联系人电话")
    relationship = Column(String(20), nullable=True, comment="与用户关系")
    is_primary = Column(Integer, nullable=False, default=0, comment="是否主要联系人: 0=否 1=是")
    priority = Column(Integer, nullable=False, default=1, comment="通知优先级")
    notify_channels = Column(JSON, nullable=True, comment="通知渠道")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="emergency_contacts")

    def to_dict(
        self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None
    ) -> dict:
        """
        转换为字典

        Args:
            exclude: 要排除的字段列表
            include: 只包含的字段列表

        Returns:
            dict: 紧急联系人的字典表示
        """
        return super().to_dict(exclude=exclude, include=include)
