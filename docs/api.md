# 起了吗 App - API 文档

## 文档信息

- **版本**：v1.0
- **基础URL**：`http://localhost:8000/api/v1`
- **API文档**：启动服务后访问 `http://localhost:8000/docs` (Swagger UI)

---

## 1. 认证相关

### 1.1 用户注册

**请求**：
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "yourpassword",
  "nickname": "张三"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "uuid-string",
    "phone": "13800138000",
    "nickname": "张三",
    "created_at": "2026-01-26T10:00:00"
  }
}
```

### 1.2 用户登录

**请求**：
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=13800138000&password=yourpassword
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "jwt-token-string",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 1.3 刷新Token

**请求**：
```http
POST /api/v1/auth/refresh
Authorization: Bearer {token}
```

---

## 2. 用户相关

### 2.1 获取当前用户信息

**请求**：
```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "uuid-string",
    "phone": "13800138000",
    "nickname": "张三",
    "gender": 1,
    "birth_date": "1990-01-01",
    "blood_type": "A",
    "height": 175,
    "weight": 70
  }
}
```

### 2.2 更新用户信息

**请求**：
```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "nickname": "李四",
  "gender": 1,
  "height": 176
}
```

---

## 3. 签到相关

### 3.1 每日签到

**请求**：
```http
POST /api/v1/checkin
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "签到成功",
  "data": {
    "checkin_id": "uuid-string",
    "check_in_time": "2026-01-26T08:30:00",
    "status": "checked_in",
    "streak_days": 5
  }
}
```

### 3.2 获取签到历史

**请求**：
```http
GET /api/v1/checkin/history?page=1&limit=20
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "checkin_id": "uuid-string",
        "check_in_time": "2026-01-26T08:30:00",
        "status": "checked_in"
      }
    ]
  }
}
```

### 3.3 获取签到状态

**请求**：
```http
GET /api/v1/checkin/status
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "today_checked_in": true,
    "last_checkin_time": "2026-01-26T08:30:00",
    "streak_days": 5,
    "next_checkin_deadline": "2026-01-27T23:59:59"
  }
}
```

---

## 4. 紧急联系人相关

### 4.1 获取联系人列表

**请求**：
```http
GET /api/v1/contacts
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "contact_id": "uuid-string",
      "name": "张三",
      "phone": "13900139000",
      "relationship": "父母",
      "priority": 1,
      "notify_channels": ["push", "sms"]
    }
  ]
}
```

### 4.2 添加联系人

**请求**：
```http
POST /api/v1/contacts
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "李四",
  "phone": "13900139001",
  "relationship": "朋友",
  "priority": 2,
  "notify_channels": ["push", "sms", "call"]
}
```

### 4.3 更新联系人

**请求**：
```http
PUT /api/v1/contacts/{contact_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "李四",
  "phone": "13900139002"
}
```

### 4.4 删除联系人

**请求**：
```http
DELETE /api/v1/contacts/{contact_id}
Authorization: Bearer {token}
```

---

## 5. SOS紧急求助相关

### 5.1 触发SOS

**请求**：
```http
POST /api/v1/sos
Authorization: Bearer {token}
Content-Type: application/json

{
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "address": "北京市朝阳区xxx"
  },
  "message": "需要紧急救助"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "SOS已触发",
  "data": {
    "sos_id": "uuid-string",
    "status": "active",
    "trigger_time": "2026-01-26T10:30:00",
    "contacts_notified": 3
  }
}
```

### 5.2 获取SOS状态

**请求**：
```http
GET /api/v1/sos/{sos_id}
Authorization: Bearer {token}
```

### 5.3 取消SOS

**请求**：
```http
DELETE /api/v1/sos/{sos_id}
Authorization: Bearer {token}
```

---

## 6. 健康档案相关

### 6.1 获取健康档案

**请求**：
```http
GET /api/v1/health-profile
Authorization: Bearer {token}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "record_id": "uuid-string",
    "blood_type": "A",
    "height": 175,
    "weight": 70,
    "medical_history": [
      {
        "disease": "高血压",
        "diagnosed_date": "2020-01-01",
        "status": "控制中"
      }
    ],
    "medications": [
      {
        "name": "降压药",
        "dosage": "每日一次",
        "time": "早饭后"
      }
    ],
    "allergies": [
      {
        "allergen": "青霉素",
        "reaction": "皮疹"
      }
    ]
  }
}
```

### 6.2 更新健康档案

**请求**：
```http
PUT /api/v1/health-profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "blood_type": "A",
  "height": 176,
  "weight": 71,
  "medical_history": [...],
  "medications": [...],
  "allergies": [...]
}
```

---

## 7. 设备相关

### 7.1 获取设备列表

**请求**：
```http
GET /api/v1/devices
Authorization: Bearer {token}
```

### 7.2 绑定设备

**请求**：
```http
POST /api/v1/devices
Authorization: Bearer {token}
Content-Type: application/json

{
  "device_type": "smart_band",
  "device_id": "device-uuid",
  "device_name": "小米手环7"
}
```

### 7.3 上传设备数据

**请求**：
```http
POST /api/v1/devices/{device_id}/data
Authorization: Bearer {token}
Content-Type: application/json

{
  "data_type": "heart_rate",
  "value": 72,
  "timestamp": "2026-01-26T10:00:00"
}
```

---

## 8. 系统相关

### 8.1 健康检查

**请求**：
```http
GET /health
```

**响应**：
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 8.2 获取应用信息

**请求**：
```http
GET /
```

**响应**：
```json
{
  "app": "起了吗App",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 9. 错误码说明

| 错误码 | 含义 | 说明 |
|-------|------|------|
| 200 | 成功 | 请求成功 |
| 400 | 请求错误 | 参数错误或格式错误 |
| 401 | 未授权 | 需要登录 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 429 | 请求过多 | 超过限流阈值 |
| 500 | 服务器错误 | 服务器内部错误 |
| 1001 | 用户不存在 | 用户不存在 |
| 1002 | 手机号已注册 | 手机号已注册 |
| 1003 | 签到失败 | 签到失败（已签到、未登录等） |
| 1004 | 紧急联系人为空 | 紧急联系人为空 |
| 1005 | SOS触发失败 | SOS触发失败 |

---

## 10. 认证说明

所有需要认证的API都需要在请求头中包含：

```
Authorization: Bearer {access_token}
```

Token通过登录接口获取，默认有效期30分钟。
