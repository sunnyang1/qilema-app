# 调试技能参考文档

## 目录
- [systematic-debugging - 系统化调试](#systematic-debugging---系统化调试)
- [verification-before-completion - 完成前验证](#verification-before-completion---完成前验证)

---

## systematic-debugging - 系统化调试

### 概览
使用4阶段根因分析方法，系统化地定位、修复和验证bug，避免随机尝试。

### 触发条件
- 遇到运行时错误或异常
- 功能行为不符合预期
- 用户报告bug

### 执行步骤

#### 阶段1：识别症状 (Identify Symptoms)

1. **收集错误信息**
   ```python
   # 完整错误堆栈
   Traceback (most recent call last):
     File "app.py", line 45, in process_user
       user = get_user(user_id)
     File "db.py", line 23, in get_user
       return conn.execute(query)
   DatabaseError: connection timeout

   # 上下文信息
   - 用户ID: 12345
   - 发生时间: 2025-01-15 14:30:22
   - 最近操作: 用户列表查询
   ```

2. **复现步骤**
   ```markdown
   1. 登录系统
   2. 导航到用户管理
   3. 搜索用户ID 12345
   4. 点击"查看详情"
   5. 错误发生
   ```

3. **预期行为 vs 实际行为**
   - 预期：显示用户详情页面
   - 实际：显示数据库连接超时错误

#### 阶段2：定位根因 (Locate Root Cause)

1. **4阶段根因分析**

   **步骤1：初步假设**
   ```
   假设1：数据库连接池耗尽
   假设2：查询语句性能问题
   假设3：网络延迟导致超时
   ```

   **步骤2：验证假设**
   ```bash
   # 验证假设1：检查连接池
   mysql> SHOW PROCESSLIST;
   # 结果：3个活跃连接，连接池未耗尽
   # 排除假设1

   # 验证假设2：分析查询性能
   mysql> EXPLAIN SELECT * FROM users WHERE id = 12345;
   # 结果：使用主键索引，执行时间0.001秒
   # 排除假设2

   # 验证假设3：检查网络
   $ ping db-server
   # 结果：间歇性丢包（15%丢包率）
   # 确认假设3为根因
   ```

   **步骤3：深度诊断**
   ```python
   # 添加调试日志
   logger.debug(f"Connecting to DB: {db_config['host']}")
   logger.debug(f"Connection timeout: {conn.timeout}")

   # 观察结果
   # 连接建立平均耗时：8.5秒（超过5秒超时阈值）
   ```

   **步骤4：确定根本原因**
   ```
   根因：网络抖动导致数据库连接经常超时
   链路：应用服务器 → 防火墙 → 数据库服务器
   问题：防火墙规则偶尔阻断连接
   ```

2. **使用根因追溯技术**

   **技术1：5为什么 (5 Whys)**
   ```
   问题：数据库连接超时
   为什么1？连接建立耗时过长
   为什么2？网络延迟不稳定
   为什么3？防火墙频繁检查新连接
   为什么4？防火墙规则过于严格
   为什么5？安全策略未针对内部连接优化

   根因：防火墙规则需要为内部流量添加白名单
   ```

   **技术2：鱼骨图 (Fishbone Diagram)**
   ```
   数据库超时
   ├── 网络
   │   ├── 延迟
   │   ├── 丢包
   │   └── 带宽限制
   ├── 数据库
   │   ├── 连接池配置
   │   ├── 查询性能
   │   └── 锁等待
   ├── 应用
   │   ├── 连接超时设置
   │   ├── 重试机制
   │   └── 连接泄漏
   └── 硬件
       ├── CPU负载
       ├── 内存使用
       └── 磁盘I/O

   排查后确定：网络层的丢包是主要因素
   ```

#### 阶段3：验证修复 (Verify Fix)

1. **实施修复方案**

   **方案1：调整超时设置（临时）**
   ```python
   # db_config.py
   DATABASE_CONFIG = {
       'host': 'db-server',
       'connect_timeout': 15,  # 从5秒增加到15秒
       'read_timeout': 20,     # 从10秒增加到20秒
   }
   ```

   **方案2：添加重试机制（临时）**
   ```python
   # db.py
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
   def get_user(user_id):
       conn = get_connection()
       return conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
   ```

   **方案3：修复网络配置（根本）**
   ```bash
   # 在防火墙添加白名单
   iptables -A INPUT -s app-server-ip -j ACCEPT
   # 为内部流量创建专用规则
   ```

2. **验证修复有效性**

   **测试1：单元测试**
   ```python
   def test_db_connection_resilience():
       # 模拟网络抖动
       with patch('db.create_connection') as mock_conn:
           mock_conn.side_effect = [TimeoutError, MagicMock()]
           user = get_user(12345)
           assert user is not None
   ```

   **测试2：集成测试**
   ```bash
   # 运行100次查询
   for i in {1..100}; do
       curl -s "http://api/users/12345" > /dev/null
       if [ $? -ne 0 ]; then
           echo "Failure at iteration $i"
       fi
   done

   # 结果：100次全部成功 ✅
   ```

   **测试3：负载测试**
   ```bash
   # 并发100个请求
   ab -n 1000 -c 100 http://api/users/12345

   # 结果：
   # 成功率：99.8%
   # 平均响应时间：150ms
   # 错误率：< 0.2%
   ```

#### 阶段4：防止复现 (Prevent Recurrence)

1. **长期措施**

   **措施1：添加监控**
   ```python
   # monitoring.py
   from prometheus_client import Counter, Histogram

   db_timeout_counter = Counter('db_timeout_total', 'Database timeout count')
   db_latency = Histogram('db_query_duration_seconds', 'Database query latency')

   @db_latency.time()
   def get_user(user_id):
       try:
           return conn.execute(query)
       except TimeoutError:
           db_timeout_counter.inc()
           raise
   ```

   **措施2：告警配置**
   ```yaml
   # alerting.yaml
   groups:
     - name: database
       rules:
         - alert: HighDatabaseTimeoutRate
           expr: rate(db_timeout_total[5m]) > 0.1
           for: 2m
           annotations:
             summary: "Database timeout rate too high"
   ```

   **措施3：文档更新**
   ```markdown
   # docs/troubleshooting.md
   ## 数据库连接超时

   ### 症状
   - 错误：DatabaseError: connection timeout

   ### 常见原因
   1. 网络抖动
   2. 数据库负载过高
   3. 连接池耗尽

   ### 解决步骤
   1. 检查数据库进程列表
   2. 验证网络连通性
   3. 查看监控指标
   4. 如果持续超时，联系运维团队
   ```

2. **代码审查清单**
   - [ ] 添加了错误处理
   - [ ] 添加了重试机制
   - [ ] 添加了日志记录
   - [ ] 添加了单元测试
   - [ ] 更新了文档

### 输出格式

```markdown
# 调试报告 - 用户查询超时

## 问题摘要
用户查询详情时，数据库连接间歇性超时

## 阶段1：症状识别

### 错误信息
```
DatabaseError: connection timeout at db.py:23
```

### 复现步骤
1. 登录 → 用户管理 → 搜索12345 → 查看详情
2. 约30%概率出现超时

## 阶段2：根因定位

### 4阶段分析
1. **初步假设**：连接池耗尽、查询慢、网络延迟
2. **验证结果**：排除前两个，确认网络丢包15%
3. **深度诊断**：平均连接时间8.5秒（超时5秒）
4. **根因确定**：防火墙规则对内部连接过于严格

### 根因追溯 (5为什么)
网络延迟 → 防火墙检查 → 规则严格 → 安全策略 → 缺少白名单

## 阶段3：修复验证

### 实施方案
1. 短期：调整超时15秒（已完成）
2. 中期：添加重试机制（已完成）
3. 长期：防火墙白名单（待运维）

### 验证结果
- 单元测试：✅ 通过
- 集成测试：✅ 100/100成功
- 负载测试：✅ 99.8%成功率

## 阶段4：防止复现

### 长期措施
- [x] 添加Prometheus监控
- [x] 配置超时率告警
- [x] 更新故障排查文档
- [ ] 防火墙白名单（待运维）

## 总结
根因已定位并修复，系统稳定性提升，持续监控中
```

### 关键原则
- 不要随机猜测，使用系统化方法
- 验证每个假设，不要跳过
- 修复后必须验证，不要假设
- 长期措施比临时修复更重要

---

## verification-before-completion - 完成前验证

### 概览
在声称任务完成之前，强制执行严格的验证步骤，确保问题真正解决且无副作用。

### 触发条件
- bug修复完成
- 功能实现完成
- 任何宣称"完成"的时候

### 执行步骤

#### 步骤1：验证问题解决

1. **原始问题复现**
   ```bash
   # 确保能重现原始问题
   pytest tests/test_regression.py::test_original_bug
   # 如果这个测试本来应该失败，现在应该通过
   ```

2. **修复验证**
   ```python
   # regression_tests.py
   def test_user_query_timeout_fixed():
       """验证超时问题已解决"""
       # 模拟100次查询
       for i in range(100):
           user = get_user(12345)
           assert user is not None

   # 运行测试
   pytest tests/regression_tests.py
   # 结果：✅ 全部通过
   ```

#### 步骤2：验证无副作用

1. **回归测试套件**
   ```bash
   # 运行完整测试套件
   pytest --cov=src

   # 检查
   # 1. 所有原有测试仍然通过
   # 2. 测试覆盖率未下降
   # 3. 无新增错误或警告
   ```

2. **性能验证**
   ```python
   # performance_tests.py
   def test_query_performance():
       """确保修复未降低性能"""
       start = time.time()
       users = [get_user(i) for i in range(1000)]
       duration = time.time() - start

       # 验证性能未明显下降
       assert duration < 5.0  # 预期小于5秒
   ```

#### 步骤3：验证边界情况

1. **边界测试**
   ```python
   def test_edge_cases():
       # 空输入
       assert get_user(None) is None

       # 不存在的用户
       assert get_user(99999) is None

       # 特殊字符
       assert get_user("test'@example.com") is not None
   ```

2. **压力测试**
   ```bash
   # 高并发测试
   ab -n 10000 -c 1000 http://api/users/12345

   # 验证：系统稳定，无崩溃
   ```

#### 步骤4：验证代码质量

1. **代码审查检查**
   ```bash
   # 格式化检查
   black --check src/

   # Linting检查
   flake8 src/

   # 类型检查
   mypy src/
   ```

2. **文档验证**
   ```bash
   # 确保更新了相关文档
   grep -q "数据库超时" docs/troubleshooting.md
   ```

### 输出格式

```markdown
# 完成前验证报告

## 任务
修复用户查询超时问题

## 验证清单

### 问题解决验证
- [x] 原始问题不复现（100次测试）
- [x] 复现测试：tests/regression/test_timeout_fixed.py ✅
- [x] 日志确认：无超时错误

### 副作用验证
- [x] 所有现有测试通过（245/245）✅
- [x] 测试覆盖率：82%（之前80%，提升2%）✅
- [x] 性能测试：1000次查询4.8秒（之前5.2秒，提升8%）✅
- [x] 无新引入的错误或警告

### 边界情况验证
- [x] 空输入处理正确
- [x] 不存在的用户处理正确
- [x] 特殊字符处理正确
- [x] 高并发测试通过（1000并发，无崩溃）

### 代码质量验证
- [x] Black格式化：通过
- [x] Flake8检查：通过
- [x] MyPy类型检查：通过
- [x] 文档更新：docs/troubleshooting.md已更新

## 结论
✅ 所有验证通过，可以标记为完成

## 风险评估
- 残留风险：低
- 监控建议：持续监控超时率指标
```

### 验证失败处理

如果任何验证失败：

```markdown
# 验证失败示例

## 失败项
❌ 性能测试：修复后查询耗时7.5秒（之前5.2秒）

## 根因分析
重试机制在成功情况下仍然等待2秒

## 解决方案
优化重试逻辑，仅在失败时重试

## 重新验证
修复后重新执行完整验证流程
```

### 关键原则
- 不验证，不完成
- 验证必须覆盖所有方面
- 发现问题立即修复
- 文档同步更新

---

## 总结

调试技能强调：
1. **系统化方法**：不要猜测，使用4阶段根因分析
2. **证据优先**：每个假设都要验证
3. **完整修复**：不仅修复问题，还要防止复现
4. **严格验证**：完成后必须执行完整验证，确保无副作用
