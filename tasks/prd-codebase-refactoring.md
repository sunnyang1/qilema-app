# 起了吗App 代码重构 PRD

## 1. 概述

### 1.1 重构目标
对起了吗App的代码库进行全面重构，消除重复代码，统一架构模式，提高代码可维护性和一致性。

### 1.2 现状问题
1. **API路由层重复代码严重** - 手动构建响应字典，模型到schema的转换代码重复
2. **BaseService缓存重建机制不可靠** - 尝试从字典重建对象可能失败
3. **模型to_dict实现不一致** - 日期格式、空值处理不统一
4. **服务层混合静态/实例方法** - 代码风格不一致，使用方式混乱
5. **缺乏统一的响应构建工具** - 不同路由使用不同方式构建响应

### 1.3 成功标准
- 消除所有重复的数据转换代码
- 所有服务统一使用BaseService模式
- 所有API路由使用统一的响应构建方式
- 测试覆盖率不降低，所有现有测试通过

---

## 2. 重构目标 (Refactoring Goals)

### RG-001: 统一API响应构建
**描述**: 所有API路由使用统一的响应构建工具函数，消除手动构建字典的重复代码

**验收标准**:
- [ ] 创建 `ApiResponseBuilder` 工具类
- [ ] 所有API路由使用统一的响应构建方式
- [ ] 消除路由文件中手动构建响应字典的代码

### RG-002: 重构BaseService缓存机制
**描述**: 修复BaseService缓存重建不可靠的问题，使用更健壮的缓存策略

**验收标准**:
- [ ] 修改缓存机制，不再尝试从字典重建对象
- [ ] 使用ID列表缓存 + 单条记录缓存的二级缓存策略
- [ ] 确保缓存命中时返回正确的模型实例

### RG-003: 统一模型to_dict方法
**描述**: 统一所有模型的to_dict实现，包括日期格式、枚举值处理、空值处理

**验收标准**:
- [ ] 创建 `BaseModelMixin` 提供统一的to_dict实现
- [ ] 所有模型继承该mixin或使用统一实现
- [ ] 日期格式统一使用ISO格式
- [ ] 枚举值自动转换为字符串

### RG-004: 统一服务层模式
**描述**: 统一所有服务类的实现模式，消除静态/实例方法混用

**验收标准**:
- [ ] 所有服务类继承BaseService
- [ ] 业务方法统一使用实例方法
- [ ] 向后兼容的静态方法包装
- [ ] 所有服务类定义model_class, cache_prefix, cache_ttl

### RG-005: 创建API路由基类/工具
**描述**: 创建通用的CRUD路由生成工具，减少样板代码

**验收标准**:
- [ ] 创建 `CRUDRouterGenerator` 自动生成标准CRUD路由
- [ ] 简化现有路由文件，使用生成的路由
- [ ] 保持自定义路由的灵活性

---

## 3. 功能需求 (Functional Requirements)

### FR-001: ApiResponseBuilder工具类
```python
class ApiResponseBuilder:
    """API响应构建器"""
    
    @staticmethod
    def success(data=None, message="success", code=200)
    @staticmethod
    def error(code, message, detail=None)
    @staticmethod
    def paginated(items, total, page, page_size)
    @staticmethod
    def from_model(model, schema_class)  # 自动转换模型到schema
```

### FR-002: BaseModelMixin
```python
class BaseModelMixin:
    """模型基类Mixin，提供统一的方法"""
    
    def to_dict(self, exclude=None, include=None)
    def to_schema(self, schema_class)
    @classmethod
    def from_dict(cls, data)
```

### FR-003: 改进的BaseService缓存
```python
class BaseService(Generic[ModelType]):
    """改进的服务基类"""
    
    # 二级缓存策略
    # 1. 列表缓存: prefix:list:{filter_hash} -> [id1, id2, ...]
    # 2. 单条缓存: prefix:id:{id} -> {dict_data}
    # 3. 查询时先查ID列表，再批量查单条缓存
```

### FR-004: CRUD路由生成器
```python
class CRUDRouterGenerator:
    """CRUD路由生成器"""
    
    @staticmethod
    def generate(
        router: APIRouter,
        service_class: Type[BaseService],
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
        response_schema: Type[BaseModel],
        prefix: str
    )
```

---

## 4. 非目标 (Non-Goals)

- **不修改数据库结构** - 保持现有表结构不变
- **不修改业务逻辑** - 保持现有业务行为不变
- **不修改API接口契约** - 保持请求/响应格式不变
- **不添加新功能** - 仅重构现有代码

---

## 5. 技术考量

### 5.1 向后兼容性
- 所有现有API端点保持URL和响应格式不变
- 服务层保留静态方法作为向后兼容包装
- 模型to_dict保持现有输出格式

### 5.2 测试策略
- 重构前运行全部测试，记录基线
- 每个重构任务完成后运行测试
- 所有测试必须通过后才能提交

### 5.3 渐进式重构
- 按模块逐个重构，不要一次性修改整个代码库
- 每次提交一个服务的重构
- 保持代码始终可运行

---

## 6. 成功指标

1. **代码重复率降低** - 使用工具检测重复代码，目标降低50%
2. **代码行数减少** - API路由文件平均行数减少30%
3. **测试通过率** - 100%现有测试通过
4. **代码一致性** - 所有服务类遵循统一模式

---

## 7. 重构任务清单

### Phase 1: 基础设施
- [ ] US-001: 创建ApiResponseBuilder工具类
- [ ] US-002: 创建BaseModelMixin
- [ ] US-003: 重构BaseService缓存机制

### Phase 2: 模型层
- [ ] US-004: 统一User模型to_dict
- [ ] US-005: 统一CheckIn模型to_dict
- [ ] US-006: 统一所有模型的to_dict实现

### Phase 3: 服务层
- [ ] US-007: 重构UserService
- [ ] US-008: 重构CheckInService
- [ ] US-009: 重构所有服务类

### Phase 4: API层
- [ ] US-010: 创建CRUDRouterGenerator
- [ ] US-011: 重构users路由
- [ ] US-012: 重构checkins路由
- [ ] US-013: 重构所有路由

---

## 8. 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 引入回归bug | 中 | 高 | 完整测试覆盖，渐进式重构 |
| API契约变化 | 低 | 高 | 严格保持向后兼容 |
| 性能下降 | 低 | 中 | 缓存优化，性能测试 |
| 重构范围过大 | 中 | 中 | 按模块分阶段重构 |

---

**文档版本**: 1.0
**创建日期**: 2026-02-09
**状态**: 草稿
