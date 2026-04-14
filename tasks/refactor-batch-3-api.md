# 批次 3: API 层更新

**复杂度**: 中等
**任务粒度**: 2-5分钟/任务
**总预估**: 30分钟

---

## 任务 US-3-1: 更新用户相关路由

**文件**: `backend/app/api/users.py`
**时间**: 5分钟

### 当前代码
```python
@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    ...
```

### 目标代码
```python
@router.get("/users")
async def list_users(
    db: DbSession,
    current_user: CurrentUserDep,
):
    ...
```

---

## 任务 US-3-2: 更新签到相关路由

**文件**: `backend/app/api/checkins.py`
**时间**: 5分钟

---

## 任务 US-3-3: 更新 SOS 相关路由

**文件**: `backend/app/api/sos_requests.py`
**时间**: 5分钟

---

## 任务 US-3-4: 更新健康记录路由

**文件**: `backend/app/api/health_records.py`
**时间**: 5分钟

---

## 任务 US-3-5: 更新设备相关路由

**文件**: `backend/app/api/devices.py`
**时间**: 5分钟

---

## 任务 US-3-6: 更新其他路由

**文件**: 剩余 api 文件
**时间**: 5分钟

---

## 批次完成检查

- [ ] 所有 API 路由可正常注册
- [ ] FastAPI 启动无错误
