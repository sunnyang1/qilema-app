"""
急救知识库服务测试

测试知识库文章、分类和标签的CRUD操作和搜索功能
"""

from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeArticle, KnowledgeCategory, KnowledgeTag
from app.services.knowledge_service import (
    KnowledgeArticleService,
    KnowledgeBaseService,
    KnowledgeCategoryService,
    KnowledgeTagService,
)


class TestKnowledgeCategoryService:
    """测试知识库分类服务"""

    def test_create_category(self, db: Session):
        """测试创建分类"""
        data = {
            "name": "急救指南",
            "description": "各种急救场景的操作指南",
            "icon": "https://example.com/icon.png",
            "sort_order": 1,
        }

        category = KnowledgeCategoryService.create_category(db, data)

        assert category.id is not None
        assert category.name == "急救指南"
        assert category.description == "各种急救场景的操作指南"
        assert category.is_active is True

    def test_get_category_by_id(self, db: Session):
        """测试根据ID获取分类"""
        # 先创建分类
        data = {"name": "心肺复苏", "sort_order": 2}
        category = KnowledgeCategoryService.create_category(db, data)

        # 再获取
        found = KnowledgeCategoryService.get_by_id(db, category.id)

        assert found is not None
        assert found.name == "心肺复苏"

    def test_get_active_categories(self, db: Session):
        """测试获取启用的分类列表"""
        # 创建多个分类
        KnowledgeCategoryService.create_category(db, {"name": "分类1", "is_active": True})
        KnowledgeCategoryService.create_category(
            db, {"name": "分类2", "is_active": False}
        )

        categories = KnowledgeCategoryService.get_active_categories(db)

        assert len(categories) >= 1
        assert all(c.is_active for c in categories)

    def test_get_category_tree(self, db: Session):
        """测试获取分类树"""
        # 创建父分类
        parent = KnowledgeCategoryService.create_category(db, {"name": "急救基础"})

        # 创建子分类
        KnowledgeCategoryService.create_category(
            db, {"name": "基础常识", "parent_id": parent.id}
        )
        KnowledgeCategoryService.create_category(
            db, {"name": "基本操作", "parent_id": parent.id}
        )

        tree = KnowledgeCategoryService.get_category_tree(db)

        assert len(tree) > 0
        # 检查是否有子分类
        root_categories = [t for t in tree if t.get("parent_id") is None]
        assert len(root_categories) > 0

    def test_update_category(self, db: Session):
        """测试更新分类"""
        category = KnowledgeCategoryService.create_category(db, {"name": "旧名称"})

        updated = KnowledgeCategoryService.update_category(
            db, category.id, {"name": "新名称"}
        )

        assert updated is not None
        assert updated.name == "新名称"

    def test_to_dict(self, db: Session):
        """测试分类转换为字典"""
        category = KnowledgeCategoryService.create_category(
            db, {"name": "测试分类", "description": "测试描述"}
        )

        data = category.to_dict()

        assert data["name"] == "测试分类"
        assert data["description"] == "测试描述"
        assert "created_at" in data


class TestKnowledgeTagService:
    """测试知识库标签服务"""

    def test_create_tag(self, db: Session):
        """测试创建标签"""
        data = {"name": "心肺复苏", "description": "CPR相关内容", "color": "#ff0000"}
        tag = KnowledgeTagService.create_record(db, data)

        assert tag.id is not None
        assert tag.name == "心肺复苏"
        assert tag.color == "#ff0000"

    def test_get_or_create_tag(self, db: Session):
        """测试获取或创建标签"""
        # 第一次创建
        tag1 = KnowledgeTagService.get_or_create_tag(db, "新标签")
        assert tag1.id is not None

        # 第二次获取
        tag2 = KnowledgeTagService.get_or_create_tag(db, "新标签")
        assert tag2.id == tag1.id

    def test_search_tags(self, db: Session):
        """测试搜索标签"""
        KnowledgeTagService.create_record(db, {"name": "急救基础"})
        KnowledgeTagService.create_record(db, {"name": "急救进阶"})
        KnowledgeTagService.create_record(db, {"name": "健康知识"})

        results = KnowledgeTagService.search_tags(db, "急救", limit=10)

        assert len(results) >= 2
        assert all("急救" in r.name for r in results)

    def test_get_active_tags(self, db: Session):
        """测试获取启用的标签列表"""
        KnowledgeTagService.create_record(db, {"name": "标签1", "is_active": True})
        KnowledgeTagService.create_record(db, {"name": "标签2", "is_active": False})

        tags = KnowledgeTagService.get_active_tags(db)

        assert len(tags) >= 1
        assert all(t.is_active for t in tags)


