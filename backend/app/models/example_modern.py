"""
SQLAlchemy 2.x 风格的模型示例

展示 SQLAlchemy 2.0 新特性：
1. Mapped[] 类型注解
2. mapped_column() 替代 Column()
3. 使用 relationship() 的 typing 支持

参考: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
"""

import enum
from datetime import datetime
from typing import List, Optional

from app.models.base_mixin import BaseModelMixin
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ModernUser(Base, BaseModelMixin):
    """
    SQLAlchemy 2.x 风格的用户模型
    
    关键变化:
    1. 使用 Mapped[] 类型注解声明字段类型
    2. 使用 mapped_column() 替代 Column()
    3. 类型检查器可以正确推断字段类型
    """
    
    __tablename__ = "modern_users"
    
    # SQLAlchemy 2.x: 使用 Mapped[] 类型注解
    # mapped_column() 替代 Column()
    
    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        comment="用户唯一标识"
    )
    
    phone: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        index=True,
        nullable=False,
        comment="手机号"
    )
    
    # Optional[] 表示可空字段
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称"
    )
    
    # Enum 类型
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        comment="用户状态"
    )
    
    # 数值类型
    age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="年龄"
    )
    
    # 日期时间类型 - SQLAlchemy 2.x 支持更好的类型推断
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="创建时间"
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )
    
    # ===== 关联关系 =====
    
    # SQLAlchemy 2.x: relationship 返回 Mapped[List[T]] 或 Mapped[T]
    # 一对多关系
    posts: Mapped[List["ModernPost"]] = relationship(
        "ModernPost",
        back_populates="author",
        cascade="all, delete-orphan",
        # SQLAlchemy 2.x: lazy loading 默认行为可以配置
        lazy="selectin",  # 使用 selectin loading 优化 N+1 问题
    )
    
    # 一对一关系
    profile: Mapped[Optional["ModernUserProfile"]] = relationship(
        "ModernUserProfile",
        back_populates="user",
        uselist=False,
        lazy="joined",  # 立即加载一对一关系
    )
    
    def __repr__(self) -> str:
        """SQLAlchemy 2.x: 推荐添加类型注解"""
        return f"<ModernUser(user_id={self.user_id}, phone={self.phone})>"


class ModernPost(Base, BaseModelMixin):
    """
    SQLAlchemy 2.x 风格的帖子模型
    """
    
    __tablename__ = "modern_posts"
    
    post_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="帖子ID"
    )
    
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="标题"
    )
    
    content: Mapped[Optional[str]] = mapped_column(
        String(5000),
        nullable=True,
        comment="内容"
    )
    
    # 外键 - SQLAlchemy 2.x 使用 mapped_column(ForeignKey(...))
    author_id: Mapped[str] = mapped_column(
        ForeignKey("modern_users.user_id"),
        nullable=False,
        comment="作者ID"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="创建时间"
    )
    
    # 关联关系
    author: Mapped[ModernUser] = relationship(
        "ModernUser",
        back_populates="posts",
    )
    
    def __repr__(self) -> str:
        return f"<ModernPost(post_id={self.post_id}, title={self.title})>"


class ModernUserProfile(Base, BaseModelMixin):
    """
    SQLAlchemy 2.x 风格的用户资料模型（一对一关系示例）
    """
    
    __tablename__ = "modern_user_profiles"
    
    profile_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="资料ID"
    )
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("modern_users.user_id"),
        unique=True,  # 一对一关系需要 unique
        nullable=False,
        comment="用户ID"
    )
    
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="个人简介"
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="头像URL"
    )
    
    # 关联关系
    user: Mapped[ModernUser] = relationship(
        "ModernUser",
        back_populates="profile",
    )


# ===== SQLAlchemy 2.x 查询示例 =====

"""
# 传统 SQLAlchemy 1.x 查询方式:
users = db.query(ModernUser).filter(ModernUser.status == UserStatus.ACTIVE).all()

# SQLAlchemy 2.x 新的查询方式（推荐）:
from sqlalchemy import select

# 使用 select() 构造查询
stmt = select(ModernUser).where(ModernUser.status == UserStatus.ACTIVE)
result = db.execute(stmt)
users = result.scalars().all()

# 或者使用新的 Session.get() 方式
user = db.get(ModernUser, user_id)

# 使用 QueryBuilder（项目自定义）
from app.core.query_builder import QueryBuilder

builder = QueryBuilder(select(ModernUser), ModernUser)
users = (
    builder.filter(status=UserStatus.ACTIVE)
    .order_by("created_at", desc=True)
    .paginate(page=1, per_page=20)
    .execute()
)
"""

# ===== SQLAlchemy 2.x 与 Pydantic v2 集成 =====

"""
from pydantic import BaseModel

class ModernUserResponse(BaseModel):
    user_id: str
    phone: str
    nickname: Optional[str]
    status: UserStatus
    created_at: datetime
    
    model_config = {"from_attributes": True}  # 启用 ORM 模式

# 从 ORM 模型转换为 Pydantic 模型
user = db.get(ModernUser, user_id)
response = ModernUserResponse.model_validate(user)  # Pydantic v2
"""
