# FastAPI + SQLAlchemy 2.x 迁移指南

本文档总结了项目从传统模式迁移到 FastAPI 0.135.x + SQLAlchemy 2.x 规范的变更。

## 1. 已完成的迁移

### 1.1 SQLAlchemy 2.x 迁移

#### 数据库基类更新
```python
# 旧方式 (SQLAlchemy 1.x)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# 新方式 (SQLAlchemy 2.x)
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

#### 模型定义更新
```python
# 旧方式 (SQLAlchemy 1.x)
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

# 新方式 (SQLAlchemy 2.x)
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
```

#### 关键变化
1. 使用 `Mapped[]` 类型注解声明字段类型
2. 使用 `mapped_column()` 替代 `Column()`
3. 类型检查器可以正确推断字段类型
4. 支持更好的 IDE 自动补全

参考：`app/models/example_modern.py`

### 1.2 FastAPI 0.135.x 迁移

#### Lifespan 上下文管理器
```python
# 旧方式（仍支持但不推荐）
@app.on_event("startup")
async def startup_event():
    init_db()

# 新方式（推荐）
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动逻辑
    init_db()
    yield
    # 关闭逻辑

app = FastAPI(lifespan=lifespan)
```

#### Annotated 依赖注入模式
```python
# 旧方式（仍然支持）
from fastapi import Depends

@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
):
    ...

# 新方式（推荐）
from typing import Annotated

@router.get("/users")
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
):
    ...

# 最简洁方式（使用预定义类型）
from app.api.dependencies import DbSession

@router.get("/users")
async def list_users(
    db: DbSession,  # 即 Annotated[Session, Depends(get_db)]
    page: Annotated[int, Query(ge=1)] = 1,
):
    ...
```

参考：`app/api/example_modern.py`

### 1.3 Pydantic v2 迁移（已完成）

项目已经使用 Pydantic v2 语法，符合规范：
- ✅ `@field_validator` 替代 `@validator`
- ✅ `@model_validator` 替代 `@root_validator`
- ✅ `model_config = {"from_attributes": True}` 替代 `Config.orm_mode = True`
- ✅ `model_validate()` 替代 `from_orm()`
- ✅ `Field(pattern=...)` 替代 `Field(regex=...)`

## 2. 迁移检查清单

### 后端迁移清单

#### 必须迁移（影响功能）
- [x] SQLAlchemy 数据库基类 (`app/core/database.py`)
- [x] FastAPI Lifespan 上下文管理器 (`main.py`)
- [ ] 模型层：逐步将 `Column()` 迁移到 `mapped_column()`
- [ ] 查询层：逐步将 `db.query()` 迁移到 `select()`

#### 推荐迁移（提升代码质量）
- [ ] API 层：将 `Depends()` 迁移到 `Annotated[..., Depends()]`
- [ ] 模型层：添加 `Mapped[]` 类型注解

#### 已符合规范
- [x] Pydantic v2 语法
- [x] 配置管理 (`pydantic-settings`)

### 前端迁移清单

#### 已符合规范
- [x] Express.js 5.x 使用正确
- [x] 中间件配置正确 (`express.json()`, `express.urlencoded()`)

#### 需要检查
- [ ] Supabase SDK 使用（项目中引入了但未找到使用代码）

## 3. 向后兼容性说明

### 向后兼容的变更
- ✅ `DeclarativeBase` 继承自 `declarative_base()` 的模型可以共存
- ✅ `Annotated[..., Depends()]` 和 `Depends()` 可以混用
- ✅ `lifespan` 和 `@app.on_event` 可以共存（但不推荐）

### 不兼容的变更
- ❌ SQLAlchemy 2.x 的 `select()` 语法与 `db.query()` 语法不同
- ❌ Pydantic v2 的验证行为与 v1 有所不同

## 4. 示例代码

### 完整的新风格 API
```python
from typing import Annotated, List
from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.dependencies import DbSession
from app.services.user_service import UserService
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
):
    service = UserService(db)
    users = service.get_list(page=page, per_page=per_page)
    return [UserResponse.model_validate(u) for u in users]
```

### 完整的新风格模型
```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    phone: Mapped[str] = mapped_column(String(11), unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
```

## 5. 验证迁移

运行以下命令验证迁移是否成功：

```bash
# 1. 检查导入
cd backend
python -c "from app.core.database import Base, engine; print('✅ Database import OK')"

# 2. 检查 FastAPI
python -c "from main import app; print('✅ FastAPI import OK')"

# 3. 检查依赖注入
python -c "from app.api.dependencies import DbSession; print('✅ Dependencies import OK')"

# 4. 运行测试
pytest tests/ -v --tb=short
```

## 6. 参考资料

- [FastAPI 0.135.x Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Context Hub](https://github.com/andrewyng/context-hub) - 获取最新 API 文档

## 7. 下一步行动

1. **模型层迁移**：逐步将现有模型从 `Column()` 迁移到 `mapped_column()`
2. **API 层迁移**：逐步将 `Depends()` 迁移到 `Annotated[..., Depends()]`
3. **查询层迁移**：逐步将 `db.query()` 迁移到 `select()`
4. **测试**：确保所有测试通过
