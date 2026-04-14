# 批次 1: 核心模型重构

**复杂度**: 复杂
**任务粒度**: 1-3分钟/任务
**总预估**: 90分钟

---

## 任务 US-1-1: 重构 User 模型

**文件**: `backend/app/models/user.py`
**时间**: 10分钟

### 当前代码
```python
class User(Base, BaseModelMixin):
    user_id = Column(String(36), primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    # ... Column() 定义
    emergency_contacts = db_relationship("EmergencyContact", ...)
```

### 目标代码
```python
class User(Base, BaseModelMixin):
    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(11), unique=True, index=True)
    # ... mapped_column() 定义
    emergency_contacts: Mapped[List["EmergencyContact"]] = relationship(...)
```

### 步骤
1. [ ] 添加 `Mapped`, `mapped_column` 导入
2. [ ] 转换所有 `Column()` → `mapped_column()`
3. [ ] 添加类型注解 `Mapped[Type]`
4. [ ] 转换 `db_relationship` → `Mapped[List[T]]`
5. [ ] 验证导入成功

### 验证
```python
python -c "from app.models.user import User; print('✅ User model OK')"
```

---

## 任务 US-1-2: 重构 CheckIn 模型

**文件**: `backend/app/models/checkin.py`
**时间**: 10分钟

### 步骤
1. [ ] 添加 SQLAlchemy 2.x 导入
2. [ ] 转换字段定义
3. [ ] 更新关系定义
4. [ ] 验证导入

---

## 任务 US-1-3: 重构 SOSRequest 模型

**文件**: `backend/app/models/sos_request.py`
**时间**: 10分钟

---

## 任务 US-1-4: 重构 Notification 模型

**文件**: `backend/app/models/notification_model.py`
**时间**: 10分钟

---

## 任务 US-1-5: 重构 HealthRecord 模型

**文件**: `backend/app/models/health_record.py`
**时间**: 10分钟

---

## 任务 US-1-6: 重构 Device 模型

**文件**: `backend/app/models/device.py`
**时间**: 10分钟

---

## 任务 US-1-7: 重构 EmergencyContact 模型

**文件**: `backend/app/models/emergency_contact.py`
**时间**: 10分钟

---

## 任务 US-1-8: 重构 Alert 模型

**文件**: `backend/app/models/alert.py`
**时间**: 10分钟

---

## 任务 US-1-9: 重构剩余模型

**文件**: 多个模型文件
**时间**: 30分钟

### 模型列表
- [ ] `medication.py` - Medication, MedicationSchedule, MedicationReminder
- [ ] `anomaly.py` - Anomaly, AnomalyDetectionRule
- [ ] `device_data.py` - DeviceData
- [ ] `emergency_center_model.py` - EmergencyCenter
- [ ] `emergency_resource_model.py` - EmergencyResource
- [ ] `knowledge_base.py` - KnowledgeBaseArticle
- [ ] `login_record.py` - LoginRecord
- [ ] `user_setting_model.py` - UserSetting

---

## 批次完成检查

- [ ] 所有模型可正常导入
- [ ] 无 SQLAlchemy 弃用警告
- [ ] 数据库结构未改变
