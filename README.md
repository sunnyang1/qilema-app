# 起了吗 App

一个面向独居人群的紧急医疗服务应用，提供签到监测、智能预警、SOS求助、健康档案管理等功能，为用户提供全方位的安全保障和快速救援通道。

---

## 项目简介

"起了吗"App基于"死了么"的产品逻辑，将核心价值从"身后关怀"重构为"生命救援"。通过整合每日签到监测、智能设备联动、SOS紧急求助、急救资源对接等功能，为用户提供全方位的安全保障和快速救援通道，实现从"被动通知"到"主动救援"的质变。

### 核心价值

- **从被动到主动**：相比传统的事后通知，"起了吗"强调实时救援和多方联动
- **从单一到全面**：不仅提供签到监测，还整合了健康档案、智能设备、急救资源
- **从工具到服务**：不是简单的签到工具，而是完整的紧急医疗服务平台

### 目标用户

| 用户角色 | 描述 | 主要需求 |
|---------|------|---------|
| 独居青年（20-40岁） | 在一二线城市独自打拼的年轻人 | 快速急救、有人关注、低成本、易操作 |
| 独居老人（65岁以上） | 子女不在身边的空巢老人 | 简单易用、可靠通知、子女安心 |
| 异地子女 | 在外地工作的子女 | 远程了解父母状态、及时接收预警 |
| 高危职业人群 | 夜班工作者、高空作业等 | 安全监测、快速求助、实时定位 |
| 慢性病患者 | 患有心脑血管疾病等需要长期监测的用户 | 健康档案、用药提醒、异常预警 |

---

## 功能特性

### 核心功能

- ✅ **每日签到打卡**：用户每天早上完成签到，让紧急联系人知道你的安全状态
- ✅ **异常预警机制**：连续未签到或生理数据异常时自动预警
- ✅ **SOS紧急求助**：一键发送求助信号，快速通知联系人和急救中心
- ✅ **紧急联系人管理**：添加多个联系人，设置通知优先级和渠道
- ✅ **健康档案管理**：记录病史、用药、过敏史，紧急情况下快速分享
- ✅ **智能设备联动**：绑定手环/手表，实时监测生理数据
- ✅ **急救资源对接**：周边急救资源地图，一键拨打120
- ✅ **多渠道通知**：APP推送、短信、电话等多种通知方式

### 使用场景

#### 场景1：独居青年突发急性疾病
智能手环检测到心率异常 → 自动触发预警 → 通知紧急联系人 → 对接120急救中心 → 联系人收到位置和健康信息前往救援

#### 场景2：老人日常安全监测
老人每天点击"早安"签到 → 子女收到平安通知 → 若48小时未签到 → 系统自动预警通知子女

#### 场景3：夜间紧急求助
长按SOS按钮3秒 → 系统获取GPS位置 → 向联系人发送求助通知（含位置和地图） → 一键拨打120 → 联系人通过导航快速到达

#### 场景4：慢性病患者健康监测
智能设备监测到血压/心率异常 → 系统分析并预警 → 自动发送健康档案摘要给联系人和急救中心 → 帮助急救人员快速制定救治方案

---

## 技术架构

### 技术栈

#### 前端
- **框架**：Flutter 3.16+
- **语言**：Dart 3.2+
- **UI组件**：Material Design / Cupertino
- **状态管理**：Riverpod / Provider
- **导航**：GoRouter / AutoRoute
- **网络请求**：Dio

#### 后端
- **框架**：Python 3.11+ + FastAPI 0.104+
- **异步处理**：asyncio / Celery
- **认证授权**：JWT + OAuth2.0
- **数据验证**：Pydantic
- **API文档**：自动生成OpenAPI/Swagger

#### 数据库
- **关系型数据库**：PostgreSQL 15+
- **缓存**：Redis 7+
- **ORM**：SQLAlchemy / Tortoise ORM

#### 基础设施
- **容器化**：Docker + Docker Compose
- **CI/CD**：GitHub Actions
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack

### 系统架构

