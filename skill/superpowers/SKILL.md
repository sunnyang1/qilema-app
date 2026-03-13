---
name: superpowers
description: 强制用于任何软件开发任务，融合Superpowers框架（TDD、设计细化、任务分解）、Ralph自主迭代循环（PRD驱动、进度持久化、知识积累）及BMad最佳实践（对抗性审查、高级启发、复杂度自适应），适用于从零构建、功能开发、重构等场景
---

# Superpowers - 自主软件开发工作流

<EXTREMELY-IMPORTANT>
**强制使用**：只要有1%的可能性适用于任务，必须在提供任何响应或提问之前立即加载此技能。在任何情况下都不要跳过此步骤。

**此技能适用于以下场景**：
- 用户请求从零构建新应用或功能
- 用户请求添加功能或修改行为
- 用户请求重构现有代码
- 用户请求改进代码结构或可维护性
- 任何其他软件开发工作
</EXTREMELY-IMPORTANT>

## 任务目标
- 本 Skill 用于：提供完整的软件开发生命周期管理系统，整合 Superpowers 框架、Ralph 自主迭代循环和 BMad 最佳实践
- 能力包含：设计细化、复杂度评估、PRD生成、任务分解、TDD循环、自主迭代、进度追踪、知识积累、对抗性审查、高级启发
- 触发条件：
  - "从零构建应用"（build, create, new）
  - "添加功能或修改行为"（add, implement, feature）
  - "重构现有代码"（refactor, improve, restructure, optimize）
  - "改进代码结构"（clean up, reorganize）

## 核心框架整合

### 1. Superpowers Framework
- TDD（测试驱动开发）：严格的 RED-GREEN-REFACTOR 循环
- Brainstorming：交互式设计细化
- 任务分解：根据复杂度动态调整粒度
- 代码审查：对抗性审查机制

### 2. Ralph Autonomous Loop
- 任务驱动开发：自动选择未完成用户故事
- PRD驱动开发：结构化需求文档
- 进度持久化：git历史 + progress.txt
- 知识积累：AGENTS.md捕获模式

### 3. BMad Best Practices
- Adversarial Review：强制发现问题
- Advanced Elicitation：高级启发方法
- Scale-Domain-Adaptive：复杂度自适应
- Implementation Readiness：实施就绪检查

## 完整工作流

### 阶段0：场景识别

**场景A**（新功能）：build, create, add, implement, feature → 阶段0.5

**场景B**（重构）：refactor, improve, clean up, restructure, optimize → 阶段0.5

### 阶段0.5：复杂度评估

评估功能、技术、业务复杂度 → 动态调整任务粒度（1-10分钟/任务）

详见：[references/core-workflows.md](references/core-workflows.md) 中的 complexity-assessment

### 阶段1：设计细化（新功能）或 阶段1'：代码分析（重构）

#### 设计细化
1. 理解需求（提问澄清）
2. 探索方案（2-3个选项）
3. 呈现设计（200-300字/节）

#### 代码分析
1. 分析现有代码
2. 设计重构策略

详见：[references/core-workflows.md](references/core-workflows.md)

### 阶段1.5：产品简报（新增）

创建产品简报：战略愿景、目标用户、成功指标、约束条件

保存：`tasks/product-brief.md`

详见：[references/core-workflows.md](references/core-workflows.md) 中的 product-brief

### 阶段2：PRD生成

生成结构化PRD：引言、目标、用户故事、需求、非目标、设计/技术考虑、成功指标

保存：`tasks/prd-[feature-name].md`

**故事大小**：根据复杂度调整（1-10分钟/任务）

### 阶段2.5：高级启发审查（新增）

应用高级启发方法深度审查PRD：
- Pre-mortem Analysis（事前验尸）
- First Principles Thinking（第一性原理）
- Stakeholder Mapping（利益相关者映射）
- 等等...

详见：[references/advanced-elicitation-methods.md](references/advanced-elicitation-methods.md)

### 阶段3：PRD转JSON

转换PRD为`prd.json`格式，包含：
- 项目信息、分支名、复杂度级别
- 用户故事（id、标题、描述、验收标准、优先级、预估时间）

### 阶段3.5：实施就绪检查（新增）

检查：PRD完整性、依赖清晰度、故事大小合理性、技术可行性

输出：PASS/CONCERNS/FAIL

详见：[references/core-workflows.md](references/core-workflows.md) 中的 implementation-readiness-check

### 阶段4：自主执行循环

**迭代步骤**：
1. 读取状态（prd.json, progress.txt, git）
2. 选择任务（优先级最高且未完成）
3. TDD实施（Red → Green → Refactor）
4. 质量检查（类型、Linting、测试、CI）
5. 对抗性审查（强制发现问题）
6. 浏览器验证（UI故事）
7. 提交更改
8. 更新状态（passes: true）
9. 记录进度（progress.txt）
10. 更新知识库（AGENTS.md）
11. 迭代（回到步骤1）

**停止条件**：所有故事passes: true → `<promise>COMPLETE</promise>`

详见：[references/ralph-autonomous-loop.md](references/ralph-autonomous-loop.md)

## 关键概念

