# 测试组织规范文档

## 1. 概述

本文档定义了起了吗App项目的测试组织规范，包括测试文件命名规则、测试分类、测试清理流程等，旨在确保测试套件的稳定性和可维护性。

## 2. 测试文件命名规则

### 2.1 单元测试文件命名

**格式**: `test_<module_name>.py`

**示例**:
- `test_user_service.py` - UserService的单元测试
- `test_device_service.py` - DeviceService的单元测试
- `test_health_record_service.py` - HealthRecordService的单元测试

**规则**:
- 必须以`test_`开头
- 模块名称应为小写，使用下划线分隔
- **禁止在文件名中使用hash后缀**（如`test_user_service-4d794b424b.py`）
- 文件名应简洁且描述性强

### 2.2 集成测试文件命名

**格式**: `test_<feature>_integration.py`

**示例**:
- `test_notification_integration.py` - 通知功能集成测试

**规则**:
- 必须以`test_`开头，以`_integration.py`结尾
- 功能名称应为小写，使用下划线分隔

### 2.3 其他测试文件命名

**配置测试**: `test_<component>_<aspect>.py`
- `test_config_validation.py` - 配置验证测试
- `test_cache_decorator.py` - 缓存装饰器测试

## 3. 测试分类

### 3.1 单元测试 (Unit Tests)

**定义**: 测试单个函数、方法或类，隔离外部依赖（如数据库、网络等）

**特点**:
- 快速执行
- 不依赖外部系统
- 使用Mock隔离依赖
- 覆盖边界条件和异常情况

**存放位置**: `tests/`目录下（当前不使用子目录）

**示例**:
```python
def test_create_health_record_success(db, health_service):
    """测试成功创建健康档案"""
    # Given
    data = HealthRecordCreate(...)
    # When
    result = health_service.create_health_record(db, data)
    # Then
    assert result is not None
```

### 3.2 集成测试 (Integration Tests)

**定义**: 测试多个组件或服务之间的交互，使用真实的数据库和外部服务

**特点**:
- 测试组件间的集成
- 使用测试数据库
- 可能使用真实的外部服务（如Redis）
- 执行速度较慢

**示例**:
```python
def test_notification_integration():
    """测试通知发送集成流程"""
    # 测试从异常检测到通知发送的完整流程
```

### 3.3 E2E测试 (End-to-End Tests)

**定义**: 测试完整的用户场景，从前端到后端

**状态**: 当前不实现E2E测试，将来可根据需要添加

## 4. 测试结构规范

### 4.1 测试类组织

**格式**:
```python
class Test<ModuleName>:
    """测试描述"""

    def test_<feature>_<scenario>(self, fixtures):
        """测试描述"""
        # Given - 准备测试数据
        # When - 执行操作
        # Then - 验证结果
```

**规则**:
- 测试类以`Test`开头，使用大驼峰命名法
- 测试方法以`test_`开头，使用小写和下划线
- 测试方法名应清晰描述测试的场景
- 使用`pytest.fixture`管理测试数据

### 4.2 Fixture命名

**格式**: `test_<resource_name>` 或 `<resource_name>`

**示例**:
```python
@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(...)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def health_service():
    """创建健康档案服务实例"""
    return HealthRecordService()
```

**规则**:
- Fixture函数名应简洁且描述性强
- 清理操作应在`finally`块中或使用`yield`实现
- 避免Fixture之间的隐式依赖

### 4.3 数据库Fixture

**格式**:
```python
@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

**规则**:
- 使用`scope="function"`确保每个测试都有干净的数据库
- 在`finally`块中清理数据库
- 使用SQLite内存数据库进行测试

## 5. 测试清理流程

### 5.1 定期清理

**频率**: 每月或每个Sprint

**清理内容**:
- 删除过时的测试文件
- 合并重复的测试
- 更新测试文档
- 清理临时测试数据

**流程**:
1. 运行完整测试套件
2. 识别未通过的测试
3. 分析失败原因（代码变更 vs 测试问题）
4. 删除或归档无效测试
5. 更新相关文档

### 5.2 代码重构时的测试清理

**触发条件**: 服务层重构或API变更

**流程**:
1. 识别受影响的服务
2. 列出相关测试
3. 更新测试以使用新API
4. 验证所有测试通过
5. 更新测试文档

### 5.3 测试命名清理

**触发条件**: 发现不符合命名规范的测试文件

**流程**:
1. 识别不符合规范的文件（如带hash后缀的文件）
2. 重命名文件为规范格式
3. 更新所有相关导入
4. 验证测试仍然通过

## 6. 测试最佳实践

### 6.1 测试编写原则

**AAA模式**: Given-When-Then
```python
def test_create_user_duplicate(db):
    # Given - 已存在用户
    existing_user = User(phone="13800138000")
    db.add(existing_user)
    db.commit()

    # When - 创建相同手机号的用户
    with pytest.raises(Exception):
        create_user(db, User(phone="13800138000"))

    # Then - 抛出异常
    pass
