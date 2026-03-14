# AGENTS.md - 项目知识库

## 服务层重构 - 最佳实践

### 阶段4: 模型层优化

#### 关联加载策略
```python
# 高频/大数据量 - 使用 lazy='dynamic'（返回 Query 对象）
checkins = db_relationship("CheckIn", lazy="dynamic")

# 中频/小数据量 - 使用 lazy='select'（默认）
emergency_contacts = db_relationship("EmergencyContact", lazy="select")

# 一对一/总是需要 - 使用 lazy='joined'（立即加载）
health_record = db_relationship("HealthRecord", lazy="joined", uselist=False)
```

#### 数据库索引
```python
__table_args__ = (
    Index("idx_users_phone_created", "phone", "created_at"),
    Index("idx_users_last_sign_in", "last_sign_in"),
)
```

#### to_dict() 优化
```python
# 预定义关联关系列表，避免运行时 inspect
_RELATIONSHIP_NAMES = frozenset(["emergency_contacts", "checkins", ...])

# 支持选择性包含关联关系
def to_dict(self, include_relations: Optional[List[str]] = None) -> dict:
    ...

# 便捷方法：包含指定关联关系
def to_dict_with_relations(self, relations: List[str]) -> dict:
    ...
```

### 阶段5: 代码复用优化

#### CacheMixin 使用
```python
from app.core.cache_mixin import CacheMixin

class UserService(BaseService[User], CacheMixin):
    cache_prefix = "user"
    cache_ttl = 300

    def get_by_id(self, user_id: str):
        # 1. 尝试从缓存获取
        cache_key = self._make_key(f"id:{user_id}")
        cached = self._get(cache_key)
        if cached:
            return cached

        # 2. 查询数据库
        user = ...

        # 3. 写入缓存
        self._set(cache_key, user)
        return user
```

#### QueryBuilder 使用
```python
from app.core.query_builder import QueryBuilder, paginate

# 方法1: 使用 QueryBuilder
builder = QueryBuilder(db.query(User), User)
result = (
    builder.filter(status='active')
    .where_like('name', f'%{keyword}%')
    .order_by('created_at', desc=True)
    .paginate(page=1, per_page=20)
    .execute()
)

# 方法2: 使用便捷函数
pagination = paginate(query, page=1, per_page=20)
```

#### 统一缓存失效
```python
def _invalidate_user_caches(self, user_id: str, phone: Optional[str] = None):
    """失效用户相关缓存"""
    self.invalidate_entity_cache(f"id:{user_id}")
    if phone:
        self.invalidate_entity_cache(f"phone:{phone}")
    self._invalidate_list_cache()
    self._invalidate_pattern("search:*")
```

---

## CI/CD 流程 (Consolidated)

### 文件结构

```
.github/workflows/
├── ci.yml          # 代码检查、测试、lint
├── build.yml       # 构建镜像、安全扫描
├── deploy.yml      # 部署到 staging/production
└── pr-checks.yml   # PR 标题检查、依赖审查

docker-compose.yml          # 基础服务定义
docker-compose.dev.yml      # 开发环境覆盖
docker-compose.prod.yml     # 生产环境覆盖
```

### 使用方式

**开发环境**:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**生产环境**:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Workflow 触发规则

| Workflow | 触发条件 | 说明 |
|----------|----------|------|
| ci.yml | PR, push to main/develop | 运行测试、lint |
| build.yml | PR, push to main, tag v* | 构建镜像、安全扫描 |
| deploy.yml | push to main, tag v*, manual | 部署 staging/production |
| pr-checks.yml | PR opened/edited | 标题检查、依赖审查 |

### 已弃用文件

以下文件已标记弃用，将在未来版本中移除：
- `docker-compose.override.yml` → 使用 `docker-compose.dev.yml`
- `docker-compose.staging.yml` → 使用 `docker-compose.prod.yml` + env vars
- `docker-compose.test.yml` → 使用 `docker-compose.yml`
- `build-consolidated.yml`, `deploy-consolidated.yml`, etc. → 使用新 workflow

---

## CI/CD 最佳实践

### GitHub Actions Workflow 配置

#### 1. 并发控制（必须）
```yaml
# 防止多个 workflow 同时运行
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# 部署特殊配置（不能取消）
concurrency:
  group: deployment-${{ github.ref }}
  cancel-in-progress: false
```

#### 2. 超时设置（必须）
```yaml
jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # 根据任务复杂度设置
```

#### 3. Action 版本管理
```yaml
# 推荐使用的稳定版本
actions/checkout@v4
actions/setup-python@v5
actions/cache@v4
actions/upload-artifact@v4
codecov/codecov-action@v4
github/codeql-action/upload-sarif@v3
```

#### 4. pre-commit 优化
```yaml
# 单独运行 pre-commit，避免在矩阵中重复
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Cache pre-commit
        uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
      - name: Run pre-commit
        run: |
          pip install pre-commit
          pre-commit run --all-files --show-diff-on-failure
```

#### 5. Docker 构建优化
```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    push: ${{ github.event_name != 'pull_request' }}
    tags: ${{ steps.meta.outputs.tags }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

#### 6. 安全扫描配置
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: your-image:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'  # 只关注严重问题
    exit-code: '0'  # 不阻止构建
    ignore-unfixed: true  # 忽略无修复版本的漏洞
```

#### 7. 条件执行
```yaml
# PR 不推送镜像
push: ${{ github.event_name != 'pull_request' }}

# Secret 存在时才通知
if: always() && secrets.SLACK_WEBHOOK != ''
```

### PR 规范

#### 标题格式（约定式提交）
```
feat: 添加用户登录功能
fix: 修复数据库连接问题
docs: 更新 API 文档
refactor: 重构通知服务
ci: 修复 GitHub Actions 配置
```

#### Workflow 检查
- `pr-title-check.yml`: 自动验证 PR 标题格式
- `dependency-review.yml`: 检查依赖安全漏洞

---

## 设计原则

### 代码设计
1. **关联加载策略**：按使用频率选择 lazy 模式
   - 高频/大数据量：dynamic
   - 中频/小数据量：select
   - 一对一/必需要：joined

2. **缓存策略**：
   - 单个实体：长期缓存（5分钟+）
   - 列表数据：短期缓存（60秒）
   - 数据变更时主动失效

3. **查询优化**：
   - 使用 QueryBuilder 替代原始 SQLAlchemy 查询
   - 分页查询使用 QueryBuilder.paginate()
   - 复杂条件使用链式调用

### CI/CD 设计
1. **并发控制**：所有 workflow 必须配置 concurrency
2. **超时设置**：所有 job 必须配置 timeout-minutes
3. **版本管理**：定期检查并升级 action 版本
4. **安全优先**：安全扫描不阻止构建但报告问题
5. **条件执行**：根据事件类型和 secrets  availability 控制步骤

## 测试

```bash
# 运行核心测试
python -m pytest tests/test_user_model.py tests/test_user_service.py -v

# 运行 CacheMixin 测试
python -m pytest tests/unit/core/test_cache_mixin.py -v

# 运行 QueryBuilder 测试
python -m pytest tests/unit/core/test_query_builder.py -v
```

## CI/CD 测试

```bash
# 本地验证 workflow 语法
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# 使用 act 本地运行 workflow（需要安装 act）
act -j pre-commit
```
