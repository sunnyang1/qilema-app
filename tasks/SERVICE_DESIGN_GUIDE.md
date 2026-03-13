# 服务类设计规范

## 1. 概述

本文档定义了 "起了吗" App 后端服务类的设计规范，旨在统一服务类的实现方式，提高代码的可维护性和可测试性。

## 2. 设计原则

### 2.1 实例方法模式（推荐）

所有服务类应该使用**实例方法模式**，通过构造函数接收依赖。

```python
class UserService:
    """用户服务类 - 实例方法模式"""

    def __init__(self, db: Session):
        """
        初始化服务实例

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.user_id == user_id).first()

    def create(self, data: dict) -> User:
        """创建用户"""
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        return user
```

**优点**:
- 依赖明确：通过构造函数声明依赖
- 易于测试：可以轻松 mock 依赖
- 状态隔离：每个实例有自己的状态和依赖
- 支持 DI：与依赖注入容器完美配合

### 2.2 禁用模式

#### ❌ 禁止使用静态方法模式

```python
# 不推荐
class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()
```

**缺点**:
- 每次调用都需要传递 db 参数
- 难以 mock 依赖
- 无法使用实例状态

#### ❌ 禁止使用类方法模式

```python
# 不推荐
class UserService:
    @classmethod
    def get_by_id(cls, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()
```

**缺点**:
- 语义不清晰（类方法与实例方法混用）
- 继承时容易出错
- 难以 mock

#### ❌ 禁止混合使用多种方法类型

```python
# 不推荐
class UserService:
    @staticmethod
    def create_user(db: Session, data: dict) -> User:
        pass

    @classmethod
    def get_user_by_id(cls, db: Session, user_id: str) -> Optional[User]:
        pass

    def login(self, phone: str, password: str) -> dict:
        pass
```

## 3. 服务类结构模板

### 3.1 标准模板

```python
"""
XXX服务

提供XXX相关的业务逻辑处理
"""

from typing import Any, Dict, List, Optional

from app.models.xxx import XXX
from sqlalchemy.orm import Session


class XXXService:
    """
    XXX服务类

    提供XXX的CRUD操作和业务逻辑

    Attributes:
        db: 数据库会话
    """

    def __init__(self, db: Session):
        """
        初始化XXX服务

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========== 查询方法 ==========

    def get_by_id(self, id: str) -> Optional[XXX]:
        """
        根据ID获取记录

        Args:
            id: 记录ID

        Returns:
            记录对象或None
        """
        return self.db.query(XXX).filter(XXX.id == id).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[XXX]:
        """
        获取记录列表

        Args:
            skip: 跳过数量
            limit: 限制数量
            **filters: 过滤条件

        Returns:
            记录列表
        """
        query = self.db.query(XXX)

        # 应用过滤条件
        for field, value in filters.items():
            if value is not None and hasattr(XXX, field):
                query = query.filter(getattr(XXX, field) == value)

        return query.offset(skip).limit(limit).all()

    # ========== 创建方法 ==========

    def create(self, data: Dict[str, Any]) -> XXX:
        """
        创建记录

        Args:
            data: 记录数据

        Returns:
            创建的记录对象
        """
        instance = XXX(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    # ========== 更新方法 ==========

    def update(self, id: str, data: Dict[str, Any]) -> Optional[XXX]:
        """
        更新记录

        Args:
            id: 记录ID
            data: 更新数据

        Returns:
            更新后的记录对象或None
        """
        instance = self.get_by_id(id)
        if not instance:
            return None

        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    # ========== 删除方法 ==========

    def delete(self, id: str) -> bool:
        """
        删除记录

        Args:
            id: 记录ID

        Returns:
            是否成功删除
        """
        instance = self.get_by_id(id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True
```

### 3.2 继承 BaseService 的模板

