# CI/CD 流程整合与清理 - PRD

## 背景与问题分析

### 当前问题

1. **Docker Compose 文件过多** (6个)
   - `docker-compose.yml` - 基础配置
   - `docker-compose.override.yml` - 开发覆盖
   - `docker-compose.dev.yml` - 开发详细配置 (与 override 重复)
   - `docker-compose.prod.yml` - 生产环境
   - `docker-compose.staging.yml` - 测试环境 (接近生产)
   - `docker-compose.test.yml` - 测试环境 (简单版本)

   **问题**: override 和 dev 功能重叠，staging 和 test 也可以合并

2. **GitHub Actions Workflow 文件过多** (15个)
   - `ci.yml` - 主 CI (测试、lint)
   - `build.yml` - 构建镜像
   - `build-consolidated.yml` - 构建 (重复)
   - `build-scan-consolidated.yml` - 扫描 (重复)
   - `deploy.yml` - 部署
   - `deploy-consolidated.yml` - 部署 (更完整)
   - `deploy-docker.yml` - 部署 (重复)
   - `deploy-new.yml` - 部署 (重复)
   - `deploy-production.yml` - 生产部署
   - `deploy-staging.yml` - 测试部署
   - `test.yml` - 测试 (重复)
   - `test-consolidated.yml` - 测试 (重复)
   - `test-lint-consolidated.yml` - lint (重复)
   - `dependency-review.yml` - 依赖审查
   - `pr-title-check.yml` - PR标题检查

### 目标

**简化后结构**:

| 当前 | 目标 | 说明 |
|------|------|------|
| 6个 docker-compose | 3个 | base + dev + prod |
| 15个 workflow | 4个 | ci.yml + build.yml + deploy.yml + pr-checks.yml |

## 设计

### Docker Compose 整合

```
docker-compose.yml          # 基础服务定义 (postgres, redis, backend, nginx)
docker-compose.dev.yml      # 开发环境覆盖 (热重载、调试、宽松限制)
docker-compose.prod.yml     # 生产环境覆盖 (资源限制、安全、持久化)
```

**使用方式**:
- 开发: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`
- 生产: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`

### Workflow 整合

```
.github/workflows/
├── ci.yml          # 代码检查、测试、lint (PR + Push)
├── build.yml       # 构建镜像、安全扫描 (Push 到 main, tag)
├── deploy.yml      # 部署到 staging/production (Push 到 main, tag)
└── pr-checks.yml   # PR 标题检查、依赖审查 (PR)
```

## 非目标

- 不改变任何应用代码
- 不改变 Dockerfile
- 不改变部署逻辑，只整合工作流
- 不改变环境变量配置

## 技术考虑

1. **向后兼容**: 保留旧文件一段时间，添加 deprecation 注释
2. **并发控制**: 每个 workflow 必须有 concurrency 配置
3. **超时设置**: 每个 job 必须有 timeout-minutes
4. **Action 版本**: 使用稳定版本 (v4/v5)

## 成功指标

- [ ] Docker Compose 文件从 6 个减少到 3 个
- [ ] Workflow 文件从 15 个减少到 4 个
- [ ] 所有 workflow 语法验证通过
- [ ] 所有 compose 配置验证通过
- [ ] 文档更新
