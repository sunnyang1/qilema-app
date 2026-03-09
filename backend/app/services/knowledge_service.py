"""
急救知识库服务

提供急救知识文章、分类和标签的CRUD操作和搜索功能
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import markdown
from app.core.cache_config import CacheConfig
from app.models.knowledge_base import KnowledgeArticle, KnowledgeCategory, KnowledgeTag
from app.services.base_service import BaseService
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session


class KnowledgeCategoryService(BaseService[KnowledgeCategory]):
    """知识库分类服务"""

    model_class = KnowledgeCategory
    cache_prefix = CacheConfig.PREFIX_KNOWLEDGE_CATEGORY
    cache_ttl = CacheConfig.TTL_KNOWLEDGE_LIST

    @classmethod
    def get_active_categories(
        cls, db: Session, parent_id: Optional[int] = None
    ) -> List[KnowledgeCategory]:
        """获取启用的分类列表

        Args:
            db: 数据库会话
            parent_id: 父分类ID，None表示获取顶级分类

        Returns:
            分类列表
        """
        query = db.query(KnowledgeCategory).filter(KnowledgeCategory.is_active)

        if parent_id is None:
            query = query.filter(KnowledgeCategory.parent_id.is_(None))
        else:
            query = query.filter(KnowledgeCategory.parent_id == parent_id)

        return query.order_by(KnowledgeCategory.sort_order.asc()).all()

    @classmethod
    def get_category_tree(cls, db: Session) -> List[Dict[str, Any]]:
        """获取分类树

        Args:
            db: 数据库会话

        Returns:
            分类树列表
        """
        # 获取所有顶级分类
        root_categories = cls.get_active_categories(db, parent_id=None)

        tree = []
        for category in root_categories:
            tree.append(category.to_dict(include_children=True))

        return tree

    @classmethod
    def create_category(cls, db: Session, data: Dict[str, Any]) -> KnowledgeCategory:
        """创建分类

        Args:
            db: 数据库会话
            data: 分类数据

        Returns:
            创建的分类对象
        """
        category = cls.create_record(db, data)

        # 清除列表缓存
        cls.invalidate_list_cache()

        return category

    @classmethod
    def update_category(
        cls, db: Session, category_id: int, data: Dict[str, Any]
    ) -> Optional[KnowledgeCategory]:
        """更新分类

        Args:
            db: 数据库会话
            category_id: 分类ID
            data: 更新数据

        Returns:
            更新后的分类对象或None
        """
        category = cls.update_record(db, category_id, data)

        if category:
            # 清除缓存
            cls.invalidate_record_cache(category_id)
            cls.invalidate_list_cache()

        return category


class KnowledgeTagService(BaseService[KnowledgeTag]):
    """知识库标签服务"""

    model_class = KnowledgeTag
    cache_prefix = CacheConfig.PREFIX_KNOWLEDGE_TAG
    cache_ttl = CacheConfig.TTL_KNOWLEDGE_LIST

    @classmethod
    def get_active_tags(cls, db: Session) -> List[KnowledgeTag]:
        """获取启用的标签列表

        Args:
            db: 数据库会话

        Returns:
            标签列表
        """
        return (
            db.query(KnowledgeTag)
            .filter(KnowledgeTag.is_active)
            .order_by(KnowledgeTag.name.asc())
            .all()
        )

    @classmethod
    def get_or_create_tag(cls, db: Session, name: str) -> KnowledgeTag:
        """获取或创建标签

        Args:
            db: 数据库会话
            name: 标签名称

        Returns:
            标签对象
        """
        tag = db.query(KnowledgeTag).filter(KnowledgeTag.name == name).first()

        if not tag:
            tag = KnowledgeTag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

            # 清除缓存
            cls.invalidate_list_cache()

        return tag

    @classmethod
    def search_tags(
        cls, db: Session, keyword: str, limit: int = 10
    ) -> List[KnowledgeTag]:
        """搜索标签

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            limit: 限制数量

        Returns:
            标签列表
        """
        return (
            db.query(KnowledgeTag)
            .filter(
                and_(
                    KnowledgeTag.is_active.is_(True),
                    KnowledgeTag.name.ilike(f"%{keyword}%"),
                )
            )
            .limit(limit)
            .all()
        )


class KnowledgeArticleService(BaseService[KnowledgeArticle]):
    """知识库文章服务"""

    model_class = KnowledgeArticle
    cache_prefix = CacheConfig.PREFIX_KNOWLEDGE_ARTICLE
    cache_ttl = CacheConfig.TTL_KNOWLEDGE_DETAIL

    @classmethod
    def get_published_articles(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        tag_names: Optional[List[str]] = None,
    ) -> List[KnowledgeArticle]:
        """获取已发布的文章列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            category_id: 分类ID筛选
            tag_names: 标签名称列表筛选

        Returns:
            文章列表
        """
        query = db.query(KnowledgeArticle).filter(
            and_(
                KnowledgeArticle.is_active.is_(True),
                KnowledgeArticle.status == "published",
            )
        )

        # 分类筛选
        if category_id:
            query = query.filter(KnowledgeArticle.category_id == category_id)

        # 标签筛选
        if tag_names:
            for tag_name in tag_names:
                query = query.filter(
                    KnowledgeArticle.tags.any(KnowledgeTag.name == tag_name)
                )

        # 排序：置顶优先，然后按发布时间倒序
        query = query.order_by(
            desc(KnowledgeArticle.is_top), desc(KnowledgeArticle.published_at)
        )

        return query.offset(skip).limit(limit).all()

    @classmethod
    def search_articles(
        cls, db: Session, keyword: str, skip: int = 0, limit: int = 20
    ) -> List[KnowledgeArticle]:
        """搜索文章

        Args:
            db: 数据库会话
            keyword: 搜索关键词
            skip: 跳过数量
            limit: 限制数量

        Returns:
            文章列表
        """
        search_pattern = f"%{keyword}%"

        return (
            db.query(KnowledgeArticle)
            .filter(
                and_(
                    KnowledgeArticle.is_active.is_(True),
                    KnowledgeArticle.status == "published",
                    or_(
                        KnowledgeArticle.title.ilike(search_pattern),
                        KnowledgeArticle.summary.ilike(search_pattern),
                        KnowledgeArticle.content.ilike(search_pattern),
                    ),
                )
            )
            .order_by(desc(KnowledgeArticle.published_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_article_detail(
        cls, db: Session, article_id: int
    ) -> Optional[KnowledgeArticle]:
        """获取文章详情

        Args:
            db: 数据库会话
            article_id: 文章ID

        Returns:
            文章对象或None
        """
        article = (
            db.query(KnowledgeArticle)
            .filter(
                and_(
                    KnowledgeArticle.id == article_id,
                    KnowledgeArticle.is_active.is_(True),
                    KnowledgeArticle.status == "published",
                )
            )
            .first()
        )

        if article:
            # 增加浏览次数
            article.increment_view_count()
            db.commit()

        return article

    @classmethod
    def create_article(cls, db: Session, data: Dict[str, Any]) -> KnowledgeArticle:
        """创建文章

        Args:
            db: 数据库会话
            data: 文章数据

        Returns:
            创建的文章对象
        """
        # 处理标签
        tag_names = data.pop("tag_names", [])

        # 渲染Markdown为HTML
        if "content" in data and data["content"]:
            data["html_content"] = markdown.markdown(
                data["content"], extensions=["tables", "fenced_code"]
            )

        # 设置发布时间
        if data.get("status") == "published" and not data.get("published_at"):
            data["published_at"] = datetime.utcnow()

        # 创建文章
        article = cls.create_record(db, data)

        # 添加标签
        if tag_names:
            for tag_name in tag_names:
                tag = KnowledgeTagService.get_or_create_tag(db, tag_name)
                article.tags.append(tag)
            db.commit()
            db.refresh(article)

        # 清除缓存
        cls.invalidate_list_cache()

        return article

    @classmethod
    def update_article(
        cls, db: Session, article_id: int, data: Dict[str, Any]
    ) -> Optional[KnowledgeArticle]:
        """更新文章

        Args:
            db: 数据库会话
            article_id: 文章ID
            data: 更新数据

        Returns:
            更新后的文章对象或None
        """
        article = cls.get_by_id(db, article_id)
        if not article:
            return None

        # 处理标签
        tag_names = data.pop("tag_names", None)

        # 重新渲染Markdown
        if "content" in data and data["content"]:
            data["html_content"] = markdown.markdown(
                data["content"], extensions=["tables", "fenced_code"]
            )

        # 设置发布时间
        if data.get("status") == "published" and article.status != "published":
            data["published_at"] = datetime.utcnow()

        # 更新文章
        article = cls.update_record(db, article_id, data)

        # 更新标签
        if tag_names is not None and article:
            article.tags.clear()
            for tag_name in tag_names:
                tag = KnowledgeTagService.get_or_create_tag(db, tag_name)
                article.tags.append(tag)
            db.commit()
            db.refresh(article)

        if article:
            # 清除缓存
            cls.invalidate_record_cache(article_id)
            cls.invalidate_list_cache()

        return article

    @classmethod
    def delete_article(cls, db: Session, article_id: int) -> bool:
        """删除文章

        Args:
            db: 数据库会话
            article_id: 文章ID

        Returns:
            是否成功删除
        """
        result = cls.delete_record(db, article_id)

        if result:
            # 清除缓存
            cls.invalidate_list_cache()

        return result

    @classmethod
    def increment_like(cls, db: Session, article_id: int) -> bool:
        """增加文章点赞数

        Args:
            db: 数据库会话
            article_id: 文章ID

        Returns:
            是否成功
        """
        article = cls.get_by_id(db, article_id)
        if not article:
            return False

        article.increment_like_count()
        db.commit()

        # 清除缓存
        cls.invalidate_record_cache(article_id)

        return True

    @classmethod
    def get_related_articles(
        cls, db: Session, article_id: int, limit: int = 5
    ) -> List[KnowledgeArticle]:
        """获取相关文章

        基于相同分类和标签获取相关文章

        Args:
            db: 数据库会话
            article_id: 文章ID
            limit: 限制数量

        Returns:
            相关文章列表
        """
        article = cls.get_by_id(db, article_id)
        if not article:
            return []

        # 获取相同分类的其他文章
        query = db.query(KnowledgeArticle).filter(
            and_(
                KnowledgeArticle.id != article_id,
                KnowledgeArticle.is_active.is_(True),
                KnowledgeArticle.status == "published",
            )
        )

        # 优先相同分类
        if article.category_id:
            query = query.filter(KnowledgeArticle.category_id == article.category_id)

        # 然后按标签匹配度排序
        if article.tags:
            tag_ids = [tag.id for tag in article.tags]
            # 这里简化处理，实际可以计算标签匹配数量
            query = query.filter(
                KnowledgeArticle.tags.any(KnowledgeTag.id.in_(tag_ids))
            )

        return query.order_by(desc(KnowledgeArticle.published_at)).limit(limit).all()


class KnowledgeBaseService:
    """知识库综合服务（提供统一入口）"""

    category_service = KnowledgeCategoryService
    tag_service = KnowledgeTagService
    article_service = KnowledgeArticleService

    @classmethod
    def get_homepage_data(cls, db: Session) -> Dict[str, Any]:
        """获取首页数据

        Args:
            db: 数据库会话

        Returns:
            首页数据字典
        """
        # 获取分类树
        categories = cls.category_service.get_category_tree(db)

        # 获取置顶文章
        top_articles = (
            db.query(KnowledgeArticle)
            .filter(
                and_(
                    KnowledgeArticle.is_active.is_(True),
                    KnowledgeArticle.status == "published",
                    KnowledgeArticle.is_top.is_(True),
                )
            )
            .order_by(desc(KnowledgeArticle.published_at))
            .limit(5)
            .all()
        )

        # 获取最新文章
        latest_articles = cls.article_service.get_published_articles(db, limit=10)

        # 获取热门标签
        popular_tags = (
            db.query(KnowledgeTag).filter(KnowledgeTag.is_active).limit(20).all()
        )

        return {
            "categories": categories,
            "top_articles": [a.to_dict() for a in top_articles],
            "latest_articles": [a.to_dict() for a in latest_articles],
            "popular_tags": [t.to_dict() for t in popular_tags],
        }