```
┌─────────────────────────────────────────┐
│           客户端层                        │
│  ┌──────────┐  ┌──────────┐             │
│  │ iOS App  │  │ Android  │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
                    ↓ HTTPS
┌─────────────────────────────────────────┐
│           API网关层                       │
│  ┌─────────────────────────────────┐  │
│  │  Nginx / Kong API Gateway        │  │
│  │  - 路由转发                       │  │
│  │  - 负载均衡                       │  │
│  │  - 限流熔断                       │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           应用服务层                      │
│  ┌──────────┐  ┌──────────┐             │
│  │ 用户服务  │  │ 签到服务  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ 预警服务  │  │ SOS服务  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ 通知服务  │  │ 设备服务  │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           数据层                          │
│  ┌──────────┐  ┌──────────┐             │
│  │PostgreSQL│  │  Redis   │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ 阿里云OSS │  │ 消息队列  │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           第三方服务                      │
│  ┌──────────┐  ┌──────────┐             │
│  │ 短信服务  │  │ 推送服务  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ 地图服务  │  │ 120接口  │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
```

---

## 快速开始

### 环境要求

- **Flutter SDK**：3.16.0+
- **Dart SDK**：3.2.0+
- **Python**：3.11+
- **PostgreSQL**：15+
- **Redis**：7+
- **Docker**：20.10+ (可选)

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/qilema-app.git
cd qilema-app
```

#### 2. 安装前端依赖

```bash
cd frontend
flutter pub get
```

#### 3. 安装后端依赖

```bash
cd ../backend
pip install -r requirements.txt
```

#### 4. 配置环境变量

复制环境变量模板并填写实际值：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/qilema
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# 第三方服务
ALIYUN_ACCESS_KEY=your-access-key
ALIYUN_ACCESS_SECRET=your-access-secret
ALIYUN_SMS_SIGN_NAME=起了吗
ALIYUN_SMS_TEMPLATE_CODE=SMS_123456789

# 地图服务
AMAP_API_KEY=your-amap-api-key

# 120接口（需要官方对接）
EMERGENCY_SERVICE_API_URL=https://api.emergency.example.com
```

#### 5. 初始化数据库

```bash
cd backend
python init_db.py
```

#### 6. 启动Redis

```bash
# 使用Docker启动Redis
docker-compose up -d redis

# 或使用系统包管理器安装Redis
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis
```

#### 7. 启动后端服务

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 8. 启动前端应用

```bash
cd frontend

# iOS
flutter run -d ios

# Android
flutter run -d android

# 或使用Chrome浏览器调试
flutter run -d chrome
```

#### 9. 使用Docker启动（推荐）

```bash
# 启动所有服务（前端、后端、数据库、Redis）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 项目结构

```
qilema-app/
├── frontend/                  # Flutter前端应用
│   ├── lib/
│   │   ├── main.dart         # 应用入口
│   │   ├── core/             # 核心模块
│   │   ├── features/         # 功能模块
│   │   │   ├── auth/         # 认证模块
│   │   │   ├── signin/       # 签到模块
│   │   │   ├── sos/          # SOS模块
│   │   │   ├── contacts/     # 联系人模块
│   │   │   ├── health/       # 健康档案模块
│   │   │   └── devices/      # 设备模块
│   │   ├── shared/           # 共享组件
│   │   └── l10n/             # 国际化
│   ├── pubspec.yaml          # 依赖配置
│   └── assets/               # 静态资源
│
├── backend/                   # Python后端服务
│   ├── app/
│   │   ├── main.py           # FastAPI应用入口
│   │   ├── api/              # API路由
│   │   │   ├── v1/
│   │   │   │   ├── auth.py   # 认证API
│   │   │   │   ├── users.py  # 用户API
│   │   │   │   ├── signin.py # 签到API
│   │   │   │   ├── sos.py    # SOS API
│   │   │   │   ├── contacts.py # 联系人API
│   │   │   │   └── health.py # 健康档案API
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── services/         # 业务逻辑
│   │   │   ├── auth_service.py
│   │   │   ├── notification_service.py
│   │   │   └── alert_service.py
│   │   ├── tasks/            # Celery任务
│   │   └── utils/            # 工具函数
│   ├── tests/                # 测试
│   ├── requirements.txt       # Python依赖
│   └── Dockerfile            # Docker镜像
│
├── docs/                     # 文档
│   ├── prd.md                # 产品需求文档
│   ├── api.md                # API文档
│   └── deployment.md         # 部署文档
│
├── docker-compose.yml        # Docker编排配置
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

