# 起了吗App 项目改进PRD

## 1. 概述

### 1.1 项目背景
基于 `project-improvement-report.md` 的代码审查结果，项目存在服务层架构不一致、缓存策略不统一、安全缺陷等问题，需要进行系统性改进。

### 1.2 改进目标
- 统一100%服务类继承 BaseService
- 标准化缓存策略（TTL、键命名、失效逻辑）
- 修复安全缺陷（加密密钥管理）
- 统一API响应格式
- 提升测试覆盖率至85%+

---

## 2. 用户故事

### US-001: 修复加密密钥管理安全缺陷
**描述**: 作为开发人员，我希望 HealthRecordService 正确处理加密密钥，避免数据丢失风险

**验收标准**:
- [ ] 当 ENCRYPTION_KEY 环境变量未设置时，抛出明确的错误信息
- [ ] 提供生成密钥的命令行工具
- [ ] 加密服务在初始化时验证密钥有效性
- [ ] 所有现有测试仍然通过

**优先级**: P0 (安全关键)

---

### US-002: 添加缺失的服务导出
**描述**: 作为开发人员，我希望所有服务类都正确导出，便于统一导入使用

**验收标准**:
- [ ] EmergencyContactService 添加到 app/services/__init__.py
- [ ] __all__ 列表包含所有服务类
- [ ] 可以从 app.services 统一导入所有服务

**优先级**: P1

---

### US-003: 统一时间戳使用
**描述**: 作为开发人员，我希望 AlertService 统一使用 datetime.utcnow()，避免时区问题

**验收标准**:
- [ ] 检查并修复 AlertService 中所有 datetime.now() 调用
- [ ] 确保所有时间戳使用 UTC 时间
- [ ] 相关测试验证时间戳格式正确

**优先级**: P1

---

### US-004: 完善缓存失效逻辑
**描述**: 作为开发人员，我希望 EmergencyContactService 在数据变更时正确失效缓存

**验收标准**:
- [ ] create_emergency_contact 方法失效相关缓存
- [ ] update_emergency_contact 方法失效相关缓存
- [ ] delete_emergency_contact 方法失效相关缓存
- [ ] set_primary_contact 方法失效相关缓存

**优先级**: P1

---

### US-005: 创建统一缓存配置
**描述**: 作为开发人员，我希望有统一的缓存配置规范，避免TTL和键命名不一致

**验收标准**:
- [ ] 创建 app/core/cache_config.py 模块
- [ ] 定义按数据类型的 TTL 常量
- [ ] 定义统一的键前缀规范
- [ ] 所有服务使用统一的缓存配置

**优先级**: P1

---

### US-006: 重构 AlertService 继承 BaseService
**描述**: 作为开发人员，我希望 AlertService 继承 BaseService 以获得通用 CRUD 和缓存能力

**验收标准**:
- [ ] AlertService 继承 BaseService[Alert]
- [ ] 设置 model_class, cache_prefix, cache_ttl
- [ ] 保留业务特定方法（create_alert, resolve_alert 等）
- [ ] 使用统一的缓存策略替换原有缓存逻辑
- [ ] 所有测试通过

**优先级**: P2

---

### US-007: 重构 CheckInService 继承 BaseService
**描述**: 作为开发人员，我希望 CheckInService 继承 BaseService 以获得通用 CRUD 和缓存能力

**验收标准**:
- [ ] CheckInService 继承 BaseService[CheckIn]
- [ ] 设置 model_class, cache_prefix, cache_ttl
- [ ] 保留业务特定方法（签到统计、连续签到计算等）
- [ ] 使用统一的缓存策略替换原有缓存逻辑
- [ ] 所有测试通过

**优先级**: P2

---

### US-008: 重构 EmergencyContactService 继承 BaseService
**描述**: 作为开发人员，我希望 EmergencyContactService 继承 BaseService 以获得通用 CRUD 和缓存能力

**验收标准**:
- [ ] EmergencyContactService 继承 BaseService[EmergencyContact]
- [ ] 设置 model_class, cache_prefix, cache_ttl
- [ ] 保留业务特定方法（set_primary_contact 等）
- [ ] 完善缓存覆盖所有查询方法
- [ ] 所有测试通过

**优先级**: P2

---

### US-009: 重构 HealthRecordService 继承 BaseService
**描述**: 作为开发人员，我希望 HealthRecordService 继承 BaseService 并获得缓存能力

**验收标准**:
- [ ] HealthRecordService 继承 BaseService[HealthRecord]
- [ ] 修复加密密钥管理问题
- [ ] 添加健康档案查询缓存
- [ ] 所有测试通过

**优先级**: P2

---

### US-010: 重构 NotificationService 继承 BaseService
**描述**: 作为开发人员，我希望 NotificationService 继承 BaseService 并获得缓存能力

**验收标准**:
- [ ] NotificationService 继承 BaseService[Notification]
- [ ] 添加通知列表查询缓存
- [ ] 添加通知偏好设置缓存
- [ ] 所有测试通过