class TestKnowledgeArticleService:
    """测试知识库文章服务"""

    def test_create_article(self, db: Session):
        """测试创建文章"""
        # 先创建分类
        category = KnowledgeCategoryService.create_category(db, {"name": "急救分类"})

        data = {
            "title": "心肺复苏操作指南",
            "content": "# 心肺复苏\n\n1. 确认现场安全\n2. 检查意识和呼吸",
            "summary": "CPR操作步骤",
            "author": "急救专家",
            "category_id": category.id,
            "status": "published",
        }

        article = KnowledgeArticleService.create_article(db, data)

        assert article.id is not None
        assert article.title == "心肺复苏操作指南"
        assert article.html_content is not None  # Markdown已渲染
        assert "<h1>" in article.html_content

    def test_create_article_with_tags(self, db: Session):
        """测试创建文章并添加标签"""
        data = {
            "title": "急救文章",
            "content": "文章内容",
            "tag_names": ["急救", "CPR"],
            "status": "published",
        }

        article = KnowledgeArticleService.create_article(db, data)

        assert len(article.tags) == 2
        tag_names = [t.name for t in article.tags]
        assert "急救" in tag_names
        assert "CPR" in tag_names

    def test_get_published_articles(self, db: Session):
        """测试获取已发布文章列表"""
        # 创建文章
        KnowledgeArticleService.create_article(
            db, {"title": "文章1", "content": "内容1", "status": "published"}
        )
        KnowledgeArticleService.create_article(
            db, {"title": "文章2", "content": "内容2", "status": "draft"}
        )

        articles = KnowledgeArticleService.get_published_articles(db)

        assert len(articles) >= 1
        assert all(a.status == "published" for a in articles)

    def test_search_articles(self, db: Session):
        """测试搜索文章"""
        KnowledgeArticleService.create_article(
            db,
            {
                "title": "心肺复苏指南",
                "content": "CPR操作步骤详解",
                "summary": "CPR指南",
                "status": "published",
            },
        )
        KnowledgeArticleService.create_article(
            db,
            {
                "title": "健康饮食习惯",
                "content": "如何保持健康饮食",
                "status": "published",
            },
        )

        results = KnowledgeArticleService.search_articles(db, "CPR")

        assert len(results) >= 1

    def test_get_article_detail(self, db: Session):
        """测试获取文章详情（增加浏览次数）"""
        article = KnowledgeArticleService.create_article(
            db, {"title": "测试文章", "content": "测试内容", "status": "published"}
        )
        initial_views = article.view_count

        # 获取详情
        found = KnowledgeArticleService.get_article_detail(db, article.id)

        assert found is not None
        assert found.view_count == initial_views + 1

    def test_update_article(self, db: Session):
        """测试更新文章"""
        article = KnowledgeArticleService.create_article(
            db, {"title": "旧标题", "content": "旧内容", "status": "draft"}
        )

        updated = KnowledgeArticleService.update_article(
            db, article.id, {"title": "新标题", "status": "published"}
        )

        assert updated is not None
        assert updated.title == "新标题"
        assert updated.status == "published"

    def test_increment_like(self, db: Session):
        """测试增加点赞数"""
        article = KnowledgeArticleService.create_article(
            db, {"title": "点赞测试", "content": "内容", "status": "published"}
        )
        initial_likes = article.like_count

        success = KnowledgeArticleService.increment_like(db, article.id)

        assert success is True
        assert article.like_count == initial_likes + 1

    def test_get_related_articles(self, db: Session):
        """测试获取相关文章"""
        category = KnowledgeCategoryService.create_category(db, {"name": "同分类"})

        article1 = KnowledgeArticleService.create_article(
            db,
            {
                "title": "文章1",
                "content": "内容1",
                "category_id": category.id,
                "status": "published",
            },
        )
        KnowledgeArticleService.create_article(
            db,
            {
                "title": "文章2",
                "content": "内容2",
                "category_id": category.id,
                "status": "published",
            },
        )

        related = KnowledgeArticleService.get_related_articles(db, article1.id, limit=5)

        assert len(related) >= 1

    def test_delete_article(self, db: Session):
        """测试删除文章"""
        article = KnowledgeArticleService.create_article(
            db, {"title": "待删除", "content": "内容", "status": "published"}
        )

        success = KnowledgeArticleService.delete_article(db, article.id)

        assert success is True
        assert KnowledgeArticleService.get_by_id(db, article.id) is None


class TestKnowledgeBaseService:
    """测试知识库综合服务"""

    def test_get_homepage_data(self, db: Session):
        """测试获取首页数据"""
        # 创建测试数据
        KnowledgeCategoryService.create_category(db, {"name": "首页分类"})
        KnowledgeArticleService.create_article(
            db,
            {
                "title": "置顶文章",
                "content": "内容",
                "is_top": True,
                "status": "published",
            },
        )

        data = KnowledgeBaseService.get_homepage_data(db)

        assert "categories" in data
        assert "top_articles" in data
        assert "latest_articles" in data
        assert "popular_tags" in data


class TestKnowledgeModels:
    """测试知识库模型"""

    def test_category_parent_child(self, db: Session):
        """测试分类父子关系"""
        parent = KnowledgeCategory(name="父分类")
        db.add(parent)
        db.commit()

        child = KnowledgeCategory(name="子分类", parent_id=parent.id)
        db.add(child)
        db.commit()

        # 刷新父对象以加载子对象
        db.refresh(parent)

        assert child.parent_id == parent.id
        assert child in parent.children

    def test_article_to_dict(self, db: Session):
        """测试文章转换为字典"""
        article = KnowledgeArticle(title="测试文章", content="测试内容", status="published")
        db.add(article)
        db.commit()

        data = article.to_dict()

        assert data["title"] == "测试文章"
        assert "content" not in data  # 默认不包含内容

        data_with_content = article.to_dict(include_content=True)
        assert "content" in data_with_content

    def test_article_tags_relationship(self, db: Session):
        """测试文章标签多对多关系"""
        article = KnowledgeArticle(title="文章", content="内容", status="published")
        tag1 = KnowledgeTag(name="标签1")
        tag2 = KnowledgeTag(name="标签2")

        article.tags.append(tag1)
        article.tags.append(tag2)

        db.add(article)
        db.commit()

        assert len(article.tags) == 2
        assert article in tag1.articles
        assert article in tag2.articles
