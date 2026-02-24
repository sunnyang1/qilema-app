# 后端服务调试和测试完整指南

## 目录
1. [快速开始](#快速开始)
2. [详细步骤](#详细步骤)
3. [测试说明](#测试说明)
4. [常见问题](#常见问题)
5. [前端适配](#前端适配)

---

## 快速开始

### 一键启动和测试

```bash
# 1. 启动后端服务
cd /workspace/projects/backend
chmod +x start_backend.sh
./start_backend.sh

# 2. 执行 API 测试
chmod +x test_api.sh
./test_api.sh
```

---

## 详细步骤

### 步骤 1: 检查后端服务状态

```bash
# 检查是否有运行中的服务
ps aux | grep -E "python.*uvicorn|python.*start_server" | grep -v grep

# 如果有旧服务，停止它
pkill -f "python.*uvicorn"
pkill -f "python.*start_server"

# 检查端口 8000 是否被占用
lsof -i :8000
```

**预期结果**：
- 无旧服务运行
- 端口 8000 未被占用

### 步骤 2: 启动后端服务

#### 方式 1: 使用启动脚本（推荐）

```bash
cd /workspace/projects/backend
chmod +x start_backend.sh
./start_backend.sh
```

#### 方式 2: 手动启动

```bash
cd /workspace/projects/backend
pkill -f "python.*uvicorn"
python3 start_server.py > /tmp/backend.log 2>&1 &
```

**预期结果**：
- 服务进程运行中（PID 显示）
- 健康检查返回 `{"code":200,"message":"success",...}`

### 步骤 3: 检查服务状态

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 查看日志
tail -30 /tmp/backend.log
```

**预期结果**：
- 健康检查 HTTP 200
- 日志无错误信息

### 步骤 4: 测试认证流程

#### 4.1 注册用户

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "Test123456",
    "name": "测试用户"
  }'
```

**预期结果**：
```json
{
  "code": 200,
  "message": "success",
  "data": {"user_id": "..."},
  "timestamp": 1234567890
}
```

#### 4.2 登录获取 token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=13800138000&password=Test123456"
```

**预期结果**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "user_id": "...",
      "phone": "13800138000",
      ...
    }
  },
  "timestamp": 1234567890
}
```

**重要**：保存返回的 `access_token`，后续所有请求都需要使用。

```bash
# 设置环境变量
export TOKEN="your_access_token_here"
```

#### 4.3 获取当前用户信息（关键测试）

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**预期结果**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_id": "...",
    "phone": "13800138000",
    "nickname": "测试用户",
    "gender": "0",
    "blood_type": "UNKNOWN",
    "height": null,
    "weight": null,
    "birth_date": null,
    "created_at": "2024-01-01T00:00:00"
  },
  "timestamp": 1234567890
}
```

**关键点**：
- 必须返回 `code: 200`
- 不应出现 `RecursionError`
- 返回数据为字典（非 ORM 对象）

### 步骤 5: 测试其他功能模块

#### 5.1 签到功能

```bash
# 创建签到
curl -X POST http://localhost:8000/api/v1/checkins \
  -H "Authorization: Bearer $TOKEN"

# 获取签到记录
curl http://localhost:8000/api/v1/checkins \
  -H "Authorization: Bearer $TOKEN"

# 获取今日签到
curl http://localhost:8000/api/v1/checkins/today \
  -H "Authorization: Bearer $TOKEN"
```

#### 5.2 设备管理

```bash
# 获取设备列表
curl http://localhost:8000/api/v1/devices \
  -H "Authorization: Bearer $TOKEN"

# 绑定设备
curl -X POST http://localhost:8000/api/v1/devices/bind \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "smartband_001",
    "device_type": "smart_band",
    "device_name": "智能手环"
  }'
```

#### 5.3 健康档案

```bash
# 获取健康档案
curl http://localhost:8000/api/v1/health-records/1 \
  -H "Authorization: Bearer $TOKEN"

# 创建健康档案
curl -X POST http://localhost:8000/api/v1/health-records \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "real_name": "张三",
    "gender": "男",
    "blood_type": "A",
    "height": 175,
    "weight": 70,
    "age": 30
  }'
```

#### 5.4 紧急联系人

```bash
# 获取紧急联系人列表
curl http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN"

# 创建紧急联系人
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "紧急联系人1",
    "phone": "13800138001",
    "relation": "配偶",
    "is_primary": true
  }'

# 设置主要联系人
curl -X PUT http://localhost:8000/api/v1/contacts/1/primary \
  -H "Authorization: Bearer $TOKEN"
