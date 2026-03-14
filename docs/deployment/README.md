# 部署文档

## 快速导航

| 文档 | 说明 |
|------|------|
| [快速开始](quick-start.md) | 5分钟部署指南 |
| [完整指南](guide.md) | 详细部署流程 |
| [服务器设置](server-setup.md) | 服务器环境准备 |
| [Secrets 配置](secrets-setup.md) | 密钥和敏感信息配置 |

## 部署环境

- **Staging**: `https://staging.api.qilema.com`
- **Production**: `https://api.qilema.com`

## 部署方式

### 1. Docker Compose 部署 (推荐)

```bash
# 生产环境
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. CI/CD 自动部署

代码推送到 `main` 分支自动部署到 Staging，打 tag `v*` 自动部署到 Production。

### 3. 手动部署

```bash
# 使用部署脚本
./scripts/deploy/local.sh
```

## 部署检查清单

- [ ] 服务器环境已配置
- [ ] Secrets 已设置
- [ ] 数据库已备份
- [ ] 域名和 SSL 已配置
- [ ] 健康检查通过

## 回滚

如果部署失败，系统会自动回滚到上一个版本。

手动回滚:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

*更多细节请查看各子文档*
