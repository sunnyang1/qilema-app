---
name: project-improvement-plan
overview: 基于项目改进报告，创建服务层架构统一、缓存策略标准化、安全修复的完整改进计划
todos:
  - id: fix-encryption
    content: 修复HealthRecordService加密密钥管理缺陷
    status: pending
  - id: export-service
    content: 添加EmergencyContactService到app/services/__init__.py
    status: pending
  - id: fix-timestamp
    content: 统一AlertService时间戳使用(datetime.utcnow)
    status: pending
  - id: cache-invalidation
    content: 添加EmergencyContactService缓存失效逻辑
    status: pending
  - id: cache-config
    content: 创建统一缓存配置模块app/core/cache_config.py
    status: pending
  - id: refactor-alert
    content: 重构AlertService继承BaseService并统一缓存策略
    status: pending
    dependencies:
      - cache-config
  - id: refactor-checkin
    content: 重构CheckInService继承BaseService并统一缓存策略
    status: pending
    dependencies:
      - cache-config
  - id: refactor-emergency
    content: 重构EmergencyContactService继承BaseService并完善缓存
    status: pending
    dependencies:
      - cache-config
  - id: refactor-health
    content: 重构HealthRecordService继承BaseService并添加缓存
    status: pending
    dependencies:
      - fix-encryption
      - cache-config
  - id: refactor-notification
    content: 重构NotificationService继承BaseService并添加缓存
    status: pending
    dependencies:
      - cache-config
  - id: refactor-other-services
    content: 重构其他服务类继承BaseService
    status: pending
    dependencies:
      - refactor-alert
      - refactor-checkin
  - id: exception-system
    content: 完善异常体系添加ResourceNotFoundException
    status: pending
  - id: api-standardization
    content: 统一API层响应格式
    status: pending
    dependencies:
      - exception-system
  - id: test-service-refactor
    content: 添加服务重构测试
    status: pending
    dependencies:
      - refactor-alert
      - refactor-checkin
      - refactor-emergency
  - id: test-coverage
    content: 提升测试覆盖率至85%+
    status: pending
    dependencies:
      - test-service-refactor
  - id: final-verify
    content: 全面验证所有测试通过并生成报告
    status: pending
    dependencies:
      - test-coverage
---

## 产品概述

根据项目改进分析报告，实施起了吗App的全面改进计划，包括架构统一、缓存优化、安全修复和测试完善。

## 核心功能需求

### 阶段1: 快速修复 (立即执行)

- 修复HealthRecordService加密密钥管理缺陷
- 添加EmergencyContactService到服务导出
- 统一AlertService时间戳使用
- 完善EmergencyContactService缓存失效逻辑

### 阶段2: 架构统一 (1-2周)

- 重构AlertService继承BaseService并统一缓存策略
- 重构CheckInService继承BaseService并统一缓存策略
- 重构EmergencyContactService继承BaseService并完善缓存
- 重构HealthRecordService继承BaseService并添加缓存
- 重构NotificationService继承BaseService并添加缓存
- 重构其他服务类(AnomalyService等)继承BaseService

### 阶段3: 缓存策略统一 (1周)

- 创建统一缓存配置模块(cache_config.py)
- 标准化缓存TTL和键命名规范
- 统一缓存失效策略
- 添加缓存性能监控

### 阶段4: API层标准化 (1周)

- 统一API响应格式使用APIResponse
- 完善全局异常处理
- 添加资源不存在异常(ResourceNotFoundException)

### 阶段5: 测试完善 (1-2周)

- 补充服务基类继承测试
- 添加缓存策略测试
- 提升整体测试覆盖率至85%+

## 技术栈

- **后端框架**: Python + FastAPI
- **数据库**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **缓存**: Redis
- **测试**: pytest
- **加密**: cryptography.fernet

## 技术方案

### 架构设计

采用分层架构，统一服务层基类:

```
app/
├── core/
│   ├── cache_config.py      # [NEW] 统一缓存配置
│   ├── cache.py             # [已有] 缓存工具
│   ├── exceptions.py        # [MODIFY] 添加ResourceNotFoundException
│   └── response.py          # [已有] API响应格式
├── services/
│   ├── base_service.py      # [已有] 服务基类
│   ├── alert_service.py     # [MODIFY] 继承BaseService
│   ├── checkin_service.py   # [MODIFY] 继承BaseService
│   ├── emergency_contact_service.py  # [MODIFY] 继承BaseService
│   ├── health_record_service.py      # [MODIFY] 继承BaseService+修复加密
│   ├── notification_service.py       # [MODIFY] 继承BaseService
│   └── __init__.py          # [MODIFY] 导出EmergencyContactService
└── tests/
    ├── test_service_refactoring.py   # [NEW] 服务重构测试
    ├── test_cache_config.py          # [NEW] 缓存配置测试
    └── test_health_record_encryption.py  # [NEW] 加密修复测试
```

### 关键改进点

1. **服务基类统一**: 所有服务继承BaseService[ModelType]，获得统一CRUD和缓存能力
2. **加密密钥管理**: HealthRecordService强制要求ENCRYPTION_KEY环境变量
3. **缓存策略标准化**: 统一TTL、键前缀、失效逻辑
4. **异常体系完善**: 添加ResourceNotFoundException等特定异常

## 实现注意事项

1. **向后兼容**: 保持现有API接口不变，仅内部实现重构
2. **渐进式迁移**: 按优先级逐步重构服务类
3. **测试覆盖**: 每个重构的服务类必须配套测试用例
4. **缓存一致性**: 确保所有写操作正确失效相关缓存

## Agent Extensions

### Skill

- **superpower**: 软件开发生命周期管理，集成TDD、PRD驱动开发和自主迭代
- Purpose: 用于实施所有改进任务，确保每个重构都遵循TDD原则
- Expected outcome: 按照PRD要求完成所有功能实现，确保测试通过

### SubAgent

- **code-explorer**: 用于代码库探索和分析
- Purpose: 识别需要重构的服务类，分析代码重复和依赖关系
- Expected outcome: 生成详细的服务类重构清单和依赖关系图