```

#### 5.5 SOS 求助

```bash
# 创建 SOS 求助
curl -X POST http://localhost:8000/api/v1/sos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 39.9042,
    "longitude": 116.4074,
    "location": "北京市朝阳区",
    "emergency_level": "high"
  }'

# 获取 SOS 记录
curl http://localhost:8000/api/v1/sos \
  -H "Authorization: Bearer $TOKEN"
```

#### 5.6 其他接口

```bash
# 获取急救知识
curl "http://localhost:8000/api/v1/knowledge?limit=5" \
  -H "Authorization: Bearer $TOKEN"

# 获取用药提醒
curl http://localhost:8000/api/v1/medications \
  -H "Authorization: Bearer $TOKEN"

# 获取 AED 设备
curl "http://localhost:8000/api/v1/aed?latitude=39.9042&longitude=116.4074&radius=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 测试说明

### 使用自动化测试脚本

```bash
cd /workspace/projects/backend
chmod +x test_api.sh
./test_api.sh
```

测试脚本会自动执行以下步骤：
1. ✅ 健康检查
2. ✅ 注册用户
3. ✅ 登录获取 token
4. ✅ 获取用户信息
5. ✅ 创建签到
6. ✅ 获取签到记录
7. ✅ 获取设备列表
8. ✅ 获取健康档案
9. ✅ 获取紧急联系人
10. ✅ 创建 SOS 求助
11. ✅ 获取急救知识
12. ✅ 获取用药提醒

### 测试结果标识

- ✅ **成功**：接口返回 HTTP 200/201
- ⚠️ **警告**：接口返回其他 HTTP 状态码（可能是正常情况，如空数据）
- ❌ **失败**：接口返回错误或无法访问

---

## 常见问题

### 问题 1: 服务无法启动

**症状**：
- 执行 `start_backend.sh` 后进程立即退出
- 日志显示 `SECRET_KEY` 验证失败

**解决方案**：
```bash
# 检查日志
tail -50 /tmp/backend.log

# 如果是 SECRET_KEY 问题，检查配置
cd /workspace/projects/backend
grep -A 5 "SECRET_KEY" app/core/config.py
```

### 问题 2: RecursionError（循环引用）

**症状**：
- 访问 `/api/v1/auth/me` 返回 500 错误
- 日志显示 `RecursionError: maximum recursion depth exceeded`

**解决方案**：
```bash
# 检查日志
tail -50 /tmp/backend.log | grep -A 10 "RecursionError"

# 确认以下修改已生效：
# 1. app/core/security.py 中 get_current_user 返回字典
# 2. app/models/user.py 中 to_dict 排除关联关系
# 3. app/api/auth.py 中使用 JSONResponse
```

### 问题 3: 路由路径不匹配

**症状**：
- 接口返回 404 Not Found
- 路由路径不符合 `/api/v1/{resource}` 格式

**解决方案**：
```bash
# 检查路由注册
cd /workspace/projects/backend
grep -r "include_router" app/api/__init__.py

# 确认最终路径格式
# 例如：/api/v1/devices, /api/v1/health-records 等
```

### 问题 4: 认证失败

**症状**：
- 返回 401 Unauthorized
- Token 无效或过期

**解决方案**：
```bash
# 重新登录获取新 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=13800138000&password=Test123456"

# 检查 token 格式
# 应该是：Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 问题 5: 数据库错误

**症状**：
- 返回 500 错误
- 日志显示数据库相关错误

**解决方案**：
```bash
# 检查数据库文件
ls -la /workspace/projects/backend/qilema.db

