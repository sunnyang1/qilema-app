"""
用户设置SQLAlchemy模型
"""

from app.core.database import Base
from app.models.base_mixin import BaseModelMixin
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship as db_relationship


class UserSetting(Base, BaseModelMixin):
    """用户设置模型"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    user_id = Column(
        String(36),
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
        index=True,
        comment="用户ID",
    )
    language = Column(String(10), nullable=False, default="zh-CN", comment="语言")
    region = Column(String(10), nullable=False, default="CN", comment="地区")
    share_profile = Column(
        Integer, nullable=False, default=1, comment="是否分享个人资料: 0=否 1=是"
    )
    share_location = Column(
        Integer, nullable=False, default=1, comment="是否分享位置: 0=否 1=是"
    )
    allow_analytics = Column(
        Integer, nullable=False, default=1, comment="是否允许数据分析: 0=否 1=是"
    )
    theme = Column(
        String(10), nullable=False, default="light", comment="主题: light/dark/auto"
    )
    font_size = Column(
        String(10),
        nullable=False,
        default="medium",
        comment="字体大小: small/medium/large",
    )
    extra_settings = Column(JSON, nullable=True, comment="其他设置")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(),
        comment="创建时间",
    )
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关系
    user = db_relationship("User", back_populates="user_setting")
