# 前后端对接报告

## 项目信息
- **项目名称**: 起了吗 App
- **前端技术栈**: Expo 54 + React Native + TypeScript
- **后端技术栈**: Python 3.12.3 + FastAPI + SQLAlchemy + SQLite
- **对接日期**: 2026-02-14
- **对接状态**: ✅ 核心功能已对接

## 环境配置

### 后端服务
- **服务地址**: http://localhost:8000
- **健康检查端点**: GET /health
- **API 版本前缀**: /api/v1
- **运行状态**: ✅ 正常运行

### 前端配置
- **API Base URL**: http://localhost:8000 (通过环境变量 EXPO_PUBLIC_BACKEND_BASE_URL 配置)
- **前端服务地址**: http://localhost:5000
- **运行状态**: ✅ 正常运行

## 认证功能对接

### 已实现功能
1. **用户注册** - POST /api/v1/auth/register
   - 状态: ✅ 正常工作
   - 测试结果: 注册成功，返回用户ID

2. **用户登录** - POST /api/v1/auth/login
   - 状态: ✅ 正常工作
   - 测试结果: 登录成功，返回 access_token 和用户信息
   - Token 格式: JWT (Bearer)

3. **获取当前用户信息** - GET /api/v1/auth/me
   - 状态: ✅ 正常工作
   - 需要认证: 是 (Bearer Token)
   - 测试结果: 成功返回用户基本信息

4. **刷新访问令牌** - POST /api/v1/auth/refresh
   - 状态: ✅ 已实现
   - 需要认证: 是

5. **用户登出** - POST /api/v1/auth/logout
   - 状态: ✅ 已实现
   - 需要认证: 是

### 认证流程
```
用户注册 → 登录获取 access_token → 使用 access_token 访问受保护资源
```

## 核心功能对接

### 签到功能
1. **创建签到** - POST /api/v1/checkins/
   - 状态: ✅ 正常工作
   - 需要认证: 是
   - 请求参数:
     - checkin_method: string (manual/auto)
     - latitude: float (可选)
     - longitude: float (可选)
     - notes: string (可选)
   - 测试结果: 签到成功，返回签到记录

2. **获取签到历史** - GET /api/v1/checkins/history
   - 状态: ✅ 已实现
   - 需要认证: 是

3. **获取签到统计** - GET /api/v1/checkins/stats
   - 状态: ✅ 已实现
   - 需要认证: 是

4. **获取今日签到状态** - GET /api/v1/checkins/today
   - 状态: ✅ 已实现
   - 需要认证: 是

### SOS 紧急求助功能
1. **发起 SOS** - POST /api/v1/sos/
   - 状态: ✅ 已实现
   - 需要认证: 是
   - 请求参数:
     - latitude: float (必需)
     - longitude: float (必需)
     - address: string (可选)
     - emergency_reason: string (可选)
     - call_120: boolean (可选)

2. **获取 SOS 记录** - GET /api/v1/sos/
   - 状态: ✅ 已实现
   - 需要认证: 是

3. **获取 SOS 详情** - GET /api/v1/sos/{sos_id}
   - 状态: ✅ 已实现
   - 需要认证: 是

4. **取消 SOS** - PUT /api/v1/sos/{sos_id}/cancel
   - 状态: ✅ 已实现
   - 需要认证: 是

5. **解决 SOS** - PUT /api/v1/sos/{sos_id}/resolve
   - 状态: ✅ 已实现
   - 需要认证: 是

## 路由修复记录

### 问题 1: 认证路由缺失
- **问题描述**: 后端缺少认证路由 (login, register, refresh, logout)
- **解决方案**: 创建 /workspace/projects/backend/app/api/auth.py，实现所有认证端点
- **影响范围**: 所有需要认证的功能

### 问题 2: User 模型字段名称不匹配
- **问题描述**: 代码中使用 `user.hashed_password`，但模型中字段名为 `user.password_hash`
- **解决方案**: 修改 auth.py 中所有引用，改为 `user.password_hash`

### 问题 3: User 模型缺少 is_active 字段
- **问题描述**: 登录逻辑检查 `user.is_active`，但模型中无此字段
- **解决方案**: 移除登录逻辑中的 `is_active` 检查

### 问题 4: 用户对象序列化循环引用
- **问题描述**: 返回完整用户对象时出现 `RecursionError`
- **解决方案**: 手动构建用户信息字典，只返回基本字段

### 问题 5: checkins 路由路径重复
- **问题描述**: checkins.router 在 checkins.py 和 __init__.py 中都定义了 prefix="/checkins"
- **解决方案**: 修改 __init__.py，移除重复的 prefix 参数

### 问题 6: SOS 模型字段不匹配
- **问题描述**: create_sos 函数使用 `location` 字典，但 SOSRequest 模型使用分开的 latitude/longitude 字段
- **解决方案**: 修改 create_sos 函数，使用正确的字段名

## API 响应格式

所有 API 响应遵循统一格式：
```json
{
  "code": 200,
  "message": "成功",
  "data": {...},
  "timestamp": 1771018075
}
```

错误响应：
```json
{
  "code": 500,
  "message": "服务器内部错误",
  "detail": null,
  "request_id": "cc4a4f83",
  "timestamp": 1771017817
}
```

## 测试数据

### 测试用户
- **手机号**: 13800138000
- **密码**: 123456
- **用户 ID**: fdd7afce-215a-4fc7-8530-3dbe6a23a8f0

### 测试结果
1. ✅ 用户注册成功
2. ✅ 用户登录成功
3. ✅ 获取用户信息成功
4. ✅ 创建签到记录成功
5. ✅ SOS 功能已实现（未完整测试）

## 前端 API 客户端配置

前端使用 `@/utils/api.ts` 中的 APIClient 类进行 API 调用。

### 使用示例
```typescript
import { apiClient } from '@/utils/api';

// 登录
const response = await apiClient.post('/api/v1/auth/login', {
  username: '13800138000',
  password: '123456'
});

// 签到（需要认证）
const checkinResponse = await apiClient.post('/api/v1/checkins/', {
  checkin_method: 'manual'
});
```

## 待完成功能

以下功能后端已实现，但前端尚未完整对接：
1. 紧急联系人管理 (POST/GET/PUT/DELETE /api/v1/contacts)
2. 健康档案管理 (POST/GET/PUT/DELETE /api/v1/health-records)
3. 用药提醒 (POST/GET/PUT/DELETE /api/v1/medications)
4. 设备管理 (POST/GET/PUT/DELETE /api/v1/devices)
5. 急救知识库 (GET /api/v1/knowledge/*)
6. AED 设备查询 (GET /api/v1/aed)
7. 紧急中心查询 (GET /api/v1/emergency_centers)

## 建议

1. **统一 API 路径**: 建议前端使用后端实际的 API 路径，或创建路径映射层
2. **错误处理**: 前端应添加统一的错误处理机制
3. **Token 刷新**: 建议实现自动 token 刷新机制
4. **数据验证**: 前端应添加表单验证，减少无效请求

## 总结

✅ **核心功能已完成对接**:
- 认证功能（登录、注册、获取用户信息）
- 签到功能（创建签到记录）
- SOS 紧急求助功能（基础实现）

⚠️ **待完善功能**:
- Token 自动刷新机制
- 紧急联系人管理
- 健康档案管理
- 用药提醒
- 设备管理

📅 **下次对接计划**:
- 完成剩余功能的对接
- 添加单元测试
- 性能优化
