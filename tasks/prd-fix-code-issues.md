# PRD: 修复代码问题

## 1. 引言

修复在之前 API 升级过程中发现的项目原有代码问题，确保所有模块可正常导入和运行。

## 2. 目标

- 修复 `notification_service.py` 的导入和定义问题
- 修复 `schemas.py` 的 Pydantic v2 警告
- 批量迁移 `orm_mode` → `from_attributes`

## 3. 用户故事

### US-1: 修复 notification_service 导入问题
**作为** 开发者
**我需要** 能够正常导入 notification_service 模块
**以便** 使用通知服务功能

**验收标准**:
- [ ] `from app.services.notification_service import NotificationService` 成功
- [ ] 无 NameError 错误

**预估**: 10分钟

### US-2: 修复 schemas.py Pydantic 警告
**作为** 开发者
**我需要** 消除 Pydantic v2 的继承顺序警告
**以便** 代码符合最新规范

**验收标准**:
- [ ] `class ListResponse(BaseModel, Generic[T])` 顺序正确
- [ ] 无 `GenericBeforeBaseModelWarning` 警告

**预估**: 3分钟

### US-3: 迁移 orm_mode 到 from_attributes
**作为** 开发者
**我需要** 将所有 `orm_mode = True` 迁移到 `from_attributes = True`
**以便** 符合 Pydantic v2 规范

**验收标准**:
- [ ] `backend/app/schemas/notification.py` 已修复
- [ ] `backend/app/schemas/user_setting.py` 已修复
- [ ] `backend/app/api/example_modern.py` 已修复（如需要）

**预估**: 5分钟

## 4. 需求

### 功能需求
- FR-1: notification_service 模块无导入错误
- FR-2: 所有 Pydantic 模型无弃用警告

### 非功能需求
- NFR-1: 向后兼容（不影响现有功能）

## 5. 技术考虑

### 依赖
- Pydantic v2.x
- SQLAlchemy 2.x

### 风险
- 低：仅修改配置和继承顺序，不影响业务逻辑

## 6. 成功指标
- 所有模块可正常导入
- 无 Pydantic v2 弃用警告
