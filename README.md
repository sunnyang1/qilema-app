# 起了吗 App (Qilema App)

一个面向独居人群的紧急医疗服务平台，提供签到监测、异常预警、紧急求助、资源对接等核心功能。

## 项目概述

"起了吗"App基于"死了么"的产品逻辑，将核心价值从"身后关怀"重构为"生命救援"，为独居人群构建一个可靠的紧急医疗救助通道。

### 核心功能

- **每日签到打卡** - 用户通过每日签到确认安全状态
- **异常预警机制** - 超时未签到自动触发预警，通知紧急联系人
- **SOS紧急求助** - 一键长按发送求助信号，自动获取位置信息
- **紧急联系人管理** - 添加、编辑、删除紧急联系人，设置通知优先级
- **健康档案管理** - 记录病史、用药情况、过敏史等健康信息
- **智能设备联动** - 绑定智能手环/手表，实时监测生理数据
- **急救资源对接** - 显示周边120急救中心、医院、AED设备位置

### 目标用户

- 独居青年（20-40岁）
- 独居老人（65岁以上）
- 异地子女
- 高危职业人群
- 慢性病患者

## 项目结构

```
qilema-app/
├── backend/              # Python FastAPI 后端
│   ├── app/             # 应用核心代码
│   ├── tests/           # 测试代码
│   ├── scripts/         # 脚本工具
│   └── main.py          # 应用入口
├── mobile/              # Expo + React Native 前端
│   ├── client/          # React Native 应用代码
│   └── .coze/           # Coze 配置
├── docs/                # 项目文档
│   ├── prd.md          # 产品需求文档
│   ├── api.md          # API 文档
│   └── deployment.md   # 部署文档
└── README.md            # 本文件
```

## 技术栈

### 后端
- **语言**: Python 3.12.3
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite (开发/测试), PostgreSQL (生产)
- **缓存**: Redis
- **认证**: JWT + OAuth2.0
- **监控**: Prometheus
- **测试**: pytest + pytest-cov

### 前端
- **框架**: Expo 54 + React Native 0.81.5
- **语言**: TypeScript
- **路由**: Expo Router 6.0
- **状态管理**: React Context
- **UI组件**: React Native + Expo 模块
- **包管理**: pnpm workspace

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 20+
- pnpm 8+
- Expo CLI

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 前端启动

```bash
# 进入移动端目录
cd mobile

# 安装依赖
pnpm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
coze dev
# 或
cd client && npx expo start
```

前端服务将在 `http://localhost:19006` (Web) 或 Expo Go (Mobile) 启动

## API 文档

后端启动后，访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 测试

### 后端测试

```bash
cd backend
pytest tests/ -v --cov=app
```

### 前端测试

```bash
cd mobile/client
npx expo install --fix
npx jest
```

## 部署

详细部署文档请参考：[deployment.md](docs/deployment.md)

## 文档

- [产品需求文档](docs/prd.md)
- [API 文档](docs/api.md)
- [部署文档](docs/deployment.md)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- GitHub: https://github.com/sunnyang1/qilema-app
- 问题反馈: https://github.com/sunnyang1/qilema-app/issues

---

**设计风格**: 温暖守护（晨光橙 #FF8A65 + 生命绿 #66BB6A）

**当前版本**: v1.0.0

**最后更新**: 2024-02-24
