# 数据库迁移

本目录包含数据库模式变更的迁移脚本。

## 使用说明

### 初始化Alembic
```bash
alembic init migrations
```

### 创建新的迁移
```bash
alembic revision --autogenerate -m "描述变更"
```

### 应用迁移
```bash
alembic upgrade head
```

### 回滚迁移
```bash
alembic downgrade -1
```

## 迁移文件命名规范

迁移文件应使用以下命名格式：
```
YYYYMMDD_HHMMSS_描述变更.py
```

例如：
```
20240211_143000_add_user_phone_number.py
```

## 注意事项

- 迁移脚本必须是幂等的
- 每个迁移应该包含升级和降级操作
- 在生产环境应用迁移前，请先在测试环境验证
- 迁移脚本应该包含必要的错误处理