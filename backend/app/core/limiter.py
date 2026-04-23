"""
API 限流配置 (Phase 5)

差异化限流策略：
- 认证端点：严格限流，防暴力破解
- SOS 端点：宽松限流，紧急场景
- 普通查询：标准限流
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# 全局限流器实例
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# 预定义限流策略
STRICT_LIMIT = "5/minute"  # 认证端点：登录、注册
SOS_LIMIT = "10/minute"  # SOS 端点：紧急求助
STANDARD_LIMIT = "200/minute"  # 普通查询
ADMIN_LIMIT = "500/minute"  # 管理端点
