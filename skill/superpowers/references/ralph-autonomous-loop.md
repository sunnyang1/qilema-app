# Ralph自主迭代循环详细指导

## 概览

Ralph自主迭代循环是Superpowers的核心执行机制，通过自动化的任务选择、实施和进度追踪，实现高效软件开发。

## 完整迭代过程

### 步骤1：读取状态

**目标**：获取当前项目状态和进度信息

**执行步骤**：

1. **读取PRD文件**
   ```bash
   cat prd.json | jq '.'
   ```
   - 获取项目名称、分支名、描述
   - 查看所有用户故事及其状态
   - 识别优先级和依赖关系

2. **读取进度文件**
   ```bash
   cat progress.txt
   ```
   - 查看已完成的学习记录
   - 了解代码库模式
   - 识别需要注意的常见陷阱

3. **检查Git状态**
   ```bash
   git branch --show-current
   git status
   ```
   - 确认在正确的分支上
   - 检查是否有未提交的更改
   - 确保工作目录干净

### 步骤2：选择任务

**目标**：选择下一个待实施的最高优先级用户故事

**选择策略**：

1. **筛选条件**
   - `passes: false` 的故事
   - 优先级最高的故事（priority数值最小）
   - 依赖已满足的故事（前置任务已完成）

2. **选择输出**
   ```
   选择的故事：US-003 - 创建用户注册API
   优先级：1
   状态：未完成
   ```

3. **停止条件**
   - 如果所有故事都标记为 `passes: true`
   - 输出：`<promise>COMPLETE</promise>`
   - 退出迭代循环

### 步骤3：TDD实施

**目标**：严格遵循TDD循环实施所选故事

#### Red阶段：编写失败测试

**检查清单**：
- [ ] 测试描述了预期行为
- [ ] 测试明确定义了方法、输入、输出
- [ ] 运行测试，确认失败（红色）
- [ ] 失败原因清晰明确

**示例**：
```python
# test_user_api.py
def test_create_user_success():
    """成功创建用户"""
    response = client.post('/api/users', json={
        'name': 'Alice',
        'email': 'alice@example.com'
    })
    assert response.status_code == 201
    assert 'id' in response.json()
```

**运行测试**：
```bash
pytest tests/test_user_api.py::test_create_user_success -v
# 预期：FAILED（用户API尚未实现）
```

#### Green阶段：实现最小代码

**检查清单**：
- [ ] 编写使测试通过的**最小**代码
- [ ] 代码简单且专注
- [ ] 不过度工程化或优化
- [ ] 运行测试，确认通过（绿色）

**示例**：
```python
# app.py
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = str(uuid.uuid4())
    return jsonify({'id': user_id}), 201
```

**运行测试**：
```bash
pytest tests/test_user_api.py::test_create_user_success -v
# 预期：PASSED
```

#### Refactor阶段：优化代码

**检查清单**：
- [ ] 优化代码质量和可读性
- [ ] 减少重复（DRY原则）
- [ ] 改进命名和结构
- [ ] 保持所有测试通过
- [ ] 频繁运行测试确保无回归

**重构示例**：
```python
# 重构前
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = str(uuid.uuid4())
    return jsonify({'id': user_id}), 201

# 重构后
@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    user_data = _validate_user_data(request.get_json())
    return _create_user_record(user_data)

def _validate_user_data(data):
    """验证用户数据"""
    if not data or 'name' not in data or 'email' not in data:
        raise ValueError("Invalid user data")
    return data

def _create_user_record(data):
    """创建用户记录"""
    user_id = str(uuid.uuid4())
    return jsonify({'id': user_id}), 201
```

**验证重构**：
```bash
# 运行所有测试
pytest tests/ -v
# 预期：全部PASSED
```

**TDD循环总结**：
```
Red → Green → Refactor → (下一个测试) → Red → Green → Refactor
```

### 步骤4：质量检查

**目标**：确保代码质量满足所有标准

**检查项目**：

1. **类型检查**
   ```bash
   # Python
   mypy .

   # TypeScript
   npm run type-check
   ```
   - 无类型错误
   - 所有类型注解正确

2. **代码风格检查**
   ```bash
   # Python
   flake8 .
   black --check .

   # JavaScript
   npm run lint
   ```
   - 符合项目代码风格
   - 无Linting警告

3. **测试**
   ```bash
   pytest tests/ -v
   # 或
   npm test
   ```
   - 所有测试通过
   - 无测试失败

4. **CI检查**
   ```bash
   # 查看CI状态
   git status
   ```
   - CI保持绿色
   - 无构建失败

5. **代码审查**（新增）

**目标**：使用结构化检查清单进行对抗性审查

**执行步骤**：