# 重新初始化数据库（谨慎操作）
cd /workspace/projects/backend
rm qilema.db
python3 -c "from app.core.database import init_db; init_db()"
```

---

## 前端适配

### 1. 更新 API 常量

文件：`mobile/client/constants/app.ts`

```typescript
export const API_ENDPOINTS = {
  // 基础路径
  BASE_URL: process.env.EXPO_PUBLIC_BACKEND_BASE_URL,

  // 认证
  AUTH_LOGIN: '/api/v1/auth/login',
  AUTH_REGISTER: '/api/v1/auth/register',
  AUTH_ME: '/api/v1/auth/me',
  AUTH_REFRESH: '/api/v1/auth/refresh',
  AUTH_LOGOUT: '/api/v1/auth/logout',

  // 签到
  CHECKINS: '/api/v1/checkins',
  CHECKIN_CREATE: '/api/v1/checkins',
  CHECKIN_TODAY: '/api/v1/checkins/today',

  // SOS 求助
  SOS_REQUESTS: '/api/v1/sos',
  SOS_CREATE: '/api/v1/sos',

  // 设备管理
  DEVICES: '/api/v1/devices',
  DEVICE_BIND: '/api/v1/devices/bind',
  DEVICE_UNBIND: '/api/v1/devices/{device_id}/unbind',

  // 健康档案
  HEALTH_RECORDS: '/api/v1/health-records',
  HEALTH_RECORD: '/api/v1/health-records/{user_id}',
  HEALTH_RECORD_SUMMARY: '/api/v1/health-records/{user_id}/summary',

  // 紧急联系人
  CONTACTS: '/api/v1/contacts',
  CONTACT_PRIMARY: '/api/v1/contacts/primary',
  CONTACT_SET_PRIMARY: '/api/v1/contacts/{id}/primary',

  // 急救知识
  KNOWLEDGE: '/api/v1/knowledge',

  // 用药提醒
  MEDICATIONS: '/api/v1/medications',
  MEDICATION_CREATE: '/api/v1/medications',

  // AED 设备
  AED: '/api/v1/aed',
};
```

### 2. 处理响应格式

文件：`mobile/client/types/api.ts`

```typescript
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T | null;
  timestamp: number;
}

interface UserInfo {
  user_id: string;
  phone: string;
  nickname: string | null;
  gender: string | null;
  blood_type: string | null;
  height: number | null;
  weight: number | null;
  birth_date: string | null;
  created_at: string | null;
}

interface Checkin {
  id: number;
  user_id: string;
  checkin_time: string;
  location?: string;
  latitude?: number;
  longitude?: number;
}

// ... 其他类型定义
```

### 3. API 请求示例

文件：`mobile/client/services/authService.ts`

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_ENDPOINTS } from '@/constants/app';

const BASE_URL = process.env.EXPO_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

export const authService = {
  // 登录
  async login(phone: string, password: string) {
    const formData = new FormData();
    formData.append('username', phone);
    formData.append('password', password);

    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.AUTH_LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const result: ApiResponse<{ access_token: string; user: UserInfo }> = await response.json();

    if (result.code === 200 && result.data) {
      // 保存 token
      await AsyncStorage.setItem('access_token', result.data.access_token);
      return result.data;
    }

    throw new Error(result.message);
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<UserInfo> {
    const token = await AsyncStorage.getItem('access_token');

    const response = await fetch(`${BASE_URL}${API_ENDPOINTS.AUTH_ME}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const result: ApiResponse<UserInfo> = await response.json();

    if (result.code === 200 && result.data) {
      return result.data;
    }

    throw new Error(result.message);
  },

  // 登出
  async logout() {
    await AsyncStorage.removeItem('access_token');
  },
};
```

### 4. 请求拦截器

文件：`mobile/client/utils/apiClient.ts`

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const BASE_URL = process.env.EXPO_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

  // 获取 token
  const token = await AsyncStorage.getItem('access_token');

  // 合并 headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // 添加认证头
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // 发送请求
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const result = await response.json();

  // 检查响应状态
  if (result.code !== 200) {
    throw new Error(result.message || '请求失败');
  }

  return result.data;
}

// 使用示例
// import { apiRequest } from '@/utils/apiClient';
// const user = await apiRequest('/api/v1/auth/me');
```

---

## 总结

### 已完成的修复

1. ✅ 路由配置统一（`/api/v1/{resource}`）
2. ✅ 序列化问题修复（返回字典而非 ORM 对象）
3. ✅ 配置问题修复（SECRET_KEY）
4. ✅ 提供启动脚本（`start_backend.sh`）
5. ✅ 提供测试脚本（`test_api.sh`）

### 下一步行动

1. **启动服务**：执行 `./start_backend.sh`
2. **执行测试**：执行 `./test_api.sh`
3. **检查结果**：查看测试输出，确认所有接口正常
4. **前端适配**：根据新的 API 响应格式更新前端代码
5. **联调测试**：前后端联调，确保数据流转正常

### 注意事项

- 所有接口返回格式统一为 `ApiResponse<T>`
- 认证接口使用 `Bearer ${token}` 格式
- 用户信息接口返回字段已更新（全部为字典）
- 如遇问题，优先检查 `/tmp/backend.log` 日志文件

---

**文档版本**: 1.0
**最后更新**: 2024-02-14
**维护者**: 起了吗 App 开发团队