```

### 6.2 测试数据隔离

- 每个测试应该独立，不依赖其他测试
- 使用fixture创建测试数据
- 在测试结束后清理数据

### 6.3 异常测试

**必须覆盖的场景**:
- 无效输入
- 权限不足
- 资源不存在
- 数据库约束违反
- 网络错误

**示例**:
```python
def test_get_user_not_found(db):
    """测试获取不存在的用户"""
    with pytest.raises(ValueError, match="用户不存在"):
        user_service.get_user_by_id(db, "invalid_id")
```

### 6.4 Mock使用原则

**使用Mock的场景**:
- 测试外部API调用
- 测试第三方服务集成
- 测试时间相关逻辑

**不应该Mock的场景**:
- 数据库操作（使用测试数据库）
- 业务逻辑核心
- 模型关系

### 6.5 断言原则

- 每个测试应该至少一个断言
- 断言消息应该清晰
- 使用`pytest.raises`测试异常
- 避免过于复杂的断言逻辑

## 7. 测试覆盖目标

### 7.1 单元测试覆盖率

**目标**: >85%

**测量**: 使用pytest-cov插件

```bash
pytest --cov=app --cov-report=html
```

### 7.2 核心功能覆盖率

**必须100%覆盖**:
- 用户认证和授权
- SOS紧急呼叫
- 异常检测和告警
- 设备数据上传

**应该>90%覆盖**:
- 健康档案管理
- 紧急联系人管理
- 通知发送

### 7.3 边界条件测试

每个功能必须测试:
- 最小值边界
- 最大值边界
- 空值/None
- 无效值
- 并发操作

## 8. 测试失败处理

### 8.1 调试失败测试

**步骤**:
1. 单独运行失败测试：`pytest tests/test_module.py::test_name -v`
2. 查看完整错误信息：`pytest --tb=long`
3. 检查数据库状态
4. 验证fixture数据
5. 查看相关日志

### 8.2 Flaky测试处理

**定义**: 偶尔失败、偶尔通过的测试

**处理方式**:
- 重试机制（谨慎使用）
- 隔离测试环境因素
- 修复根本原因
- 考虑删除不可靠的测试

### 8.3 慢速测试优化

**目标**: 每个测试<5秒

**优化方法**:
- 减少数据库操作
- 使用事务回滚而不是删除
- Mock外部服务
- 并行运行独立测试

## 9. CI/CD集成

### 9.1 测试运行命令

```bash
# 单元测试
pytest tests/ -v --tb=short

# 带覆盖率
pytest tests/ --cov=app --cov-report=xml

# 快速测试（跳过集成测试）
pytest tests/ -m "not integration" -v
```

### 9.2 测试报告

- JUnit XML：用于CI/CD集成
- HTML覆盖率报告：用于本地查看
- 控制台输出：用于快速反馈

### 9.3 失败处理

- 测试失败时，CI应该失败
- 提供详细的错误报告
- 上传覆盖率报告
- 通知相关人员

## 10. 文档维护

### 10.1 更新频率

- 代码结构变更时更新
- 新增测试类型时更新
- 发现新的最佳实践时更新
- 每季度审查一次

### 10.2 责任分工

- 测试开发人员：编写和维护测试
- 代码审查人员：确保测试符合规范
- 技术负责人：维护测试文档

## 11. 参考资源

- [Pytest官方文档](https://docs.pytest.org/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [测试覆盖率工具](https://coverage.readthedocs.io/)

---

**文档版本**: 1.0
**最后更新**: 2026-02-02
**维护者**: 开发团队