1. **加载审查检查清单**
   - 读取 [code-review-checklist.md](code-review-checklist.md)
   - 遍历 6 个审查维度：
     - SOLID 原则（SRP、OCP、LSP、ISP、DIP）
     - 安全与可靠性（XSS、注入、SSRF、竞态条件）
     - 性能（N+1 查询、CPU 热点、缓存）
     - 错误处理（吞并异常、异步错误）
     - 边界条件（null/undefined、空集合、数值边界）
     - 移除规划（死代码识别）

2. **执行审查**
   - 使用新鲜上下文（无原始推理访问）
   - 采用批判性立场，假设问题存在
   - 按优先级分类问题（P0-P3）

3. **生成审查报告**
   - 使用 [review-output-template.md](review-output-template.md) 格式
   - 按优先级分组问题（P0、P1、P2、P3）
   - 提供具体修复建议

4. **修复发现的问题**
   - P0（Critical）：必须立即修复
   - P1（High）：应该修复
   - P2（Medium）：可以延后或创建后续任务
   - P3（Low）：可选改进

**审查示例**：
```markdown
## Code Review Summary

**Files reviewed**: 2 files, 89 lines changed
**Overall assessment**: REQUEST_CHANGES

---

## Findings

### P0 - Critical
(none)

### P1 - High
1. **[app.py:45]** 竞态条件 - Check-Then-Act 模式
   - 余额检查后跟扣款，两个并发请求可能导致透支
   - 建议修复：使用数据库事务和原子操作

### P2 - Medium
2. **[app.py:23]** 吞并异常
   - 空的 catch 块隐藏潜在错误
   - 建议修复：记录错误并适当处理

### P3 - Low
3. **[app.py:12]** 魔术数字
   - 硬编码的超时值 `3000` 没有命名常量
   - 建议修复：定义为 `REQUEST_TIMEOUT_MS`
```

