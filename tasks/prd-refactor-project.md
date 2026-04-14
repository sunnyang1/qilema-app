# PRD: 项目全面重构

## 1. 引言

将 qilema-app 项目从传统 SQLAlchemy 1.x 风格迁移到 SQLAlchemy 2.x 现代化风格，同时统一 API 层的依赖注入模式。

## 2. 目标

- 所有模型使用 SQLAlchemy 2.x 风格（Mapped[], mapped_column()）
- 所有服务统一使用 BaseService + CacheMixin + QueryBuilder
- 所有 API 使用 Annotated[..., Depends()] 模式
- 测试覆盖率 >80%

## 3. 用户故事

### US-1: 重构核心模型到 SQLAlchemy 2.x
**作为** 开发者
**我需要** 将 User, CheckIn, SOSRequest 等核心模型迁移到 SQLAlchemy 2.x
**以便** 使用最新的 ORM 特性和类型提示

**验收标准**:
- [ ] 使用 `Mapped[]` 类型注解
- [ ] 使用 `mapped_column()` 替代 `Column()`
- [ ] 关联关系使用 `Mapped[List[T]]` 或 `Mapped[T]`
- [ ] 保留现有数据库结构（不改变迁移）

**预估**: 90分钟

### US-2: 更新服务层依赖注入
**作为** 开发者
**我需要** 更新所有服务使用现代化的依赖注入
**以便** 代码符合 FastAPI 0.135.x 规范

**验收标准**:
- [ ] 所有服务可正常导入
- [ ] 无循环导入问题
- [ ] 使用预定义的 `Annotated` 类型

**预估**: 20分钟

### US-3: 更新 API 层路由
**作为** 开发者
**我需要** 将所有 API 路由迁移到 Annotated 模式
**以便** 代码简洁且符合规范

**验收标准**:
- [ ] 使用 `DbSession` 替代 `Session = Depends(get_db)`
- [ ] 使用 `UserServiceDep` 等服务依赖类型
- [ ] 所有路由可正常注册

**预估**: 30分钟

### US-4: 创建模型层测试
**作为** 开发者
**我需要** 为核心模型创建单元测试
**以便** 确保重构后功能正确

**验收标准**:
- [ ] User 模型测试
- [ ] CheckIn 模型测试
- [ ] SOSRequest 模型测试
- [ ] 测试覆盖率 >80%

**预估**: 30分钟

### US-5: 验证和回归测试
**作为** 开发者
**我需要** 运行完整测试套件验证重构
**以便** 确保无功能退化

**验收标准**:
- [ ] 所有模块可导入
- [ ] pytest 通过率 100%
- [ ] 无 Pydantic/SQLAlchemy 弃用警告

**预估**: 15分钟

## 4. 需求

### 功能需求
- FR-1: 所有模型使用 SQLAlchemy 2.x 语法
- FR-2: 所有服务使用统一的 BaseService 模式
- FR-3: 所有 API 使用 Annotated 依赖注入

### 非功能需求
- NFR-1: 数据库结构保持不变
- NFR-2: 向后兼容现有 API
- NFR-3: 性能无退化

## 5. 技术考虑

### 依赖
- SQLAlchemy 2.0+
- Pydantic 2.5+
- FastAPI 0.104+

### 风险
- 中等：模型关系复杂，需小心处理
- 低：业务逻辑保持不变

## 6. 成功指标
- 0 个弃用警告
- 100% 测试通过
- 代码覆盖率 >80%
