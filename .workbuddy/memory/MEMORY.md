# MEMORY.md — 项目长期记忆

## 项目基本信息

- **项目名**：起了吗 App（qilema-app）
- **定位**：独居人群紧急医疗救助平台
- **后端技术**：Python 3.12 + FastAPI + SQLAlchemy 2.x + PostgreSQL + Redis
- **移动端**：React Native 0.81.5 + Expo 54 + TypeScript
- **仓库**：https://github.com/sunnyang1/qilema-app.git

## 用户偏好

- 使用中文沟通，风格简洁高效
- 倾向于简短命令驱动任务（如"上传 github"，"继续完成"）
- 期望直接交付可用方案，减少询问
- 项目 node 环境：node 25.2.1 at /opt/homebrew/Cellar/node/25.2.1/bin/node，pnpm 9.0.0 at /opt/homebrew/bin/pnpm

## 架构重构决策记录（2026-04-23）

### 已识别核心问题
- SOS 通知走同步调用链，超时即失败（P0）
- 所有服务集中单进程，无法对高频模块单独扩容（P0）
- 生产环境允许 SQLite（P0）
- 缓存命中后仍回查数据库，"假命中"（P1）
- 路由全部同步函数（`def`），阻塞 event loop（P1）

### 已输出方案
- 架构方案文档：`docs/ARCHITECTURE_REDESIGN.md`
- 核心改进：Redis Streams 消息队列 + Worker 进程 + 异步路由 + Repository 模式 + 读写分离
- 迁移路线：5 个 Phase，10 周渐进式迁移，不停服