详见：[collaboration-skills.md](collaboration-skills.md#adversarial-review---对抗性审查增强版)

**关键规则**：
- **切勿提交损坏的代码**
- 所有检查必须通过才能继续
- 发现问题立即修复
- P0/P1 问题必须在提交前修复

### 步骤5：浏览器验证（仅UI故事）

**触发条件**：用户故事涉及UI更改

**执行步骤**：

1. **启动开发服务器**
   ```bash
   npm run dev
   # 或
   python -m flask run
   ```

2. **使用dev-browser技能验证**
   - 导航到相关页面
   - 测试UI交互
   - 验证验收标准

3. **验证清单**
   - [ ] UI元素正确显示
   - [ ] 交互按预期工作
   - [ ] 验收标准全部满足
   - [ ] 无控制台错误

**示例**：
```
验证用户注册页面：
1. 访问 /register 页面
2. 输入用户名 "Alice"
3. 输入邮箱 "alice@example.com"
4. 点击"注册"按钮
5. 验证：重定向到 /profile 页面
6. 验证：显示欢迎消息 "Welcome, Alice!"
```

### 步骤6：提交更改

**目标**：将已验证的更改提交到Git

**提交检查清单**：
- [ ] 所有质量检查通过
- [ ] 测试全部通过
- [ ] UI已验证（如适用）
- [ ] 代码已审查（如需要）

**提交消息格式**：
```
feat: implement user registration API

- Add POST /api/users endpoint
- Implement basic user creation logic
- Add user data validation

Closes US-003
```

**执行提交**：
```bash
git add .
git commit -m "feat: implement user registration API"
```

### 步骤7：更新任务状态

**目标**：在PRD中标记故事为已完成

**更新JSON**：
```json
{
  "id": "US-003",
  "title": "创建用户注册API",
  "passes": true,  // 从false改为true
  "notes": "实现完成，测试通过"
}
```

**保存更新**：
```bash
# 更新prd.json
jq '.userStories[2].passes = true' prd.json > prd.json.tmp && mv prd.json.tmp prd.json
```

### 步骤8：记录进度

**目标**：记录本次迭代的学习和重要发现

**进度文件格式**：
```
================================================================================
[2025-01-15 14:30:22] - [US-003] 创建用户注册API

实施摘要：
- 实现了POST /api/users端点
- 添加了基础用户创建逻辑
- 实现了用户数据验证

更改：
- 创建：app.py (新增create_user函数)
- 创建：tests/test_user_api.py (新增test_create_user_success)
- 修改：requirements.txt (添加Flask依赖)

重要学习：
- 模式发现：此代码库使用uuid4生成用户ID
- 注意事项：用户数据验证必须在创建记录之前完成
- 有用上下文：所有API端点都在app.py中定义
- 测试模式：使用client fixture进行API测试

================================================================================
```

**代码库模式部分**：
```
================================================================================
代码库模式

1. 用户ID生成：使用uuid.uuid4()生成唯一ID
2. API响应格式：统一使用{'id': user_id}格式
3. 错误处理：使用raise ValueError抛出验证错误
4. 测试命名：使用test_<功能>_<场景>格式

================================================================================
```

### 步骤9：更新知识库

**目标**：将可复用的知识添加到AGENTS.md

**更新策略**：

1. **识别编辑的目录**
   - 本迭代编辑了：app.py, tests/

2. **检查AGENTS.md文件**
   ```bash
   find . -name "AGENTS.md" -o -name "CLAUDE.md"
   ```

3. **更新知识库**

**AGENTS.md示例**：
```markdown
# app/ 目录知识库

## API端点模式

所有API端点在app.py中定义，遵循以下约定：

```python
@app.route('/api/<resource>', methods=['<METHOD>'])
def handle_<resource>():
    data = request.get_json()
    # 验证数据
    validated_data = _validate(data)
    # 创建/更新记录
    result = _create_record(validated_data)
    return jsonify(result), status_code
```

## 用户ID生成

使用`uuid.uuid4()`生成唯一用户ID：

```python
import uuid

user_id = str(uuid.uuid4())
```

## 测试模式

使用Flask client fixture进行API测试：

```python
def test_api_endpoint(client):
    response = client.post('/api/resource', json={...})
    assert response.status_code == expected_code
```

## 注意事项

- 用户数据验证必须在创建记录之前完成
- 所有API响应使用jsonify()格式化
- 错误处理使用raise ValueError
```

**更新原则**：
- 仅记录通用、可复用的模式
- 不记录故事特定的细节
- 包含代码示例
- 标记注意事项和陷阱

### 步骤10：迭代

**目标**：返回步骤1，继续下一个用户故事

**迭代流程**：
```
步骤1：读取状态 → 步骤2：选择任务 → ... → 步骤9：更新知识库
                        ↑                                          ↓
                        ←←←←←←←←← 步骤10：返回 ←←←←←←←←←←←
```

**停止条件**：
- 所有用户故事标记为 `passes: true`
- 输出 `<promise>COMPLETE</promise>`
- 退出循环

## 调试指南

### 检查当前状态

```bash
# 查看完成状态
cat prd.json | jq '.userStories[] | {id, title, passes}'

# 查看学习记录
cat progress.txt | grep "重要学习" -A 10

# 查看最近的提交
git log --oneline -10

# 查看分支状态
git status
```

### 故障排除

#### 迭代卡住

**症状**：无法选择下一个任务或实施卡住

**诊断步骤**：
1. 检查 `progress.txt` 中的学习记录
2. 查看 `git log` 了解最近的更改
3. 阅读相关目录中的 `AGENTS.md`
4. 检查 `prd.json` 中的需求是否清晰

**解决方案**：
- 如果需求不明确，重新审查PRD
- 如果缺少上下文，查看AGENTS.md和progress.txt
- 如果依赖未满足，检查前置任务状态

#### 质量检查失败

**症状**：测试失败、类型错误或Linting问题

**诊断步骤**：
```bash
# 查看测试失败详情
pytest tests/ -v

# 查看类型错误
mypy . --show-error-codes

# 查看Linting问题
flake8 . --show-source
```

**解决方案**：
1. 修复测试失败
2. 修复类型错误或Linting问题
3. 确保所有测试通过
4. **切勿提交损坏的代码**

#### UI验证失败

**症状**：浏览器中UI不符合预期

**诊断步骤**：
1. 检查验收标准是否明确
2. 查看控制台错误
3. 验证CSS/JS文件是否正确加载

**解决方案**：
1. 修复UI问题
2. 重新验证所有验收标准
3. 记录UI特定模式到AGENTS.md

## 最佳实践

### 迭代大小

**正确的迭代**：
- 添加数据库列和迁移
- 向现有页面添加UI组件
- 更新服务器操作的新逻辑
- 向列表添加过滤器下拉菜单

**过大的迭代（需要拆分）**：
- "构建整个仪表板"
- "添加身份验证"
- "重构API"

### 知识积累

**关键原则**：
- 每次迭代后立即更新AGENTS.md
- 记录发现的模式和注意事项
- 包含代码示例
- 未来迭代将从这些模式中受益

**有价值的知识类型**：
- 代码库约定（命名、结构）
- API模式（如何调用特定模块）
- 测试模式（如何测试特定功能）
- 配置需求（环境变量、依赖）
- 常见陷阱（需要特别注意的事项）

### 反馈循环

**必须的反馈循环**：
1. **类型检查**：捕获类型错误
2. **测试**：验证行为正确性
3. **CI**：确保集成测试通过
4. **浏览器验证**：UI更改必须在浏览器中验证

**损坏代码的后果**：
- 在迭代间累积
- 导致回归
- 难以调试
- 增加维护成本

## 总结

Ralph自主迭代循环通过以下机制确保高质量软件开发：

- **自动任务选择**：基于优先级和依赖关系
- **严格TDD**：RED-GREEN-REFACTOR循环
- **质量保证**：多层检查确保代码质量
- **知识积累**：AGENTS.md捕获可复用模式
- **进度追踪**：progress.txt记录学习历史

遵循此循环，可以实现高效、可靠、可维护的软件开发。
