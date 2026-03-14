# CI/CD 文档

## 概述

项目使用 GitHub Actions 进行持续集成和部署。

## Workflow 文件

| 文件 | 用途 | 触发条件 |
|------|------|----------|
| [ci.yml](../../.github/workflows/ci.yml) | 代码检查、测试、lint | PR, push to main/develop |
| [build.yml](../../.github/workflows/build.yml) | 构建镜像、安全扫描 | PR, push to main, tag v* |
| [deploy.yml](../../.github/workflows/deploy.yml) | 部署到 staging/production | push to main, tag v*, manual |
| [pr-checks.yml](../../.github/workflows/pr-checks.yml) | PR 标题检查、依赖审查 | PR opened/edited |

## 快速开始

### 查看工作流状态

访问: `https://github.com/yourorg/qilema-app/actions`

### 本地验证 Workflow

```bash
# 验证 YAML 语法
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# 使用 act 本地运行 (需要安装 act)
act -j pre-commit
```

## 部署流程

```
代码提交 → PR 创建 → CI 测试 → 合并 → Staging 部署 → Tag 创建 → Production 部署
```

## 配置 Secrets

需要在 GitHub Settings → Secrets and variables → Actions 中配置:

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_PASSWORD`
- `DEPLOY_KEY`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `SLACK_WEBHOOK` (可选)

## 更多信息

- [部署文档](../deployment/)
- [GitHub Actions 文档](https://docs.github.com/actions)
