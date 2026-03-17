# Core Library Enhancements

本文档描述了对 qilema 项目核心库的增强内容。

## 1. QueryBuilder 增强

### 新增功能

#### group_by
```python
builder.group_by("status", "role")
```

#### distinct
```python
builder.distinct("email")  # 对指定列去重
builder.distinct()  # 对整个查询去重
```

#### only_columns
```python
# 只查询需要的列，优化大数据量查询
builder.only_columns("id", "name", "phone")
```

#### eager_load
```python
# 自动选择最优的关联加载策略
builder.eager_load("emergency_contacts", "health_record")
# - 多对一/一对一: 使用 joinedload
# - 一对多: 使用 selectinload
```

#### aggregate
```python
# 聚合函数
builder.aggregate('count', 'id', 'total')
builder.aggregate('sum', 'amount', 'total_amount')
builder.aggregate('avg', 'age', 'avg_age')
builder.aggregate('min', 'created_at', 'earliest')
builder.aggregate('max', 'created_at', 'latest')
```

### 新增 BatchQueryBuilder
```python
from app.core.query_builder import BatchQueryBuilder

# 分批处理大批量数据
batch = BatchQueryBuilder(db.query(User), batch_size=1000)
for records in batch.iter_batches():
    process_records(records)

# 逐条迭代
for record in batch.iter_records():
    process_record(record)
```

## 2. CacheMixin 增强

### 批量缓存操作
```python
# 批量获取缓存
entities = mixin.get_cached_batch(["user1", "user2", "user3"])

# 批量缓存
mixin.cache_batch_entities([
    ("user1", user1_data),
    ("user2", user2_data),
])
```

### 增强的装饰器
```python
# 自定义缓存键
@mixin.cache_decorator(key_func=lambda self, user_id: f"user:{user_id}")
def get_user(self, user_id: str):
    return self.db.query(User).filter(...).first()

# 配置 TTL
@mixin.cache_decorator(ttl=600)
def get_expensive_data(self):
    return expensive_computation()
```

### 缓存预热器
```python
from app.core.cache_mixin import CacheWarmer

warmer = CacheWarmer()
warmer.add_task("users", lambda: db.query(User).all(), priority=0)
warmer.add_task("settings", lambda: db.query(Setting).all(), priority=1)

# 在应用启动时执行
results = await warmer.warm_all()
```

## 3. BaseService 增强

### 批量操作
```python
# 批量创建
users = UserService.create_batch(db, [
    {"name": "User1", "email": "u1@test.com"},
    {"name": "User2", "email": "u2@test.com"},
], batch_size=1000)

# 批量更新
UserService.update_batch(db, [
    {"id": 1, "name": "Updated1"},
    {"id": 2, "name": "Updated2"},
])

# 批量删除
UserService.delete_batch(db, [1, 2, 3, 4, 5])

# 批量查询
users = UserService.get_by_ids(db, [1, 2, 3, 4, 5])
```

### QueryBuilder 集成
```python
# 获取预配置的 QueryBuilder
builder = UserService.get_query_builder(db)
result = (
    builder.filter(status='active')
    .where_like('name', '%john%')
    .order_by('created_at', desc=True)
    .eager_load('emergency_contacts')
    .paginate(page=1, per_page=20)
    .execute()
)

# 简化的分页查询
pagination = UserService.paginated_list(
    db, page=1, per_page=20,
    order_by='created_at', order_desc=True,
    status='active'
)
```

### 事务管理
```python
# 使用上下文管理器
with BaseService.transaction(db):
    UserService.create_record(db, {...})
    UserService.update_record(db, 1, {...})
    # 自动提交或回滚
```

## 4. 使用示例

### 完整服务示例
```python
from app.core import QueryBuilder, paginate
from app.services.base_service import BaseService

class UserService(BaseService[User]):
    model_class = User
    cache_prefix = "user"
    cache_ttl = 300

    @classmethod
    def search_users(
        cls,
        db: Session,
        keyword: str = None,
        status: str = None,
        page: int = 1,
        per_page: int = 20
    ):
        # 使用 QueryBuilder
        builder = cls.get_query_builder(db)

        if status:
            builder = builder.filter(status=status)

        if keyword:
            builder = builder.where_like('name', f'%{keyword}%')

        return (
            builder.order_by('created_at', desc=True)
            .eager_load('emergency_contacts', 'health_record')
            .paginate(page, per_page)
            .execute()
        )

    @classmethod
    def get_user_stats(cls, db: Session):
        # 使用聚合
        builder = cls.get_query_builder(db)
        total = builder.aggregate('count', 'id').scalar()
        return {"total": total}
```

## 5. 性能优化建议

1. **大数据量查询**: 使用 `only_columns()` 只查询需要的列
2. **关联加载**: 使用 `eager_load()` 避免 N+1 问题
3. **批量操作**: 使用 `create_batch()`, `update_batch()`, `delete_batch()` 减少数据库往返
4. **分页**: 使用 `paginate()` 或 `BatchQueryBuilder` 处理大量数据
5. **缓存**: 使用 `CacheWarmer` 预热关键数据缓存
