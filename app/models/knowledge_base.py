"""
急救知识库模型

提供急救知识文章、分类和标签管理功能
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


# 文章-标签关联表
article_tag_association = Table(
    'article_tag',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('knowledge_articles.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('knowledge_tags.id'), primary_key=True)
)


class KnowledgeCategory(Base):
    """知识库分类模型"""
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    description = Column(String(500), comment="分类描述")
    icon = Column(String(200), comment="分类图标URL")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    parent_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=True, comment="父分类ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    articles = relationship("KnowledgeArticle", back_populates="category")
    parent = relationship("KnowledgeCategory", remote_side=[id], back_populates="children")
    children = relationship("KnowledgeCategory", back_populates="parent", lazy="dynamic")

    def __repr__(self):
        return f"<KnowledgeCategory(id={self.id}, name={self.name})>"

    def to_dict(self, include_children: bool = False) -> dict:
        """转换为字典"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "article_count": len(self.articles) if self.articles else 0
        }
        
        if include_children and self.children:
            data["children"] = [child.to_dict() for child in self.children if child.is_active]
        
        return data


class KnowledgeTag(Base):
    """知识库标签模型"""
    __tablename__ = "knowledge_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    description = Column(String(200), comment="标签描述")
    color = Column(String(7), default="#1890ff", comment="标签颜色（十六进制）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    articles = relationship(
        "KnowledgeArticle",
        secondary=article_tag_association,
        back_populates="tags"
    )

    def __repr__(self):
        return f"<KnowledgeTag(id={self.id}, name={self.name})>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "article_count": len(self.articles) if self.articles else 0
        }


class KnowledgeArticle(Base):
    """知识库文章模型"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="文章标题")
    summary = Column(String(500), comment="文章摘要")
    content = Column(Text, nullable=False, comment="文章内容（Markdown格式）")
    html_content = Column(Text, comment="HTML格式的内容（预渲染）")
    cover_image = Column(String(500), comment="封面图片URL")
    author = Column(String(100), comment="作者")
    source = Column(String(200), comment="文章来源")
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞次数")
    is_top = Column(Boolean, default=False, comment="是否置顶")
    is_active = Column(Boolean, default=True, comment="是否启用")
    status = Column(String(20), default="published", comment="状态：draft草稿/published已发布/archived已归档")
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), comment="分类ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    published_at = Column(DateTime, comment="发布时间")

    # 关联关系
    category = relationship("KnowledgeCategory", back_populates="articles")
    tags = relationship(
        "KnowledgeTag",
        secondary=article_tag_association,
        back_populates="articles"
    )

    def __repr__(self):
        return f"<KnowledgeArticle(id={self.id}, title={self.title})>"

    def to_dict(self, include_content: bool = False) -> dict:
        """转换为字典"""
        data = {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "cover_image": self.cover_image,
            "author": self.author,
            "source": self.source,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "is_top": self.is_top,
            "is_active": self.is_active,
            "status": self.status,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "tags": [tag.name for tag in self.tags] if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
        
        if include_content:
            data["content"] = self.content
            data["html_content"] = self.html_content
        
        return data

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1

    def increment_like_count(self):
        """增加点赞次数"""
        self.like_count += 1
