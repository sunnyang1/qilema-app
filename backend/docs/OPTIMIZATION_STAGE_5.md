# Stage 5 优化文档：代码复用优化

## 概述

阶段 5 引入了两个重要的代码复用组件：
- **CacheMixin**: 统一的缓存管理混合类
- **QueryBuilder**: 统一的查询构建器

## 1. CacheMixin 缓存混合类

### 位置
`backend/app/core/cache_mixin.py`

### 功能
提供统一的缓存管理功能：
- 缓存键生成与管理
- 自动缓存读取/写入
- 缓存失效管理
- 装饰器支持

### 使用方法

```python
from app.core.cache_mixin import CacheMixin

class UserService(CacheMixin):
    cache_prefix = "user"
    cache_ttl = 300  # 5分钟

    def get_by_id(self, user_id: str):
        # 1. 生成缓存键
        cache_key = self._make_key(f"id:{user_id}")

        # 2. 尝试从缓存获取
        cached = self._get(cache_key)
        if cached:
            return cached

        # 3. 查询数据库
        user = self.db.query(User).filter(User.id == user_id).first()

        # 4. 写入缓存
        if user:
            self._set(cache_key, user)

        return user

    def update_user(self, user_id: str, data: dict):
        # 更新逻辑...

        # 自动失效缓存
        self.invalidate_entity_cache(f"id:{user_id}")
        self._invalidate_list_cache()
```

### 主要方法

| 方法 | 说明 |
|------|------|
| `_make_key(*parts)` | 生成缓存键 |
| `_make_pattern(*parts)` | 生成缓存键模式 |
| `_get(key)` | 从缓存获取 |
| `_set(key, value, ttl)` | 写入缓存 |
| `_invalidate(key)` | 失效单个缓存 |
| `_invalidate_pattern(pattern)` | 按模式失效缓存 |
| `cache_entity(id, entity)` | 缓存实体 |
| `invalidate_entity_cache(id)` | 失效实体缓存 |

## 2. QueryBuilder 查询构建器

### 位置
`backend/app/core/query_builder.py`

### 功能
提供统一的查询构建功能：
- 分页
- 排序
- 过滤条件
- 链式调用

### 使用方法

```python
from app.core.query_builder import QueryBuilder, paginate

# 方法1：使用 QueryBuilder
query = db.query(User)
builder = QueryBuilder(query, User)

result = (
    builder.filter(status='active')
    .where_like('name', '%张%')
    .where_between('age', 18, 60)
    .order_by('created_at', order_desc=True)
    .paginate(page=1, per_page=20)
)

users = result.execute()

# 方法2：使用便捷的 paginate 函数
total = query.count()
items = query.offset(0).limit(20).all()
pagination = paginate(query, page=1, per_page=20)
```

### 主要方法

| 方法 | 说明 |
|------|------|
| `filter(**conditions)` | 等值过滤 |
| `where(condition)` | 原始条件 |
| `where_in(field, values)` | IN 条件 |
| `where_like(field, pattern)` | LIKE 条件 |
| `where_between(field, min, max)` | BETWEEN 条件 |
| `order_by(field, order_desc)` | 排序 |
| `paginate(page, per_page)` | 分页 |
| `execute()` | 执行查询 |
| `first()` | 获取第一条 |
| `count()` | 获取数量 |

## 3. 示例服务

### 位置
`backend/app/services/example_refactored_service.py`

### 内容
展示了如何使用 CacheMixin 和 QueryBuilder 重构现有服务。

## 4. 测试覆盖

### 位置
- `backend/tests/unit/core/test_cache_mixin.py`
- `backend/tests/unit/core/test_query_builder.py`

### 测试结果
```
54 passed, 2 warnings in 0.54s
```

## 5. 迁移建议

### 现有服务迁移步骤

1. **继承 CacheMixin**
```python
class UserService(CacheMixin):
    cache_prefix = "user"
    cache_ttl = 300
```

2. **替换缓存代码**
```python
# 旧代码
cache_key = f"{CacheConfig.PREFIX_USER}{user_id}"
user = get_cached(cache_key)
if not user:
    user = db.query(User).filter(...).first()
    cache_result(cache_key, user)

# 新代码
user = self._get(self._make_key(user_id))
if not user:
    user = db.query(User).filter(...).first()
    self._set(self._make_key(user_id), user)
```

3. **使用 QueryBuilder**
```python
# 旧代码
query = db.query(User).filter(User.status == 'active')
query = query.order_by(desc(User.created_at))
total = query.count()
items = query.offset(0).limit(20).all()

# 新代码
builder = QueryBuilder(db.query(User), User)
result = (
    builder.filter(status='active')
    .order_by('created_at', order_desc=True)
    .paginate(page=1, per_page=20)
)
items = result.execute()
total = result.count()
```

## 6. 文件列表

### 新增文件
- `app/core/cache_mixin.py` - CacheMixin 缓存混合类
- `app/core/query_builder.py` - QueryBuilder 查询构建器
- `app/services/example_refactored_service.py` - 示例重构服务
- `tests/unit/core/test_cache_mixin.py` - CacheMixin 测试 (18个测试)
- `tests/unit/core/test_query_builder.py` - QueryBuilder 测试 (36个测试)

## 7. 优化效果

### 代码复用
- 缓存管理逻辑统一封装，避免重复代码
- 查询构建逻辑统一封装，减少样板代码

### 维护性
- 缓存策略集中管理，易于调整
- 查询构建统一规范，易于维护

### 开发效率
- 新服务开发更快（复用已有组件）
- 代码审查更简单（统一模式）

## 8. 注意事项

1. **CacheMixin** 需要配置 `cache_prefix` 和 `cache_ttl`
2. **QueryBuilder** 的 `where_between` 需要模型类有对应字段
3. 迁移时保持向后兼容，先添加新代码再逐步替换旧代码
