# 批次 2: 服务层更新

**复杂度**: 中等
**任务粒度**: 2-5分钟/任务
**总预估**: 20分钟

---

## 任务 US-2-1: 修复服务导入问题

**文件**: `backend/app/services/`
**时间**: 10分钟

### 问题
- `notification_service.py` 有循环导入
- `anomaly_service.py` 依赖有问题的 notification_service

### 步骤
1. [ ] 确认 `notification_service.py` 简化后工作正常
2. [ ] 检查 `anomaly_service.py` 导入
3. [ ] 修复其他服务的循环导入问题
4. [ ] 验证所有服务可导入

### 验证
```python
python -c "
from app.services import (
    UserService, CheckInService, SOSService,
    NotificationService, HealthRecordService
)
print('✅ All services OK')
"
```

---

## 任务 US-2-2: 统一服务使用 BaseService

**文件**: 多个服务文件
**时间**: 10分钟

### 步骤
1. [ ] 检查所有服务继承 BaseService
2. [ ] 确保 cache_prefix 设置正确
3. [ ] 确保使用统一的 CRUD 方法

---

## 批次完成检查

- [ ] 所有服务可正常导入
- [ ] 无循环导入错误
