# 模型层优化指南

## 阶段 4.1: 关联加载策略优化

### 优化原则

SQLAlchemy 提供了多种关联加载策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `lazy='select'` | 首次访问时加载（默认） | 数据量小、不常使用 |
| `lazy='dynamic'` | 返回 Query 对象，支持链式过滤 | 数据量大、需要分页/过滤 |
| `lazy='joined'` | 立即加载（JOIN） | 一对一、总是需要一起加载 |
| `lazy='subquery'` | 子查询加载 | 一对多、需要批量加载 |

### User 模型优化

#### 优化前
所有关联使用默认 `lazy='select'`，导致 N+1 查询问题。

#### 优化后

**高频关联（lazy='dynamic'）**:
- `checkins` - 签到记录（可能大量数据）
- `notifications` - 通知消息（可能大量数据）
- `anomalies` - 异常记录（可能大量数据）
- `alerts` - 预警记录（可能大量数据）
- `devices` - 绑定设备（中频）

**中频关联（lazy='select'）**:
- `emergency_contacts` - 紧急联系人
- `sos_requests` - SOS请求
- `login_records` - 登录记录

**低频关联（lazy='select'）**:
- `emergency_calls` - 紧急呼叫
- `health_trends` - 健康趋势
- `activity_patterns` - 活动模式
- `medication_*` - 用药相关

**一对一关系**:
- `health_record` - `lazy='joined'`（常一起加载）
- `user_setting` - `lazy='select'`（按需加载）
- `alert_settings` - `lazy='select'`（按需加载）
- `notification_preferences` - `lazy='select'`（按需加载）

### 使用示例

```python
# dynamic 关联返回 Query 对象，支持链式操作
recent_checkins = user.checkins.filter(
    CheckIn.checkin_date >= '2024-01-01'
).order_by(desc(CheckIn.checkin_time)).limit(10).all()

# select 关联按需加载
emergency_contacts = user.emergency_contacts  # 触发查询

# joined 关联已加载
health_record = user.health_record  # 已加载，无需查询
```

## 阶段 4.2: 数据库索引优化

### 添加的索引

```python
# 复合索引：手机号+创建时间
Index("idx_users_phone_created", "phone", "created_at")

# 单字段索引：最后登录时间
Index("idx_users_last_sign_in", "last_sign_in")
```

### 索引设计原则

1. **高频查询字段**添加索引
2. **复合索引**遵循最左前缀原则
3. **排序字段**考虑添加索引
4. **避免过多索引**（影响写入性能）

## 阶段 4.3: to_dict() 性能优化

### 优化前
每次调用都使用 `inspect()` 动态检测关联关系，性能差。

### 优化后
1. 使用预定义的 `_RELATIONSHIP_NAMES` 集合
2. 支持选择性包含关联关系
3. 提供 `to_dict_with_relations()` 便捷方法

### 使用示例

```python
# 基础字典（排除所有关联）
user_dict = user.to_dict()

# 包含指定关联
user_dict = user.to_dict(include_relations=['emergency_contacts'])

# 包含多个关联并排除敏感字段
user_dict = user.to_dict_with_relations(
    relations=['emergency_contacts', 'devices'],
    exclude=['phone']
)
```

## 迁移步骤

1. 备份现有 `user.py`
2. 用 `user_optimized.py` 替换
3. 运行数据库迁移（索引变更）
4. 验证所有查询正常工作
5. 性能测试对比
