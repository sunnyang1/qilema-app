# 起了吗App 架构优化重构 PRD

## 1. 概述

### 1.1 重构目标
对起了吗App的后端架构进行深度优化，引入依赖注入、统一DTO转换、增强中间件日志、创建服务接口抽象，提升代码的可测试性、可维护性和扩展性。

### 1.2 当前问题
1. **服务层耦合数据库Session** - 难以进行单元测试，需要Mock整个Session
2. **缺乏依赖注入容器** - 服务实例化分散，依赖关系不清晰
3. **DTO转换逻辑分散** - ApiResponseBuilder.from_model 需要手动处理to_dict
4. **中间件日志不够详细** - 缺少请求ID追踪、性能监控、错误上下文
5. **服务缺乏接口抽象** - 难以进行接口隔离和Mock测试

### 1.3 成功标准
- 所有服务通过依赖注入容器管理
- 所有Schema统一使用BaseSchema转换逻辑
- 中间件日志包含请求ID、性能指标、完整上下文
- 核心服务定义接口抽象
- 现有测试100%通过，不破坏任何功能
- 代码质量评分提升（可维护性、可测试性）

---

## 2. 重构目标 (Refactoring Goals)

### RG-ARCH-001: 引入依赖注入容器
**描述**: 使用dependency-injector库创建统一的依赖注入容器，管理所有服务和资源

**验收标准**:
- [ ] 创建Container类，配置所有服务
- [ ] 移除路由中的直接服务实例化
- [ ] 所有路由通过Depends注入服务
- [ ] 支持数据库、Redis等资源的单例管理
- [ ] 配置文件集中管理

### RG-ARCH-002: 创建统一DTO转换层
**描述**: 创建BaseSchema抽象类，统一ORM到Pydantic Schema的转换逻辑

**验收标准**:
- [ ] 创建BaseSchema抽象类
- [ ] 实现from_orm和from_orm_list方法
- [ ] 所有Response Schema继承BaseSchema
- [ ] 移除手动to_dict调用
- [ ] 添加单元测试验证转换逻辑

### RG-ARCH-003: 增强中间件日志
**描述**: 扩展现有中间件，添加请求ID追踪、性能监控、详细上下文记录

**验收标准**:
- [ ] 添加请求ID生成和传递
- [ ] 记录请求/响应时间
- [ ] 记录请求体和响应体（脱敏）
- [ ] 记录异常堆栈
- [ ] 结构化日志格式（JSON）

### RG-ARCH-004: 创建服务接口抽象
**描述**: 为核心服务创建接口抽象，使用ABC定义契约

**验收标准**:
- [ ] 创建ICheckInService接口
- [ ] 创建IUserService接口
- [ ] 创建IEmergencyContactService接口
- [ ] 所有服务实现对应接口
- [ ] 添加接口实现的单元测试

---

## 3. 功能需求 (Functional Requirements)

### FR-ARCH-001: 依赖注入容器
```python
# backend/app/core/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """依赖注入容器"""

    # 配置
    config = providers.Configuration()

    # 数据库
    database = providers.Singleton(
        Database,
        db_url=config.database.url
    )

    # Redis
    redis = providers.Singleton(
        Redis,
        url=config.redis.url
    )

    # 服务 - 使用Factory，每次请求创建新实例
    user_service = providers.Factory(
        UserService,
        db=database
    )

    checkin_service = providers.Factory(
        CheckInService,
        db=database
    )

    # ... 其他服务

# 在main.py中初始化
container = Container()
container.config.from_yaml("config.yaml")
```

### FR-ARCH-002: BaseSchema抽象类
```python
# backend/app/core/schemas.py
from pydantic import BaseModel, ConfigDict
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

ModelT = TypeVar("ModelT")

class BaseSchema(BaseModel, ABC):
    """统一的Schema基类"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    @classmethod
    @abstractmethod
    def from_orm(cls, orm_obj: ModelT) -> "BaseSchema":
        """从ORM对象转换

        Args:
            orm_obj: SQLAlchemy ORM对象

        Returns:
            Pydantic Schema实例
        """
        return cls.model_validate(orm_obj)

    @classmethod
    def from_orm_list(cls, orm_list: List[ModelT]) -> List["BaseSchema"]:
        """从ORM列表转换

        Args:
            orm_list: SQLAlchemy ORM对象列表

        Returns:
            Pydantic Schema实例列表
        """
        return [cls.model_validate(obj) for obj in orm_list]

# 使用示例
class UserResponse(BaseSchema):
    user_id: str
    username: str
    phone: str

    @classmethod
    def from_orm(cls, orm_obj: User) -> "UserResponse":
        return cls.model_validate(orm_obj)
```

### FR-ARCH-003: 增强日志中间件
```python
# backend/app/core/middleware.py
from fastapi import Request
import time
import uuid
import json
from typing import Callable

class EnhancedLoggingMiddleware:
    """增强的日志中间件"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        # 生成请求ID
        request_id = uuid.uuid4().hex[:8]
        start_time = time.time()

        # 将请求ID添加到state
        request.state.request_id = request_id

        # 记录请求日志
        logger.info(
            json.dumps({
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client": request.client.host if request.client else None,
                "type": "request"
            })
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            duration = time.time() - start_time

            # 记录响应日志
            logger.info(
                json.dumps({
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "type": "response"
                })
            )

            # 添加响应头
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 记录错误日志
            duration = time.time() - start_time
            logger.error(
                json.dumps({
                    "request_id": request_id,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                    "type": "error"
                })
            )
            raise
```

