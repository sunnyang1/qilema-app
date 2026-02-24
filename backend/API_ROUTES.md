# API 路由文档

本文档说明起了吗 App 的 API 路由设计和使用规范。

## 路由前缀策略

### 统一路由前缀

所有 API 路由使用统一前缀：`/api/v1`

**示例：**
```
GET    /api/v1/users/{id}
POST   /api/v1/users
GET    /api/v1/anomalies/{id}
```

### 路由分组

路由按功能模块分组：

| 模块 | 路径前缀 | 说明 |
|------|---------|------|
| 用户 | `/api/v1/users` | 用户管理相关接口 |
| 异常 | `/api/v1/anomalies` | 异常检测相关接口 |
| 通知 | `/api/v1/notifications` | 通知服务相关接口 |
| 心跳 | `/api/v1/health` | 健康检查接口 |

## RESTful 路由规范

### 标准方法

| HTTP 方法 | 用途 | 示例 |
|-----------|------|------|
| GET | 查询资源 | `GET /api/v1/users/{id}` |
| POST | 创建资源 | `POST /api/v1/users` |
| PUT | 更新资源（全量） | `PUT /api/v1/users/{id}` |
| PATCH | 更新资源（部分） | `PATCH /api/v1/users/{id}` |
| DELETE | 删除资源 | `DELETE /api/v1/users/{id}` |

### 命名规范

- 使用复数名词：`/users`, `/anomalies`
- 使用小写字母和连字符：`/api/v1/user-contacts`
- 避免动词：使用 `GET /api/v1/users` 而不是 `GET /api/v1/get-users`

## 认证与权限

### 认证方式

当前使用简单的用户 ID 认证，在生产环境中应升级为 JWT 或 OAuth2。

**请求头示例：**
```
X-User-Id: user_12345
```

### 权限控制

- 用户只能访问自己的资源
- 异常检测和通知推送需要用户认证

## API 端点列表

### 健康检查

#### 健康检查

```http
GET /api/v1/health
```

**响应示例：**
```json
{
  "status": "ok",
  "timestamp": "2025-01-19T12:00:00Z"
}
```

### 用户管理

#### 获取用户信息

```http
GET /api/v1/users/{user_id}
```

**响应示例：**
```json
{
  "id": "user_12345",
  "name": "张三",
  "contacts": [
    {
      "id": 1,
      "name": "李四",
      "phone": "13800138000",
      "relation": "家人"
    }
  ],
  "created_at": "2025-01-19T10:00:00Z",
  "updated_at": "2025-01-19T12:00:00Z"
}
```

#### 创建用户

```http
POST /api/v1/users
```

**请求体：**
```json
{
  "name": "张三",
  "contacts": [
    {
      "name": "李四",
      "phone": "13800138000",
      "relation": "家人"
    }
  ]
}
```

**响应示例：**
```json
{
  "id": "user_12345",
  "name": "张三",
  "contacts": [
    {
      "id": 1,
      "name": "李四",
      "phone": "13800138000",
      "relation": "家人"
    }
  ],
  "created_at": "2025-01-19T12:00:00Z"
}
```

#### 更新用户信息

```http
PUT /api/v1/users/{user_id}
```

**请求体：**
```json
{
  "name": "张三",
  "contacts": [
    {
      "name": "李四",
      "phone": "13800138000",
      "relation": "家人"
    }
  ]
}
```

#### 删除用户

```http
DELETE /api/v1/users/{user_id}
```

#### 添加紧急联系人

```http
POST /api/v1/users/{user_id}/contacts
```

**请求体：**
```json
{
  "name": "李四",
  "phone": "13800138000",
  "relation": "家人"
}
```

#### 删除紧急联系人

```http
DELETE /api/v1/users/{user_id}/contacts/{contact_id}
```

### 异常检测

#### 获取异常列表

```http
GET /api/v1/users/{user_id}/anomalies
```

