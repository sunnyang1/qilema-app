# PRD: 通知服务完善（模拟实现）

## 1. Introduction/Overview

### Description
为"起了吗App"完善通知服务的四个核心通知渠道（推送、短信、电话、邮件）的实现。当前系统已有完整的通知管理框架，但四个通知渠道仅有模拟日志，缺乏完整的行为模拟和错误处理机制。

### Problem Being Solved
- 当前通知服务的四个渠道（推送、短信、电话、邮件）只有简单的日志输出，无法模拟真实场景
- 缺乏统一的模拟行为管理，开发和测试时难以验证通知流程
- 没有失败处理和重试机制，无法测试异常场景
- 无法模拟服务延迟、网络错误等真实场景

## 2. Goals

1. 为推送、短信、电话、邮件四个通知渠道实现完整的模拟行为
2. 实现统一的通知状态管理（成功、失败、重试）
3. 提供可配置的模拟行为（成功率、延迟等）
4. 为未来集成真实SDK预留清晰的扩展点
5. 确保所有通知渠道有完整的单元测试覆盖
6. 保持与现有代码框架的向后兼容性

## 3. User Stories

### US-001: 实现推送通知模拟器
**Description:** 作为开发者，我希望有一个完整的推送通知模拟器，以便开发和测试时能模拟推送服务的各种行为（成功、失败、重试）。

**Acceptance Criteria:**
- PushNotificationSimulator类继承自NotificationSimulator基类
- 实现send()方法，支持配置化的成功/失败行为
- 记录详细的推送日志（用户ID、标题、内容、状态）
- 支持模拟推送延迟（可配置延迟时间）
- 支持模拟推送失败（可配置失败率）
- 模拟批量推送场景
- 单元测试覆盖：成功、失败、延迟、批量场景

### US-002: 实现短信通知模拟器
**Description:** 作为开发者，我希望有一个完整的短信通知模拟器，以便开发和测试时能模拟短信服务的各种行为。

**Acceptance Criteria:**
- SMSNotificationSimulator类继承自NotificationSimulator基类
- 实现send()方法，支持配置化的成功/失败行为
- 记录详细的短信日志（手机号、模板、内容、状态）
- 支持模拟短信发送延迟
- 支持模拟短信发送失败（网络错误、余额不足等）
- 支持模拟模板变量替换
- 单元测试覆盖：成功、失败、延迟、模板替换场景

### US-003: 实现电话通知模拟器
**Description:** 作为开发者，我希望有一个完整的电话通知模拟器，以便开发和测试时能模拟语音通知的各种行为。

**Acceptance Criteria:**
- PhoneNotificationSimulator类继承自NotificationSimulator基类
- 实现call()方法，支持配置化的成功/失败行为
- 记录详细的电话日志（手机号、通话时长、状态）
- 支持模拟电话接通和未接通
- 支持模拟网络错误和忙线
- 支持模拟语音播报内容
- 单元测试覆盖：接通、未接通、错误场景

### US-004: 实现邮件通知模拟器
**Description:** 作为开发者，我希望有一个完整的邮件通知模拟器，以便开发和测试时能模拟邮件发送的各种行为。

**Acceptance Criteria:**
- EmailNotificationSimulator类继承自NotificationSimulator基类
- 实现send()方法，支持配置化的成功/失败行为
- 记录详细的邮件日志（收件人、主题、内容、状态）
- 支持HTML和纯文本邮件格式
- 支持模拟邮件附件
- 支持模拟SMTP错误和发送失败
- 单元测试覆盖：成功、失败、HTML格式、附件场景

### US-005: 实现通知服务配置管理
**Description:** 作为开发者，我希望有统一的通知服务配置管理，以便方便地控制各个通知渠道的模拟行为。

**Acceptance Criteria:**
- NotificationServiceConfig类统一管理所有通知服务配置
- 支持从app/core/config.py读取配置
- 支持环境变量覆盖（NOTIFICATION_*）
- 配置项包括：启用状态、成功/失败率、延迟、重试次数
- 每个通知渠道可独立配置
- 单元测试覆盖：配置加载、环境变量覆盖、默认值

### US-006: 集成模拟器到现有通知服务
**Description:** 作为开发者，我希望将四个通知模拟器集成到现有的NotificationService中，以便无缝替换当前的模拟日志。

**Acceptance Criteria:**
- 修改NotificationService的__init__方法，初始化所有模拟器
- 更新_send_push_notification()调用PushNotificationSimulator
- 更新_send_sms_notification()调用SMSNotificationSimulator
- 更新_send_phone_notification()调用PhoneNotificationSimulator
- 更新_send_email_notification()调用EmailNotificationSimulator
- 保持现有API不变，确保向后兼容
- 集成测试验证完整通知流程

### US-007: 实现通知重试机制
**Description:** 作为开发者，我希望通知发送失败时有自动重试机制，以便提高通知送达率。

**Acceptance Criteria:**
- NotificationSimulator基类实现重试逻辑
- 支持配置最大重试次数（默认3次）
- 支持配置重试间隔（默认1秒）
- 只对特定错误重试（如网络错误），业务错误不重试
- 超过重试次数后标记为FAILED
- 记录每次重试的日志
- 单元测试覆盖：重试成功、重试失败、超过重试次数场景

### US-008: 实现通知降级策略
**Description:** 作为开发者，我希望某个通知渠道失败时能自动尝试其他渠道，以便提高通知送达率。