### FR-ARCH-004: 服务接口抽象
```python
# backend/app/core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

class ICheckInService(ABC):
    """签到服务接口"""

    @abstractmethod
    def create_checkin(
        self,
        db: Session,
        user_id: str,
        data: CheckInCreate
    ) -> CheckIn:
        """创建签到记录"""
        pass

    @abstractmethod
    def get_user_checkins(
        self,
        db: Session,
        user_id: str,
        **filters
    ) -> List[CheckIn]:
        """获取用户签到列表"""
        pass

    @abstractmethod
    def get_checkin_stats(
        self,
        db: Session,
        user_id: str,
        days: int
    ) -> dict:
        """获取签到统计"""
        pass

# 服务实现
class CheckInService(BaseService[CheckIn], ICheckInService):
    """签到服务实现"""

    def create_checkin(self, db: Session, user_id: str, data: CheckInCreate) -> CheckIn:
        # 实现逻辑...
        pass
```

---

## 4. 非目标

- ❌ 不修改前端代码（Flutter项目）
- ❌ 不修改数据库Schema
- ❌ 不改变API接口契约（保持向后兼容）
- ❌ 不引入新的外部库（仅dependency-injector）
- ❌ 不重构路由逻辑（仅注入服务）

---

## 5. 设计考虑

### 5.1 依赖注入设计
- **容器模式**: 使用DeclarativeContainer，配置集中管理
- **作用域**: Database使用Singleton，Service使用Factory
- **懒加载**: 服务仅在需要时实例化
- **可测试**: 支持测试时替换实现（Mock）

### 5.2 DTO转换设计
- **继承模式**: BaseSchema提供通用方法
- **自动化**: from_orm使用model_validate自动映射
- **列表支持**: from_orm_list批量转换
- **类型安全**: 保持Pydantic的类型验证

### 5.3 日志设计
- **结构化**: JSON格式，便于解析和分析
- **追踪性**: 请求ID贯穿整个请求链
- **性能监控**: 记录处理时间，识别慢请求
- **安全性**: 敏感数据脱敏处理

### 5.4 接口设计
- **ABC抽象**: Python标准库，IDE友好
- **最小契约**: 仅定义核心方法
- **向后兼容**: 现有实现无需大幅修改
- **可测试**: 便于Mock接口

---

## 6. 技术考虑

### 6.1 依赖项
- **dependency-injector**: ^4.41.0
- **Pydantic**: v2（已使用）
- **FastAPI**: 已使用

### 6.2 性能影响
- **DI容器开销**: 微秒级，可忽略
- **日志I/O**: 异步写入，不影响主流程
- **DTO转换**: Pydantic原生，性能优秀

### 6.3 兼容性
- **Python版本**: 3.11+
- **FastAPI版本**: 0.104+
- **现有API**: 保持100%兼容

---

## 7. 成功指标

### 7.1 代码质量指标
- ✅ 单元测试覆盖率 ≥ 90%
- ✅ 代码复杂度（圈复杂度）降低 20%
- ✅ 类型提示覆盖率 ≥ 95%

### 7.2 性能指标
- ✅ API响应时间增加 < 5ms
- ✅ 内存使用增加 < 10MB
- ✅ 日志写入延迟 < 1ms

### 7.3 可维护性指标
- ✅ 新增服务时间减少 50%
- ✅ 单元测试编写时间减少 40%
- ✅ Mock测试复杂度降低 60%

---

## 8. 未决问题

- ❓ 是否需要为所有服务创建接口，还是仅核心服务？
  - **建议**: 仅为核心服务（User, CheckIn, EmergencyContact, SOS）创建接口

- ❓ 日志记录是否需要异步队列？
  - **建议**: 暂不需要，Python logging已足够高效

- ❓ 依赖注入配置是否需要支持多环境？
  - **建议**: 是，支持dev/staging/prod三套配置

- ❓ 是否需要添加性能监控（如Prometheus）？
  - **建议**: 本次不包含，作为后续优化

---

## 9. 实施计划

### Phase 1: 基础设施（2天）
- US-ARCH-001: 安装dependency-injector
- US-ARCH-002: 创建Container类
- US-ARCH-003: 配置数据库和Redis
- US-ARCH-004: 创建配置文件（config.yaml）

### Phase 2: DTO转换层（1天）
- US-ARCH-005: 创建BaseSchema抽象类
- US-ARCH-006: 迁移User相关Schema
- US-ARCH-007: 迁移CheckIn相关Schema
- US-ARCH-008: 迁移其他Schema

### Phase 3: 中间件增强（1天）
- US-ARCH-009: 创建EnhancedLoggingMiddleware
- US-ARCH-010: 添加请求ID生成
- US-ARCH-011: 添加性能监控
- US-ARCH-012: 更新异常处理中间件

### Phase 4: 服务接口抽象（2天）
- US-ARCH-013: 创建ICheckInService接口
- US-ARCH-014: 创建IUserService接口
- US-ARCH-015: 创建IEmergencyContactService接口
- US-ARCH-016: 创建ISosService接口
- US-ARCH-017: 更新服务实现类

### Phase 5: 路由集成（1天）
- US-ARCH-018: 更新用户路由使用DI
- US-ARCH-019: 更新签到路由使用DI
- US-ARCH-020: 更新其他路由使用DI

### Phase 6: 测试和验证（1天）
- US-ARCH-021: 编写DI容器单元测试
- US-ARCH-022: 编写BaseSchema单元测试
- US-ARCH-023: 编写接口实现单元测试
- US-ARCH-024: 运行完整测试套件

**总计**: 24个用户故事，预计7-8天完成
