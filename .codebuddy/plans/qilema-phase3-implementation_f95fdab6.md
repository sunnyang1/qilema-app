---
name: qilema-phase3-implementation
overview: 基于PRD v1.1，完成Phase 2剩余功能和Phase 3完整功能，实现从"被动通知"到"主动救援"的核心价值。
todos:
  - id: phase2-notification-push
    content: 接入极光推送/Firebase实现真实APP推送通知
    status: completed
  - id: phase2-notification-sms
    content: 接入阿里云短信服务替换SMS模拟器
    status: completed
  - id: phase2-notification-phone
    content: 接入阿里云语音服务实现真实电话通知
    status: completed
  - id: phase2-notification-email
    content: 接入SendGrid邮件服务替换Email模拟器
    status: completed
  - id: phase3-knowledge-base
    content: 实现急救知识库基础功能（文章管理、分类、API）
    status: completed
  - id: phase3-aed-map
    content: 扩展急救资源模块，增加AED设备地图和导航功能
    status: completed
  - id: phase3-medication
    content: 开发用药提醒功能（用药计划、定时提醒、服用记录）
    status: completed
  - id: phase3-health-report
    content: 实现健康数据趋势分析报告功能
    status: completed
  - id: arch-refactor-services
    content: 完成剩余服务重构（NotificationService、AnomalyService等继承BaseService）
    status: completed
  - id: test-integration
    content: 编写第三方服务集成测试
    status: completed
    dependencies:
      - phase2-notification-push
      - phase2-notification-sms
      - phase2-notification-phone
      - phase2-notification-email
---

## 产品概述

基于PRD v1.1的下一步实施计划，聚焦于完成Phase 2剩余功能（真实第三方服务接入）和启动Phase 3核心功能开发。

## 当前状态

- Phase 1（MVP）已完成：用户系统、签到、SOS、联系人、健康档案
- Phase 2大部分完成：设备绑定、急救资源、通知基础框架
- 服务层重构完成：6个核心服务继承BaseService，427个测试通过
- 测试覆盖率：85%+

## 核心需求

1. **Phase 2 收尾**：将通知模拟器替换为真实第三方服务（极光推送、阿里云短信/语音、SendGrid邮件）
2. **Phase 3 启动**：实现急救知识库、AED地图、用药提醒等高价值功能
3. **架构完善**：完成剩余服务的BaseService重构（NotificationService、AnomalyService等）

## 技术栈

- **后端**：Python 3.11+ + FastAPI 0.104+
- **数据库**：PostgreSQL 15+ / SQLite（开发）
- **缓存**：Redis 7+
- **第三方服务**：极光推送(JPush)、Firebase、阿里云短信/语音、SendGrid邮件
- **测试**：pytest + pytest-cov

## 架构设计

### 通知服务架构

```mermaid
graph TD
    A[NotificationService] --> B[渠道适配器层]
    B --> C[PushAdapter]
    B --> D[SMSAdapter]
    B --> E[PhoneAdapter]
    B --> F[EmailAdapter]
    C --> G[极光推送/Firebase]
    D --> H[阿里云短信]
    E --> I[阿里云语音]
    F --> J[SendGrid]
```

### 急救知识库架构

```mermaid
graph TD
    A[KnowledgeBaseService] --> B[内容管理]
    A --> C[分类标签]
    A --> D[搜索索引]
    B --> E[文章/图文/视频]
    C --> F[急救/疾病/用药]
    D --> G[Elasticsearch/MeiliSearch]
```

### 用药提醒架构

```mermaid
graph TD
    A[MedicationService] --> B[用药计划]
    A --> C[提醒调度]
    A --> D[服用记录]
    B --> E[剂量/频率/周期]
    C --> F[Celery定时任务]
    D --> G[依从性统计]
```

## 实施策略

### Phase 2 收尾策略

1. **适配器模式**：为每种通知渠道创建适配器接口，保持与现有模拟器相同的API
2. **配置驱动**：通过环境变量切换模拟器/真实服务，支持灰度发布
3. **熔断降级**：真实服务失败时自动降级到模拟器或备用渠道

### Phase 3 启动策略

1. **急救知识库**：先实现基础CRUD和分类，再接入搜索
2. **AED地图**：复用现有emergency_resource架构，扩展AED专用字段
3. **用药提醒**：基于Celery定时任务，与通知服务集成