**Acceptance Criteria:**
- 实现通知渠道优先级策略（电话 > 短信 > 推送 > 邮件）
- 支持配置降级策略（启用/禁用）
- 渠道失败时自动尝试下一优先级渠道
- 记录降级日志（从渠道A切换到渠道B）
- 不重复发送已成功的通知
- 单元测试覆盖：单渠道失败、多渠道降级场景

### US-009: 编写通知服务完整测试套件
**Description:** 作为开发者，我希望有完整的测试套件覆盖通知服务的各种场景，以便确保代码质量。

**Acceptance Criteria:**
- tests/test_notification_simulators.py测试所有模拟器
- tests/test_notification_service_integration.py测试完整集成
- 测试覆盖率达到80%以上
- 包含单元测试和集成测试
- 测试数据使用Mock对象，不依赖真实数据库
- 所有测试通过
- 测试报告生成覆盖率报告

## 4. Functional Requirements

1. **模拟器基类要求**
   - NotificationSimulator提供统一的模拟接口
   - 定义send()抽象方法供子类实现
   - 实现重试机制配置和执行
   - 实现延迟模拟（time.sleep）
   - 实现日志记录接口

2. **推送通知模拟器要求**
   - 支持单个和批量推送
   - 模拟推送平台响应（成功token、失败原因）
   - 支持自定义推送标题和内容
   - 支持点击动作模拟

3. **短信通知模拟器要求**
   - 支持单个和批量短信
   - 模拟短信平台响应（状态码、消息ID）
   - 支持短信模板和变量替换
   - 支持长短信分割模拟

4. **电话通知模拟器要求**
   - 模拟语音通话行为
   - 支持自动语音播报
   - 模拟通话时长和挂断
   - 支持忙音和无人接听

5. **邮件通知模拟器要求**
   - 支持纯文本和HTML格式
   - 支持多收件人
   - 支持附件模拟
   - 模拟SMTP协议响应

6. **配置管理要求**
   - 统一的配置接口
   - 支持环境变量覆盖
   - 配置验证（失败率0-100%，延迟>=0）
   - 默认配置合理

7. **集成要求**
   - 保持现有API签名不变
   - 保持数据库表结构不变
   - 保持日志格式一致
   - 不影响现有功能

8. **测试要求**
   - 所有新代码有单元测试
   - 所有模拟器有独立测试文件
   - 测试覆盖正常、异常、边界场景
   - 使用pytest框架
   - 测试数据与生产隔离（使用Mock）

## 5. Non-Goals

**不在本PRD范围内：**
1. 集成真实的第三方SDK（极光推送、阿里云短信、Twilio等）
2. 实现真实的网络请求
3. 实现真实的消息队列或异步任务
4. 实现通知送达回调和状态跟踪
5. 实现推送令牌（token）管理
6. 实现短信签名和模板审核
7. 实现邮件模板渲染引擎（如Jinja2）
8. 修改现有的数据库表结构
9. 实现通知消息去重机制
10. 实现通知发送限流和防刷

## 6. Design Considerations

### UI/UX Requirements
- 本PRD不涉及UI修改，保持现有UI不变

### Reusable Existing Components
- 复用现有的NotificationService框架
- 复用现有的Notification模型和NotificationStatus枚举
- 复用现有的日志系统（logger）
- 复用现有的配置系统（app/core/config.py）

### Architecture Decisions
1. **模拟器架构：** 采用基类+子类的继承模式，便于统一管理和扩展
2. **配置模式：** 使用app/core/config.py的Settings模式，支持环境变量
3. **单例模式：** NotificationService保持单例，模拟器在初始化时创建
4. **策略模式：** 重试和降级策略可配置，便于灵活调整
5. **工厂模式：** 通知渠道选择使用策略模式，便于新增渠道

## 7. Technical Considerations

### Known Constraints
- 使用Python 3.9+
- 使用FastAPI框架
- 使用SQLAlchemy ORM
- 使用pytest测试框架
- 不依赖第三方SDK，仅模拟实现

### Dependencies
- 现有依赖：FastAPI, SQLAlchemy, pydantic, pytest
- 新增依赖：无（仅使用标准库）

### Performance Requirements
- 模拟延迟可配置，默认0秒（开发环境）
- 批量通知支持，最多1000个用户
- 重试机制不影响主流程性能

### Security Considerations
- 日志不记录敏感信息（如完整手机号、密码）
- 环境变量用于配置，不在代码中硬编码
- 测试数据使用Mock，避免生产数据泄露

### Testing Considerations
- 单元测试使用pytest.Mock，隔离依赖
- 集成测试使用测试数据库（test.db）
- 测试数据使用Factory模式生成
- 测试覆盖率目标：80%以上

## 8. Success Metrics

### 代码质量指标
- 所有新增代码有单元测试覆盖
- 测试覆盖率达到80%以上
- 无linter错误和警告
- 所有测试通过

### 功能完整性指标
- 四个通知模拟器全部实现
- 重试机制正常运行
- 降级策略正常工作
- 配置系统完整覆盖

### 向后兼容性指标
- 现有API签名不变
- 现有测试不破坏
- 现有功能不受影响
- 无需修改数据库迁移

## 9. Open Questions

1. 模拟延迟的默认值应该设置为多少？（建议：0秒开发环境，1秒测试环境）
2. 模拟失败率的默认值应该设置为多少？（建议：0%开发环境，5%测试环境）
3. 重试机制的默认最大次数？（建议：3次）
4. 降级策略是否默认启用？（建议：启用，提高送达率）
5. 日志详细程度如何控制？（建议：使用现有的LOG_LEVEL配置）