**响应示例：**
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "user_id": "user_12345",
      "type": "daily_check_missed",
      "timestamp": "2025-01-19T12:00:00Z",
      "resolved": false
    }
  ]
}
```

#### 获取异常详情

```http
GET /api/v1/anomalies/{anomaly_id}
```

**响应示例：**
```json
{
  "id": 1,
  "user_id": "user_12345",
  "type": "daily_check_missed",
  "timestamp": "2025-01-19T12:00:00Z",
  "resolved": false,
  "resolved_at": null,
  "resolved_by": null
}
```

#### 标记异常已解决

```http
POST /api/v1/anomalies/{anomaly_id}/resolve
```

**请求体：**
```json
{
  "resolved_by": "user_12345"
}
```

### 通知服务

#### 发送通知

```http
POST /api/v1/notifications/send
```

**请求体：**
```json
{
  "user_id": "user_12345",
  "title": "测试通知",
  "content": "这是一条测试通知",
  "channels": ["push", "sms"]
}
```

**响应示例：**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "notif_12345",
      "channel": "push",
      "status": "sent"
    },
    {
      "id": "notif_12346",
      "channel": "sms",
      "status": "sent"
    }
  ]
}
```

#### 获取通知历史

```http
GET /api/v1/users/{user_id}/notifications
```

**响应示例：**
```json
{
  "total": 20,
  "items": [
    {
      "id": "notif_12345",
      "user_id": "user_12345",
      "title": "测试通知",
      "content": "这是一条测试通知",
      "channel": "push",
      "status": "sent",
      "created_at": "2025-01-19T12:00:00Z"
    }
  ]
}
```

## 错误处理

### 标准错误响应

所有错误响应遵循以下格式：

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "code": "ERROR_CODE",
  "details": {
    "field": "error details"
  }
}
```

### HTTP 状态码

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器错误 |
| 503 | Service Unavailable | 服务不可用 |

### 错误代码

| 代码 | 说明 |
|------|------|
| VALIDATION_ERROR | 参数验证失败 |
| RESOURCE_NOT_FOUND | 资源不存在 |
| UNAUTHORIZED | 未授权访问 |
| RATE_LIMIT_EXCEEDED | 超过速率限制 |
| CIRCUIT_BREAKER_OPEN | 熔断器已打开 |
| SERVICE_UNAVAILABLE | 服务不可用 |

## 限流策略

为了保护服务稳定性，API 实施了以下限流策略：

- 每个用户每分钟最多发送 10 条通知
- 每个用户每小时最多发送 100 条通知
- 超过限制返回 429 状态码

## 版本控制

当前 API 版本：`v1`

### 版本更新策略

- 主版本号：破坏性更改
- 次版本号：新功能（向后兼容）
- 修订版本号：Bug 修复

### 废弃策略

- 废弃的 API 将在响应头中包含 `X-Deprecated: true`
- 废弃的 API 将至少保留 3 个月

## 测试

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 获取用户信息
curl -H "X-User-Id: user_12345" \
     http://localhost:8000/api/v1/users/user_12345

# 创建用户
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"张三"}' \
     http://localhost:8000/api/v1/users
```

### 使用 Python requests 测试

```python
import requests

# 健康检查
response = requests.get('http://localhost:8000/api/v1/health')
print(response.json())

# 获取用户信息
response = requests.get(
    'http://localhost:8000/api/v1/users/user_12345',
    headers={'X-User-Id': 'user_12345'}
)
print(response.json())
```

## 最佳实践

1. **始终使用 HTTPS**：生产环境必须使用 HTTPS
2. **验证输入**：客户端应验证所有输入
3. **处理错误**：客户端应正确处理所有错误响应
4. **使用缓存**：频繁请求的数据应使用缓存
5. **监控使用**：监控 API 调用频率和错误率

## 安全建议

1. **认证升级**：使用 JWT 或 OAuth2 替代简单的用户 ID 认证
2. **加密传输**：所有敏感数据应加密传输
3. **输入验证**：严格验证所有输入，防止注入攻击
4. **访问控制**：实施细粒度的访问控制
5. **审计日志**：记录所有 API 调用，用于审计
