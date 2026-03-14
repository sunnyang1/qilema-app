# 起了吗 App (Qilema App)

一个面向独居人群的紧急医疗服务平台，提供签到监测、异常预警、紧急求助、资源对接等核心功能。

## 核心功能

- **每日签到打卡** - 用户通过每日签到确认安全状态
- **异常预警机制** - 超时未签到自动触发预警
- **SOS紧急求助** - 一键发送求助信号，自动获取位置
- **紧急联系人管理** - 添加、管理紧急联系人
- **健康档案管理** - 记录病史、用药、过敏史
- **急救资源对接** - 显示周边医院、AED设备位置

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 + FastAPI + SQLAlchemy |
| 前端 | React Native + Expo |
| 数据库 | PostgreSQL + Redis |
| 部署 | Docker + GitHub Actions |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourorg/qilema-app.git
cd qilema-app

# 启动开发环境
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 访问 API 文档
open http://localhost:8000/docs
```

## 项目结构

```
qilema-app/
├── backend/          # Python FastAPI 后端
├── mobile/           # React Native 移动端
├── nginx/            # Nginx 反向代理
├── scripts/          # 运维脚本
├── docs/             # 项目文档
└── k8s/              # Kubernetes 配置
```

## 文档

| 文档 | 说明 |
|------|------|
| [📖 开发指南](docs/development/) | 本地开发设置 |
| [🚀 部署指南](docs/deployment/) | 服务器部署流程 |
| [⚙️ CI/CD](docs/cicd/) | GitHub Actions 工作流 |
| [🏗️ 架构设计](docs/architecture/) | 系统架构 |
| [🤖 AGENTS.md](AGENTS.md) | AI Agent 知识库 |

## 开发

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 移动端

```bash
cd mobile
pnpm install
cd client
pnpm dev
```

## 测试

```bash
# 后端测试
cd backend
pytest

# 代码检查
pre-commit run --all-files
```

## 部署

### Staging (自动)

推送到 `main` 分支自动部署到 Staging

### Production (手动)

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

详细部署文档: [docs/deployment/](docs/deployment/)

## 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: Add feature'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**设计风格**: 温暖守护（晨光橙 #FF8A65 + 生命绿 #66BB6A）

**当前版本**: v1.0.0

**最后更新**: 2026-03-14