**优先级**: P2

---

### US-011: 重构其他服务类
**描述**: 作为开发人员，我希望所有剩余服务类都继承 BaseService

**需要重构的服务**:
- AnomalyService
- EmergencyCenterService
- EmergencyResourceService
- EmergencyService
- LocationService
- SOSService

**验收标准**:
- [ ] 每个服务继承 BaseService
- [ ] 设置相应的 model_class, cache_prefix, cache_ttl
- [ ] 所有测试通过

**优先级**: P2

---

### US-012: 完善异常体系
**描述**: 作为开发人员，我希望有 ResourceNotFoundException 等特定异常，替代返回 None

**验收标准**:
- [ ] 添加 ResourceNotFoundException
- [ ] 添加 ValidationException
- [ ] 在 BaseService 中添加 get_by_id_or_raise 方法
- [ ] 更新全局异常处理器

**优先级**: P2

---

### US-013: 统一API响应格式
**描述**: 作为开发人员，我希望所有API端点使用统一的响应格式

**验收标准**:
- [ ] 所有API路由使用 APIResponse 类
- [ ] 错误响应使用统一格式
- [ ] 保留向后兼容性（如果必要）
- [ ] API测试验证响应格式

**优先级**: P3

---

### US-014: 提升测试覆盖率至85%+
**描述**: 作为开发人员，我希望测试覆盖率达到85%以上，确保代码质量

**验收标准**:
- [ ] 服务基类测试
- [ ] 缓存配置测试
- [ ] 加密服务测试
- [ ] API响应格式测试
- [ ] 整体覆盖率 >= 85%

**优先级**: P3

---

## 3. 非目标

- 不修改数据库模型结构
- 不添加新功能特性
- 不改变现有API接口契约（路径、参数）
- 不引入新的外部依赖（除测试相关）

---

## 4. 技术方案

### 4.1 缓存配置规范

```python
# app/core/cache_config.py
class CacheConfig:
    """统一缓存配置"""
    
    # TTL 配置（秒）
    TTL_USER_INFO = 300
    TTL_VERIFY_CODE = 300
    TTL_CHECKIN_STATUS = 600
    TTL_CHECKIN_STATS = 1800
    TTL_ALERT_SETTING = 1800
    TTL_ALERT_LIST = 300
    TTL_EMERGENCY_CONTACTS = 600
    TTL_HEALTH_RECORD = 600
    TTL_NOTIFICATION = 300
    TTL_DEVICE_INFO = 600
    
    # 键前缀
    PREFIX_USER = "user"
    PREFIX_CHECKIN = "checkin"
    PREFIX_ALERT = "alert"
    PREFIX_EMERGENCY = "emergency"
    PREFIX_HEALTH = "health"
    PREFIX_NOTIFICATION = "notification"
    PREFIX_DEVICE = "device"
```

### 4.2 服务重构模式

```python
# 重构前
class AlertService:
    @staticmethod
    def get_setting(db, user_id):
        cache_key = f"alert:setting:{user_id}"
        cached = get_cached(cache_key)
        if cached:
            return cached
        setting = db.query(AlertSetting).filter(...).first()
        if setting:
            cache_result(cache_key, setting, ttl=1800)
        return setting

# 重构后
class AlertService(BaseService[Alert]):
    model_class = Alert
    cache_prefix = CacheConfig.PREFIX_ALERT
    cache_ttl = CacheConfig.TTL_ALERT_LIST
    
    # 继承的通用方法: get_by_id, list_records, create_record, update_record, delete_record
    # 业务特定方法保留
```

### 4.3 加密服务修复

```python
class EncryptionService:
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY environment variable must be set. "
                "Run: python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\""
            )
        try:
            self.cipher = Fernet(key.encode())
        except ValueError as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY: {e}")
```

---

## 5. 验收标准总结

| 指标 | 当前 | 目标 |
|------|------|------|
| 服务基类采用率 | 14% (2/14) | 100% (14/14) |
| 缓存策略一致性 | 40% | 100% |
| 安全缺陷 | 1个 | 0个 |
| API响应一致性 | 60% | 100% |
| 测试覆盖率 | ~75% | >=85% |
| 测试通过率 | 403/403 | 全部通过 |

---

## 6. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重构引入回归bug | 高 | 每个服务重构后运行全部测试 |
| 缓存策略变更影响性能 | 中 | 逐步迁移，保持原有TTL |
| 加密密钥修复导致数据无法解密 | 高 | 提供数据迁移工具 |

---

## 7. 时间估算

- 快速修复（US-001~004）: 2小时
- 缓存配置（US-005）: 1小时
- 服务重构（US-006~011）: 3天
- 异常体系（US-012）: 4小时
- API标准化（US-013）: 1天
- 测试补充（US-014）: 2天

**总计**: 约6-7个工作日
