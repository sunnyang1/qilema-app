# 起了吗App 部署优化补充 PRD

## 1. 概述

### 1.1 优化目标
补充架构优化重构中的部署相关改进，优化Coze环境下的部署体验，提升可维护性、可靠性和可观测性。

### 1.2 当前部署问题分析
1. **Nginx配置缺失** - docker-compose.yml引用了nginx但实际配置文件不存在
2. **多环境配置混乱** - 缺乏明确的dev/staging/prod配置分离
3. **日志格式不统一** - 缺乏结构化日志，难以解析和分析
4. **资源无限制** - 容器可能导致资源耗尽
5. **缺乏CI/CD** - 没有自动化部署流程
6. **监控缺失** - 无Prometheus metrics端点
7. **配置验证不足** - 启动前没有配置完整性检查
8. **备份策略缺失** - 数据库无自动备份

### 1.3 成功标准
- 完整的Nginx配置文件
- 三套环境配置（dev/staging/prod）
- 结构化日志输出（JSON格式）
- 容器资源限制配置
- CI/CD自动化流程
- Prometheus metrics端点
- 配置验证脚本
- 数据库自动备份

---

## 2. 部署优化目标

### DG-001: 完整Nginx配置 ✅
**描述**: 创建完整的Nginx反向代理配置，包括HTTP和HTTPS支持

**验收标准**:
- [ ] 创建nginx/nginx.conf主配置文件
- [ ] 创建nginx/conf.d/backend.conf后端代理配置
- [ ] 支持HTTP到HTTPS重定向
- [ ] 支持静态文件缓存
- [ ] 支持请求体大小限制
- [ ] 支持超时配置

### DG-002: 多环境配置管理 ✅
**描述**: 创建dev/staging/prod三套环境配置

**验收标准**:
- [ ] 创建config.dev.yaml开发环境配置
- [ ] 创建config.staging.yaml测试环境配置
- [ ] 创建config.prod.yaml生产环境配置
- [ ] 创建.env.dev开发环境变量
- [ ] 创建.env.staging测试环境变量
- [ ] 创建.env.prod生产环境变量
- [ ] 更新docker-compose.yml支持多环境

### DG-003: 结构化日志输出 ✅
**描述**: 统一日志格式为JSON结构化日志

**验收标准**:
- [ ] 创建logging配置文件
- [ ] 日志格式统一为JSON
- [ ] 包含timestamp、level、message、request_id等字段
- [ ] 支持日志轮转
- [ ] 敏感信息自动脱敏

### DG-004: 容器资源限制 ✅
**描述**: 为所有容器配置CPU和内存限制

**验收标准**:
- [ ] backend容器配置资源限制（2核CPU, 2GB内存）
- [ ] postgres容器配置资源限制（1核CPU, 1GB内存）
- [ ] redis容器配置资源限制（512MB内存）
- [ ] 配置重启策略
- [ ] 配置健康检查依赖

### DG-005: CI/CD工作流 ✅
**描述**: 创建GitHub Actions自动化部署流程

**验收标准**:
- [ ] 创建.github/workflows/test.yml测试流程
- [ ] 创建.github/workflows/build.yml构建流程
- [ ] 创建.github/workflows/deploy.yml部署流程
- [ ] 支持多环境部署
- [ ] 包含自动化测试
- [ ] 包含安全扫描

### DG-006: Prometheus监控端点 ✅
**描述**: 添加Prometheus metrics端点

**验收标准**:
- [ ] 安装prometheus-client库
- [ ] 创建/metrics端点
- [ ] 记录HTTP请求指标
- [ ] 记录数据库连接指标
- [ ] 记录缓存命中率指标
- [ ] 记录业务指标（签到数、SOS数等）

### DG-007: 配置验证脚本 ✅
**描述**: 创建启动前配置验证脚本

**验收标准**:
- [ ] 创建scripts/validate_config.py验证脚本
- [ ] 验证必需环境变量
- [ ] 验证数据库连接
- [ ] 验证Redis连接
- [ ] 验证SECRET_KEY强度
- [ ] 验证ENCRYPTION_KEY存在
- [ ] 集成到Docker启动流程

### DG-008: 数据库备份策略 ✅
**描述**: 创建数据库自动备份方案

**验收标准**:
- [ ] 创建scripts/backup_db.sh备份脚本
- [ ] 配置定时备份（每天凌晨2点）
- [ ] 备份保留7天
- [ ] 支持备份到对象存储
- [ ] 创建恢复脚本
- [ ] 添加备份验证

### DG-009: 一键部署脚本 ✅
**描述**: 创建便捷的部署脚本

**验收标准**:
- [ ] 创建scripts/deploy.sh部署脚本
- [ ] 支持选择环境（dev/staging/prod）
- [ ] 自动检查依赖
- [ ] 自动拉取最新代码
- [ ] 自动启动服务
- [ ] 提供回滚功能

### DG-010: 容器健康检查增强 ✅
**描述**: 增强健康检查逻辑

**验收标准**:
- [ ] 检查数据库连接
- [ ] 检查Redis连接
- [ ] 检查磁盘空间
- [ ] 检查内存使用率
- [ ] 返回详细的健康状态

---

## 3. 功能需求

### FR-DG-001: Nginx配置文件
```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

```nginx
# nginx/conf.d/backend.conf
upstream backend {
    server backend:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name localhost;

    # 请求体大小限制
    client_max_body_size 10M;

    # 超时配置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # 静态文件缓存
    location /static/ {
        alias /app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $http_x_request_id;
    }

    # 健康检查
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

### FR-DG-002: 多环境配置
```yaml
# config.dev.yaml
environment: development
debug: true
database:
  url: postgresql://qilema:qilema_password@postgres:5432/qilema_dev
redis:
  url: redis://redis:6379/0
logging:
  level: DEBUG
  format: json
cors:
  origins: http://localhost:3000,http://localhost:5173
```

```yaml
# config.prod.yaml
environment: production
debug: false
database:
  url: postgresql://qilema:${DB_PASSWORD}@postgres:5432/qilema_prod
  pool_size: 20
  max_overflow: 10
redis:
  url: redis://${REDIS_PASSWORD}@redis:6379/0
logging:
  level: INFO
  format: json
cors:
  origins: https://app.qilema.com
```

### FR-DG-003: 结构化日志
```python
# app/core/logging_config.py
import logging
import logging.config
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加request_id（如果存在）
        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        # 添加异常信息（如果存在）
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'INFO',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}
```

### FR-DG-006: Prometheus Metrics
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# HTTP请求指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# 数据库指标
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

# 缓存指标
cache_hits = Counter('cache_hits_total', 'Cache hits', ['key_prefix'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['key_prefix'])

# 业务指标
checkins_total = Counter('checkins_total', 'Total checkins', ['status'])
sos_requests_total = Counter('sos_requests_total', 'SOS requests', ['status'])

# 获取metrics端点
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## 4. 实施计划

### Phase 1: 基础设施部署（1天）
- DG-001: 创建Nginx配置文件
- DG-002: 多环境配置管理
- DG-004: 容器资源限制

### Phase 2: 可观测性（1天）
- DG-003: 结构化日志输出
- DG-006: Prometheus监控端点
- DG-010: 容器健康检查增强

### Phase 3: 自动化（1天）
- DG-005: CI/CD工作流
- DG-009: 一键部署脚本

### Phase 4: 稳定性（1天）
- DG-007: 配置验证脚本
- DG-008: 数据库备份策略

**总计**: 10个用户故事，预计4天完成
