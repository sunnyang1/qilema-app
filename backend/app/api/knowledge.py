"""
急救知识库API路由

提供急救知识文章、分类和标签的REST API接口
使用 ApiResponseBuilder 统一构建响应
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response_builder import ApiResponseBuilder
from app.models.knowledge_base import KnowledgeArticle, KnowledgeCategory, KnowledgeTag
from app.services.knowledge_service import (
    KnowledgeBaseService,
    KnowledgeArticleService,
    KnowledgeCategoryService,
    KnowledgeTagService
)

router = APIRouter(tags=["急救知识库"])


# ========== 首页数据 ==========

@router.get("/homepage")
async def get_homepage_data(db: Session = Depends(get_db)):
    """获取知识库首页数据"""
    data = KnowledgeBaseService.get_homepage_data(db)
    return ApiResponseBuilder.success(data=data, message="获取首页数据成功")


# ========== 分类管理 ==========

@router.get("/categories")
async def list_categories(
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    categories = KnowledgeCategoryService.get_active_categories(db, parent_id)
    return ApiResponseBuilder.success(data=[c.to_dict() for c in categories], message="获取分类列表成功")


@router.get("/categories/tree")
async def get_category_tree(db: Session = Depends(get_db)):
    """获取分类树"""
    tree = KnowledgeCategoryService.get_category_tree(db)
    return ApiResponseBuilder.success(data=tree, message="获取分类树成功")


@router.get("/categories/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取分类详情"""
    category = KnowledgeCategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return ApiResponseBuilder.success(data=category.to_dict(include_children=True), message="获取分类详情成功")


@router.post("/categories")
async def create_category(
    name: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    sort_order: int = 0,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """创建分类（管理员功能）"""
    data = {
        "name": name,
        "description": description,
        "icon": icon,
        "sort_order": sort_order,
        "parent_id": parent_id
    }
    category = KnowledgeCategoryService.create_category(db, data)
    return ApiResponseBuilder.success(data=category.to_dict(), message="分类创建成功")


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    sort_order: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """更新分类（管理员功能）"""
    data = {k: v for k, v in {
        "name": name,
        "description": description,
        "icon": icon,
        "sort_order": sort_order,
        "is_active": is_active
    }.items() if v is not None}

    category = KnowledgeCategoryService.update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return ApiResponseBuilder.success(data=category.to_dict(), message="分类更新成功")


# ========== 标签管理 ==========

@router.get("/tags")
async def list_tags(
    keyword: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    if keyword:
        tags = KnowledgeTagService.search_tags(db, keyword, limit)
    else:
        tags = KnowledgeTagService.get_active_tags(db)
    return ApiResponseBuilder.success(data=[t.to_dict() for t in tags], message="获取标签列表成功")


@router.get("/tags/{tag_id}")
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    tag = KnowledgeTagService.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return ApiResponseBuilder.success(data=tag.to_dict(), message="获取标签详情成功")


@router.post("/tags")
async def create_tag(
    name: str,
    description: Optional[str] = None,
    color: str = "#1890ff",
    db: Session = Depends(get_db)
):
    """创建标签（管理员功能）"""
    data = {"name": name, "description": description, "color": color}
    tag = KnowledgeTagService.create_record(db, data)
    return ApiResponseBuilder.success(data=tag.to_dict(), message="标签创建成功")


# ========== 文章管理 ==========

@router.get("/articles")
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取文章列表"""
    tag_names = [tag] if tag else None
    articles = KnowledgeArticleService.get_published_articles(
        db, skip=skip, limit=limit, category_id=category_id, tag_names=tag_names
    )
    return ApiResponseBuilder.success(data=[a.to_dict() for a in articles], message="获取文章列表成功")


@router.get("/articles/search")
async def search_articles(
    keyword: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索文章"""
    articles = KnowledgeArticleService.search_articles(db, keyword, skip, limit)
    return ApiResponseBuilder.success(data=[a.to_dict() for a in articles], message="搜索文章成功")


@router.get("/articles/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情（增加浏览次数）"""
    article = KnowledgeArticleService.get_article_detail(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ApiResponseBuilder.success(data=article.to_dict(include_content=True), message="获取文章详情成功")


@router.get("/articles/{article_id}/related")
async def get_related_articles(
    article_id: int,
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """获取相关文章"""
    articles = KnowledgeArticleService.get_related_articles(db, article_id, limit)
    return ApiResponseBuilder.success(data=[a.to_dict() for a in articles], message="获取相关文章成功")


@router.post("/articles/{article_id}/like")
async def like_article(article_id: int, db: Session = Depends(get_db)):
    """点赞文章"""
    success = KnowledgeArticleService.increment_like(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ApiResponseBuilder.success(message="点赞成功")


@router.post("/articles")
async def create_article(
    title: str,
    content: str,
    summary: Optional[str] = None,
    cover_image: Optional[str] = None,
    author: Optional[str] = None,
    source: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_names: Optional[List[str]] = None,
    is_top: bool = False,
    status: str = "draft",
    db: Session = Depends(get_db)
):
    """创建文章（管理员功能）"""
    data = {
        "title": title,
        "content": content,
        "summary": summary,
        "cover_image": cover_image,
        "author": author,
        "source": source,
        "category_id": category_id,
        "tag_names": tag_names or [],
        "is_top": is_top,
        "status": status
    }
    article = KnowledgeArticleService.create_article(db, data)
    return ApiResponseBuilder.success(data=article.to_dict(), message="文章创建成功")


@router.put("/articles/{article_id}")
async def update_article(
    article_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    cover_image: Optional[str] = None,
    author: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_names: Optional[List[str]] = None,
    is_top: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新文章（管理员功能）"""
    data = {k: v for k, v in {
        "title": title,
        "content": content,
        "summary": summary,
        "cover_image": cover_image,
        "author": author,
        "category_id": category_id,
        "tag_names": tag_names,
        "is_top": is_top,
        "status": status
    }.items() if v is not None}

    article = KnowledgeArticleService.update_article(db, article_id, data)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ApiResponseBuilder.success(data=article.to_dict(), message="文章更新成功")


@router.delete("/articles/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """删除文章（管理员功能）"""
    success = KnowledgeArticleService.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ApiResponseBuilder.success(message="删除成功")