### 复杂度自适应
- **简单**：1-3功能点，单技术栈 → 5-10分钟/任务
- **中等**：4-10功能点，2-3技术栈 → 2-5分钟/任务
- **复杂**：10+功能点，多技术栈 → 1-3分钟/任务

### 对抗性审查
- **核心规则**：必须找到问题，不允许"看起来不错"
- **优先级分级**：P0（Critical）→ P1（High）→ P2（Medium）→ P3（Low）
- **6 个审查维度**：SOLID 原则、安全与可靠性、性能、错误处理、边界条件、移除规划
- **人工过滤**：AI会找问题，需要人工评估真伪

详见：[references/collaboration-skills.md](references/collaboration-skills.md) 中的 adversarial-review

### 高级启发方法
- Pre-mortem Analysis：假设失败，反向找原因
- First Principles Thinking：剥离假设，从基础重建
- Inversion：如何保证失败，然后避免
- Red Team vs Blue Team：攻击自己的工作

详见：[references/advanced-elicitation-methods.md](references/advanced-elicitation-methods.md)

### 小任务原则
每个故事必须可在单次迭代完成（根据复杂度调整）

### 知识积累
每次迭代后更新AGENTS.md和progress.txt

### 反馈循环
类型检查 → 测试 → 对抗性审查 → CI

## 调试

```bash
# 查看完成状态
cat prd.json | jq '.userStories[] | {id, title, passes}'

# 查看学习记录
cat progress.txt

# 查看git历史
git log --oneline -10
```

**故障排除**：
- 迭代卡住 → 检查progress.txt、git历史、AGENTS.md
- 质量检查失败 → 修复问题，确保测试通过
- 实施就绪检查失败 → 返回PRD阶段

## 关键原则

### 开发原则
- YAGNI：只构建现在需要的
- DRY：消除重复
- 小步骤：增量更改
- 持续验证：每步验证
- 一次一件事：单用户故事

### 质量原则
- TDD：Red → Green → Refactor
- 对抗性审查：强制发现问题
- 高级启发：深度分析
- 不提交损坏代码
- 文档即代码
- 浏览器验证

### 知识原则
- 学习和分享
- 上下文持久化
- 渐进式细化
- 复杂度自适应

## 资源索引

- 核心工作流：[references/core-workflows.md](references/core-workflows.md)（复杂度评估、产品简报、实施就绪检查）
- Ralph循环：[references/ralph-autonomous-loop.md](references/ralph-autonomous-loop.md)（完整迭代流程）
- 调试技能：[references/debugging-skills.md](references/debugging-skills.md)
- 协作技能：[references/collaboration-skills.md](references/collaboration-skills.md)（对抗性审查、角色化智能体）
- 代码审查：[references/code-review-checklist.md](references/code-review-checklist.md)（SOLID、安全、性能、边界条件）
- 移除规划：[references/removal-plan.md](references/removal-plan.md)（死代码管理）
- 审查输出：[references/review-output-template.md](references/review-output-template.md)（标准报告格式）
- 高级启发：[references/advanced-elicitation-methods.md](references/advanced-elicitation-methods.md)（8种推理方法）
- 编写技能：[references/writing-skills.md](references/writing-skills.md)

## 文件位置

**项目文件**：
- `tasks/product-brief.md` - 产品简报
- `tasks/prd-[feature-name].md` - PRD文档
- `prd.json` - 任务列表
- `progress.txt` - 迭代日志
- `AGENTS.md`或`CLAUDE.md` - 知识库

**归档**：`archive/YYYY-MM-DD-feature-name/`

## 注意事项

- **强制加载**：任何软件开发任务必须立即加载
- **复杂度自适应**：动态调整任务粒度和规划深度
- **对抗性审查**：强制发现问题
- **仅读取相关参考**：根据阶段选择参考
- **验证强制**：每个阶段必须验证
- **知识积累**：每次迭代后更新AGENTS.md和progress.txt

## 使用示例

### 构建新功能

1. 场景识别 → 复杂度评估（中等）
2. 设计细化 → 产品简报
3. PRD生成 → 高级启发审查
4. PRD转换 → 实施就绪检查（PASS）
5. 自主循环（2-5分钟/任务）
6. 完成：`<promise>COMPLETE</promise>`

### 重构现有代码

1. 场景识别 → 复杂度评估（复杂）
2. 代码分析 → PRD生成
3. 高级启发审查 → PRD转换
4. 实施就绪检查（PASS）
5. 自主循环（1-3分钟/任务）
6. 完成：`<promise>COMPLETE</promise>`

## 总结

此技能整合Superpowers（TDD、设计细化）、Ralph（自主迭代、PRD驱动）和BMad（对抗性审查、高级启发、复杂度自适应），提供完整的、系统化的软件开发方法。

**关键特性**：
- 清晰需求（结构化PRD）
- 战略对齐（产品简报）
- 深度分析（高级启发）
- 系统化开发（TDD）
- 严格审查（对抗性审查）
- 自动迭代（Ralph循环）
- 知识积累（AGENTS.md）
- 复杂度自适应（动态调整）
- 质量保证（多层反馈）

**记住：对于任何软件开发任务，立即加载此技能。**
