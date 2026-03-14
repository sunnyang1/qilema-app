# 项目清理和整理计划

## 当前问题分析

### 1. 文档混乱 (24个根目录 Markdown 文件)
**问题**: 大量重复的 CI/CD 和部署相关文档

| 类型 | 文件数量 | 问题 |
|------|----------|------|
| CI/CD 文档 | 6个 | 内容重复，分散注意力 |
| 部署文档 | 8个 | 重复、过时、难以维护 |
| README | 6个 | 重复、不一致 |
| 其他 | 4个 | 分散在不同位置 |

### 2. Workflow 文件过多 (17个)
**问题**: 大量重复、已弃用的 workflow

### 3. Docker Compose 文件过多 (6个)
**问题**: 功能重叠，使用方式混乱

### 4. 不应该在版本控制的文件
- `venv/` (67MB) - Python 虚拟环境
- `container-structure-test-linux-amd64` (15MB) - 二进制工具
- `*.log` 文件 - 日志文件
- `__pycache__/` 目录 - Python 缓存
- `.pytest_cache/` 目录 - 测试缓存

### 5. 目录结构不清晰
- 文档分散在根目录
- 脚本位置不统一
- 配置文件混乱

---

## 清理计划

### Phase 1: 删除不应该版本控制的文件

1. **删除缓存目录**
   - [ ] 删除所有 `__pycache__/` 目录
   - [ ] 删除所有 `.pytest_cache/` 目录

2. **删除日志文件**
   - [ ] `deploy.log`
   - [ ] `deploy-full.log`
   - [ ] `docker-install.log`
   - [ ] `build.log`
   - [ ] `backend/logs/*.log`

3. **删除二进制工具**
   - [ ] `container-structure-test-linux-amd64`

4. **更新 .gitignore**
   - [ ] 添加更多忽略规则

### Phase 2: 整合文档

1. **创建 docs/ 目录结构**
   ```
   docs/
   ├── README.md                 # 文档索引
   ├── deployment/               # 部署相关
   │   ├── README.md
   │   ├── guide.md
   │   └── server-setup.md
   ├── cicd/                     # CI/CD 相关
   │   ├── README.md
   │   └── workflow-guide.md
   ├── development/              # 开发相关
   │   ├── README.md
   │   └── setup.md
   └── architecture/             # 架构文档
       └── README.md
   ```

2. **整合根目录 Markdown**
   - [ ] 将所有 CI/CD 文档整合到 `docs/cicd/`
   - [ ] 将所有部署文档整合到 `docs/deployment/`
   - [ ] 保留根目录只有 `README.md` 和 `AGENTS.md`

### Phase 3: 整理 Workflow

已完成大部分整合，需要:
- [ ] 删除已弃用的 workflow 文件（保留3个月）
- [ ] 确保 4 个核心 workflow 正常工作

### Phase 4: 整理 Docker Compose

已完成整合，需要:
- [ ] 删除已弃用的 compose 文件（保留3个月）
- [ ] 确保 3 个核心 compose 文件正常工作

### Phase 5: 统一脚本位置

1. **整理 scripts/ 目录**
   ```
   scripts/
   ├── deploy/
   │   ├── local.sh          # (原 deploy-local.sh)
   │   └── docker-install.sh # (原 install-docker.sh)
   ├── maintenance/
   │   └── stop-local.sh
   └── README.md
   ```

---

## 目录结构目标

```
qilema-app/
├── README.md                 # 项目主文档
├── AGENTS.md                 # AI Agent 知识库
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml        # Docker Compose 基础
├── docker-compose.dev.yml    # 开发环境
├── docker-compose.prod.yml   # 生产环境
├── package.json
├── pnpm-lock.yaml
│
├── .github/
│   └── workflows/            # 4个核心 workflow
│       ├── ci.yml
│       ├── build.yml
│       ├── deploy.yml
│       └── pr-checks.yml
│
├── backend/                  # 后端代码
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── app/
│   ├── tests/
│   ├── migrations/
│   └── docs/                 # 后端特定文档
│
├── mobile/                   # 移动端代码
│   ├── README.md
│   ├── client/
│   └── server/
│
├── nginx/                    # Nginx 配置
│   ├── Dockerfile
│   ├── nginx.conf
│   └── conf.d/
│
├── scripts/                  # 运维脚本
│   ├── deploy/
│   ├── maintenance/
│   └── README.md
│
├── docs/                     # 项目文档
│   ├── README.md
│   ├── deployment/
│   ├── cicd/
│   ├── development/
│   └── architecture/
│
├── k8s/                      # Kubernetes 配置
│   └── README.md
│
├── tasks/                    # 任务/计划文档
│   └── *.md
│
└── tests/                    # 集成测试
    └── README.md
```

---

## 清理后统计

| 项目 | 当前 | 目标 | 减少 |
|------|------|------|------|
| 根目录 Markdown | 24 | 2 | 92% |
| Workflow 文件 | 17 | 4 | 76% |
| Docker Compose | 6 | 3 | 50% |
| 根目录脚本 | 3 | 0 (移动到 scripts/) | 100% |
| 不应该在版本控制 | 5+ | 0 | 100% |

---

## 执行顺序

1. 清理缓存和日志文件
2. 整理文档到 docs/
3. 整理脚本到 scripts/
4. 更新配置文件
5. 验证清理结果
