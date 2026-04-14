# 批次 5: 验证和回归测试

**复杂度**: 简单
**任务粒度**: 5-10分钟/任务
**总预估**: 15分钟

---

## 任务 US-5-1: 验证所有模块导入

**时间**: 5分钟

### 验证命令
```bash
cd backend
python -c "
# 核心模块
from app.core.database import Base, engine
from app.core.query_builder import QueryBuilder
from app.core.cache_mixin import CacheMixin

# 模型
from app.models.user import User
from app.models.checkin import CheckIn
from app.models.sos_request import SOSRequest

# 服务
from app.services import BaseService, UserService

# API
from app.api import api_router

print('✅ All imports OK')
"
```

---

## 任务 US-5-2: 运行测试套件

**时间**: 10分钟

### 验证命令
```bash
cd backend
pytest tests/ -v --tb=short
```

### 检查项
- [ ] 测试通过率 100%
- [ ] 无 Pydantic 弃用警告
- [ ] 无 SQLAlchemy 弃用警告

---

## 批次完成检查

- [ ] 所有模块可导入
- [ ] pytest 通过率 100%
- [ ] 无弃用警告