```python
"""
XXX服务

继承 BaseService 获得通用CRUD能力
"""

from typing import Type

from app.models.xxx import XXX
from app.services.base_service import BaseService
from sqlalchemy.orm import Session


class XXXService(BaseService[XXX]):
    """
    XXX服务类

    继承 BaseService 获得通用CRUD能力

    Attributes:
        model_class: 模型类
        db: 数据库会话
    """

    model_class: Type[XXX] = XXX

    def __init__(self, db: Session):
        """
        初始化XXX服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_by_id(self, id: str) -> Optional[XXX]:
        """根据ID获取记录"""
        return super().get_by_id(self.db, id)

    def list(self, skip: int = 0, limit: int = 100) -> List[XXX]:
        """获取记录列表"""
        return super().list_records(self.db, skip=skip, limit=limit)

    def create(self, data: dict) -> XXX:
        """创建记录"""
        return super().create_record(self.db, data)

    def update(self, id: str, data: dict) -> Optional[XXX]:
        """更新记录"""
        return super().update_record(self.db, id, data)

    def delete(self, id: str) -> bool:
        """删除记录"""
        return super().delete_record(self.db, id)
```

## 4. 依赖注入使用规范

### 4.1 服务提供者函数

```python
# app/api/xxx.py
def get_xxx_service(db: Session = Depends(get_db)) -> XXXService:
    """
    获取XXX服务实例

    Args:
        db: 数据库会话

    Returns:
        XXXService: XXX服务实例
    """
    return XXXService(db)
```

### 4.2 在 API 路由中使用

```python
@router.get("/{id}")
def get_xxx(
    id: str,
    service: XXXService = Depends(get_xxx_service),
    current_user: User = Depends(get_current_user),
):
    """获取XXX详情"""
    instance = service.get_by_id(id)
    if not instance:
        raise NotFoundException("记录不存在")
    return ApiResponseBuilder.success(data=instance.to_dict())
```

### 4.3 服务间调用

```python
class OrderService:
    def __init__(self, db: Session):
        self.db = db
        # 服务间调用时创建依赖服务实例
        self.user_service = UserService(db)

    def create_order(self, user_id: str, data: dict) -> Order:
        # 使用依赖服务
        user = self.user_service.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        # ...
```

## 5. 测试规范

### 5.1 单元测试模板

```python
"""
XXX服务单元测试
"""

import pytest
from unittest.mock import MagicMock

from app.services.xxx_service import XXXService


class TestXXXService:
    """XXX服务测试类"""

    @pytest.fixture
    def mock_db(self):
        """创建 mock 数据库会话"""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        """创建服务实例"""
        return XXXService(mock_db)

    def test_get_by_id_found(self, service, mock_db):
        """测试获取存在的记录"""
        # 准备
        mock_instance = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_instance

        # 执行
        result = service.get_by_id("test-id")

        # 验证
        assert result == mock_instance

    def test_get_by_id_not_found(self, service, mock_db):
        """测试获取不存在的记录"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # 执行
        result = service.get_by_id("non-existent")

        # 验证
        assert result is None

    def test_create(self, service, mock_db):
        """测试创建记录"""
        # 准备
        data = {"name": "测试"}

        # 执行
        result = service.create(data)

        # 验证
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
```

## 6. 迁移指南

### 6.1 从静态方法迁移到实例方法

**迁移前**:
```python
class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()
```

**迁移后**:
```python
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()
```

**API 层更新**:
```python
# 迁移前
@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = UserService.get_by_id(db, user_id)
    ...

# 迁移后
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.get("/{user_id}")
def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    user = service.get_by_id(user_id)
    ...
```

## 7. 检查清单

创建或修改服务类时，请检查：

- [ ] 使用实例方法模式
- [ ] 构造函数接收 `db: Session` 参数
- [ ] 使用 `self.db` 访问数据库会话
- [ ] 方法命名清晰（如 `get_by_id`, `create`, `update`, `delete`）
- [ ] 添加类型注解
- [ ] 添加文档字符串
- [ ] 为每个方法编写单元测试
- [ ] 更新 API 层使用依赖注入

## 8. 示例服务列表

以下服务类需要按照本规范重构：

- [ ] `UserService`
- [ ] `CheckInService`
- [ ] `SosService`
- [ ] `EmergencyContactService`
- [ ] `HealthRecordService`
- [ ] `DeviceService`
- [ ] `MedicationService`
- [ ] `AnomalyService`
- [ ] `AlertService`
- [ ] `AEDService`
- [ ] `EmergencyCenterService`
- [ ] `KnowledgeService`
- [ ] `LocationService`
- [ ] `HealthReportService`