---

## API文档

项目使用FastAPI自动生成OpenAPI文档，启动后端服务后可通过以下地址访问：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### 主要API端点

#### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token

#### 签到相关
- `POST /api/v1/signin` - 每日签到
- `GET /api/v1/signin/history` - 签到历史
- `GET /api/v1/signin/status` - 签到状态

#### SOS相关
- `POST /api/v1/sos` - 触发SOS
- `GET /api/v1/sos/{sos_id}` - 查询SOS状态
- `DELETE /api/v1/sos/{sos_id}` - 取消SOS

#### 联系人相关
- `GET /api/v1/contacts` - 获取联系人列表
- `POST /api/v1/contacts` - 添加联系人
- `PUT /api/v1/contacts/{contact_id}` - 更新联系人
- `DELETE /api/v1/contacts/{contact_id}` - 删除联系人

#### 健康档案相关
- `GET /api/v1/health-profile` - 获取健康档案
- `PUT /api/v1/health-profile` - 更新健康档案

详细API文档请参考 `docs/api.md`

---

## 开发指南

### 前端开发

#### 添加新功能模块

```bash
cd frontend/lib/features
flutter create --template=feature your_feature
```

#### 运行测试

```bash
cd frontend
flutter test
```

#### 构建发布版本

```bash
# iOS
flutter build ios --release

# Android
flutter build apk --release
```

### 后端开发

#### 添加新的API端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 定义Pydantic模型（`app/schemas/`）
3. 实现业务逻辑（`app/services/`）
4. 在 `app/api/v1/__init__.py` 中注册路由

#### 运行测试

```bash
cd backend
pytest
```

#### 代码格式化

```bash
cd backend
black .
isort .
flake8
```

---

## 部署指南

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 云服务器部署

详细的部署流程请参考 `docs/deployment.md`

主要步骤：
1. 准备云服务器（阿里云ECS/腾讯云CVM）
2. 安装Docker和Docker Compose
3. 配置环境变量
4. 部署数据库和Redis
5. 部署后端服务
6. 配置Nginx反向代理
7. 配置SSL证书（HTTPS）
8. 部署前端应用
9. 配置CI/CD自动部署

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- **Dart代码**：遵循Effective Dart指南
- **Python代码**：遵循PEP 8规范，使用black格式化
- **提交信息**：使用Conventional Commits格式

---

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

---

## 联系方式

- **项目主页**：https://github.com/your-org/qilema-app
- **问题反馈**：https://github.com/your-org/qilema-app/issues
- **邮箱**：contact@qilema.app

---

## 致谢

感谢所有为本项目做出贡献的开发者和用户！

特别感谢：
- Flutter团队提供优秀的跨平台框架
- FastAPI团队提供高性能的Web框架
- "死了么"App提供的产品灵感

---

## 路线图

### Phase 1：MVP版本（当前阶段）
- [x] 用户注册/登录
- [x] 每日签到打卡
- [x] 超时未签到预警
- [x] SOS紧急求助
- [x] 紧急联系人管理
- [x] 短信通知
- [ ] APP推送通知
- [ ] 健康档案管理

### Phase 2：增强版
- [ ] 智能设备绑定和数据同步
- [ ] 生理数据监测和异常预警
- [ ] 周边急救资源地图
- [ ] 一键拨打120
- [ ] 通知渠道扩展（邮件、电话）
- [ ] 签到提醒功能
- [ ] 用户设置和个性化配置

### Phase 3：完整版
- [ ] 与120急救中心对接
- [ ] 急救车实时位置追踪
- [ ] AED设备地图和导航
- [ ] 急救知识库和急救指南
- [ ] 健康数据趋势分析报告
- [ ] 用药提醒功能
- [ ] 社区网格员/物业联动
- [ ] 适老化版本

---

**让每个人都能安全地开始新的一天** 🌅
