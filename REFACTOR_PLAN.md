# 🚀 Superpowers 重构计划

> 使用 Superpowers 框架（TDD + 复杂度自适应 + 对抗性审查）进行项目重构

---

## 📊 项目概况

| 指标 | 数值 |
|------|------|
| Python 文件数 | 107 |
| 总代码行数 | ~30,629 |
| 模型数量 | 20+ |
| 服务数量 | 15+ |
| API 路由数 | 15+ |

**综合复杂度**: 🔴 **复杂** (10+ 功能点，多技术栈)

---

## 🎯 重构目标

1. **模型层**: SQLAlchemy 1.x → 2.x (`Column()` → `mapped_column()`)
2. **服务层**: 统一使用 `BaseService` + `CacheMixin` + `QueryBuilder`
3. **API 层**: `Depends()` → `Annotated[..., Depends()]`
4. **测试**: 覆盖率 >80%

---

## 📋 任务总览

| 批次 | 内容 | 预估时间 | 优先级 |
|------|------|----------|--------|
| 批次 1 | 核心模型重构 (9个子任务) | 90分钟 | P0 |
| 批次 2 | 服务层更新 (2个子任务) | 20分钟 | P0 |
| 批次 3 | API 层更新 (6个子任务) | 30分钟 | P1 |
| 批次 4 | 测试创建 (3个子任务) | 30分钟 | P0 |
| 批次 5 | 验证和回归 (2个子任务) | 15分钟 | P0 |
| **总计** | | **~3小时** | |

---

## 📁 文档结构

```
tasks/
├── prd-refactor-project.md      # PRD 文档
├── refactor-batch-1-models.md   # 批次 1: 模型重构
├── refactor-batch-2-services.md # 批次 2: 服务更新
├── refactor-batch-3-api.md      # 批次 3: API 更新
├── refactor-batch-4-tests.md    # 批次 4: 测试创建
└── refactor-batch-5-verify.md   # 批次 5: 验证回归

prd-refactor.json                 # 任务追踪 JSON
REFACTOR_PLAN.md                  # 本计划文档
```

---

## 🔄 工作流程

### 阶段 1: 创建分支
```bash
git checkout -b refactor/sqlalchemy2-modernization
```

### 阶段 2: 分批次执行
每个批次遵循 TDD 循环：
1. **RED**: 编写/运行测试（确认失败）
2. **GREEN**: 实现代码（使测试通过）
3. **REFACTOR**: 优化代码（保持测试通过）
4. **提交**: 小步提交

### 阶段 3: 对抗性审查
每个批次完成后：
1. 对照计划检查
2. 强制发现问题
3. 修复问题

### 阶段 4: 合并
所有批次完成后：
```bash
git checkout main
git merge refactor/sqlalchemy2-modernization
```

---

## ✅ 成功标准

| 标准 | 目标 | 验证方式 |
|------|------|----------|
| 模块导入 | 100% | `python -c "from app.models.user import User"` |
| 测试通过率 | 100% | `pytest tests/` |
| 代码覆盖率 | >80% | `pytest --cov=app` |
| 弃用警告 | 0 | 运行测试时无警告 |
| 数据库兼容 | 保持 | 现有迁移文件不变 |

---

## ⚠️ 风险控制

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 模型关系错误 | 中 | 高 | 逐个模型测试后再继续 |
| 循环导入 | 中 | 中 | 使用延迟导入简化依赖 |
| 测试失败 | 低 | 中 | 保留原始文件备份 |
| 性能退化 | 低 | 低 | 基准测试对比 |

---

## 📝 实施检查清单

### 准备阶段
- [ ] 创建分支 `refactor/sqlalchemy2-modernization`
- [ ] 通知团队成员
- [ ] 备份数据库

### 执行阶段
- [ ] 批次 1: 模型重构 (90分钟)
- [ ] 批次 2: 服务更新 (20分钟)
- [ ] 批次 3: API 更新 (30分钟)
- [ ] 批次 4: 测试创建 (30分钟)
- [ ] 批次 5: 验证回归 (15分钟)

### 收尾阶段
- [ ] 运行完整测试套件
- [ ] 代码格式化 (black, isort)
- [ ] 更新文档
- [ ] 合并到 main

---

## 🎓 Superpowers 框架应用

### 复杂度自适应
- **级别**: 复杂 (10+ 功能点，多技术栈)
- **任务粒度**: 1-3分钟/任务
- **规划深度**: 完整 PRD + 详细任务清单

### TDD 循环
每个任务严格遵循：
```
RED → GREEN → REFACTOR → COMMIT
```

### 对抗性审查
每个批次后强制审查：
- 必须找到至少 1 个问题
- 不允许"看起来不错"
- P0/P1 问题必须修复

### 知识积累
每次迭代更新：
- `progress.txt` - 进度记录
- `AGENTS.md` - 知识库
- Git commit message

---

## 🚀 开始重构

执行以下命令开始：

```bash
# 1. 创建分支
git checkout -b refactor/sqlalchemy2-modernization

# 2. 查看详细任务
cat tasks/refactor-batch-1-models.md

# 3. 开始第一个任务
# ... 按照 TDD 循环执行 ...
```

---

**准备好了吗？让我们开始重构！** 💪
