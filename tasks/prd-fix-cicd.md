# CI/CD 修复 PRD

## 项目信息
- **项目名称**: GitHub CI/CD 修复
- **分支名**: `fix/cicd-pipelines`
- **复杂度**: 中等

---

## 背景与问题

当前 GitHub Actions CI/CD 管道存在多个问题，包括使用已弃用的 action 版本、缺少并发控制、pre-commit 重复运行等问题。本 PRD 定义修复这些问题的任务。

---

## 用户故事

### 故事 1: 修复 ci.yml
**作为** 开发者
**我希望** ci.yml 使用最优配置
**以便** 提高 CI 效率并减少运行时间

**验收标准**:
- [ ] pre-commit 只在单个 Python 版本中运行（避免矩阵重复）
- [ ] 前端缓存配置正确检查 pnpm-lock.yaml
- [ ] 添加并发控制配置
- [ ] 添加超时设置

**预估时间**: 20 分钟

---

### 故事 2: 修复 test.yml
**作为** 开发者
**我希望** test.yml 使用最新版本的 actions
**以便** 避免使用已弃用的功能

**验收标准**:
- [ ] 升级 actions/cache@v3 → v4
- [ ] 升级 codecov/codecov-action@v3 → v4
- [ ] 升级 actions/upload-artifact@v3 → v4
- [ ] 添加并发控制配置
- [ ] 添加超时设置
- [ ] 修复 mypy 类型检查配置

**预估时间**: 15 分钟

---

### 故事 3: 修复 build.yml
**作为** 开发者
**我希望** build.yml 使用最新版本的 actions
**以便** 确保安全扫描和镜像构建正常工作

**验收标准**:
- [ ] 升级 github/codeql-action/upload-sarif@v2 → v3
- [ ] 完善 Trivy 扫描配置（severity 过滤、exit-code）
- [ ] 添加并发控制配置
- [ ] 添加超时设置

**预估时间**: 15 分钟

---

### 故事 4: 修复 deploy.yml
**作为** 开发者
**我希望** deploy.yml 有可靠的部署配置
**以便** 部署流程可以正常工作

**验收标准**:
- [ ] 修复 Slack 通知条件（检查 secret 是否存在）
- [ ] 添加部署步骤的占位符注释
- [ ] 添加并发控制配置（防止部署冲突）
- [ ] 添加超时设置
- [ ] 添加环境保护规则检查

**预估时间**: 15 分钟

---

### 故事 5: 添加新 workflow（可选增强）
**作为** 开发者
**我希望** 有 PR 标题检查和依赖更新 workflow
**以便** 保持代码质量和依赖最新

**验收标准**:
- [ ] 创建 pr-title-check.yml 验证 PR 标题格式
- [ ] 创建 dependency-review.yml 检查依赖安全性

**预估时间**: 20 分钟

---

## 非目标
- 不修改实际部署逻辑（仅添加注释和占位符）
- 不修改测试用例
- 不修改业务代码

---

## 技术考虑

### Action 版本升级映射
| 旧版本 | 新版本 | 文件 |
|--------|--------|------|
| actions/cache@v3 | actions/cache@v4 | test.yml |
| codecov/codecov-action@v3 | codecov/codecov-action@v4 | test.yml |
| actions/upload-artifact@v3 | actions/upload-artifact@v4 | test.yml |
| github/codeql-action/upload-sarif@v2 | github/codeql-action/upload-sarif@v3 | build.yml |

### 并发控制配置
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 超时设置
```yaml
jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

---

## 成功指标
- 所有 workflow 使用最新版本 actions
- 无弃用警告
- CI 运行时间优化（pre-commit 不重复运行）
- 并发控制防止资源竞争

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Action 版本不兼容 | HIGH | 在分支上测试所有 workflow |
| 缓存失效问题 | MEDIUM | 保留 cache restore-keys 配置 |
| 部署流程中断 | HIGH | 仅修改配置，不修改部署逻辑 |

---

## 附录

### 参考资料
- [GitHub Actions 版本发布说明](https://github.com/actions/cache/releases)
- [Codecov Action 迁移指南](https://github.com/codecov/codecov-action)
- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides)
