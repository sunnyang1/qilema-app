"""
示例：使用 CacheMixin 和 QueryBuilder 重构的服务

这个文件展示了如何在新服务中使用：
- CacheMixin: 统一的缓存管理
- QueryBuilder: 统一的查询构建

可以作为其他服务重构的参考模板。非 DI 默认实现；归属见 docs/PHASE2_DOMAIN_BOUNDARIES.md（R-W4）。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.cache_mixin import CacheMixin
from app.core.query_builder import QueryBuilder, paginate
from app.models.user import User


class RefactoredUserService(CacheMixin):
    """
    重构后的 UserService

    使用 CacheMixin 和 QueryBuilder 提供：
    - 自动缓存管理
    - 统一的查询构建
    - 更清晰的代码结构
    """

    # CacheMixin 配置
    cache_prefix = "user"
    cache_ttl = 300  # 5分钟

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据 ID 获取用户（带缓存）

        Args:
            user_id: 用户 ID

        Returns:
            Optional[User]: 用户对象或 None
        """
        # 1. 尝试从缓存获取
        cache_key = self._make_key(f"id:{user_id}")
        cached = self._get(cache_key)
        if cached:
            return cached

        # 2. 查询数据库
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # 3. 写入缓存
            self._set(cache_key, user)

        return user

    def get_active_users(
        self,
        keyword: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        获取活跃用户列表（使用 QueryBuilder 分页查询）

        Args:
            keyword: 搜索关键词
            page: 页码
            per_page: 每页数量

        Returns:
            dict: 分页结果
        """
        # 1. 检查缓存
        cache_key = self._make_key(f"active:{keyword}:{page}:{per_page}")
        cached = self._get(cache_key)
        if cached:
            return cached

        # 2. 使用 QueryBuilder 构建查询
        query = self.db.query(User)
        builder = QueryBuilder(query, User)

        # 构建查询条件
        result = (
            builder.filter(status="active")
            .where_like("name", f"%{keyword}%" if keyword else None)
            .order_by("created_at", desc=True)
            .paginate(page=page, per_page=per_page)
        )

        # 3. 转换为分页结果
        pagination = {
            "items": [u.to_dict() for u in result.execute()],
            "page": page,
            "per_page": per_page,
            "total": result.count(),
        }

        # 4. 缓存结果
        self._set(cache_key, pagination)

        return pagination

    def search_users(
        self,
        status: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        order_by: str = "created_at",
        desc: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        高级用户搜索（展示 QueryBuilder 的各种功能）

        Args:
            status: 状态过滤
            min_age: 最小年龄
            max_age: 最大年龄
            order_by: 排序字段
            desc: 是否降序
            page: 页码
            per_page: 每页数量

        Returns:
            dict: 分页结果
        """
        query = self.db.query(User)
        builder = QueryBuilder(query, User)

        result = (
            builder.filter(status=status)
            .where_between("age", min_age, max_age)
            .order_by(order_by, desc=desc)
            .paginate(page=page, per_page=per_page)
        )

        return {
            "items": [u.to_dict() for u in result.execute()],
            "page": page,
            "per_page": per_page,
            "total": result.count(),
        }

    def create_user(self, user_data: dict) -> User:
        """
        创建用户（自动失效相关缓存）

        Args:
            user_data: 用户数据

        Returns:
            User: 创建的用户
        """
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # 失效相关缓存
        self._invalidate_list_cache()

        return user

    def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """
        更新用户（自动失效缓存）

        Args:
            user_id: 用户 ID
            user_data: 更新数据

        Returns:
            Optional[User]: 更新后的用户或 None
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        # 失效缓存
        self.invalidate_entity_cache(f"id:{user_id}")
        self._invalidate_list_cache()

        return user

    def delete_user(self, user_id: str) -> bool:
        """
        删除用户（自动失效缓存）

        Args:
            user_id: 用户 ID

        Returns:
            bool: 是否成功
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        # 失效缓存
        self.invalidate_entity_cache(f"id:{user_id}")
        self._invalidate_list_cache()

        return True


# ============================================================================
# 使用示例
# ============================================================================


def example_usage():
    """
    使用示例（伪代码）
    """
    from sqlalchemy.orm import Session

    db: Session = ...  # 获取数据库会话
    service = RefactoredUserService(db)

    # 1. 获取用户（自动缓存）
    user = service.get_by_id("user123")

    # 2. 获取活跃用户列表（自动缓存）
    result = service.get_active_users(keyword="张", page=1, per_page=20)

    # 3. 高级搜索
    result = service.search_users(
        status="active",
        min_age=18,
        max_age=60,
        order_by="created_at",
        desc=True,
    )

    # 4. 创建用户（自动失效列表缓存）
    new_user = service.create_user({"name": "张三", "status": "active"})

    # 5. 更新用户（自动失效相关缓存）
    updated = service.update_user("user123", {"name": "李四"})

    # 6. 删除用户（自动失效相关缓存）
    service.delete_user("user123")
