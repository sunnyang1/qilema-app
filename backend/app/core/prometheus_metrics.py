"""
Prometheus 监控指标

提供 Prometheus 格式的监控指标端点
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response
import time

# 创建路由
router = APIRouter()

# HTTP 请求指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# 数据库连接指标
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Number of idle database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# Redis 连接指标
redis_connections_active = Gauge(
    'redis_connections_active',
    'Number of active Redis connections'
)

redis_cache_hits = Counter(
    'redis_cache_hits',
    'Total Redis cache hits',
    ['key_pattern']
)

redis_cache_misses = Counter(
    'redis_cache_misses',
    'Total Redis cache misses',
    ['key_pattern']
)

redis_cache_hit_ratio = Gauge(
    'redis_cache_hit_ratio',
    'Redis cache hit ratio',
    ['key_pattern']
)

# 业务指标
checkin_requests_total = Counter(
    'checkin_requests_total',
    'Total check-in requests',
    ['status']
)

sos_requests_total = Counter(
    'sos_requests_total',
    'Total SOS requests',
    ['status']
)

user_registrations_total = Counter(
    'user_registrations_total',
    'Total user registrations',
    ['status']
)

active_users_total = Gauge(
    'active_users_total',
    'Number of active users'
)

healthcheck_status = Gauge(
    'healthcheck_status',
    'Health check status',
    ['service']
)

# 系统资源指标
cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

memory_available_bytes = Gauge(
    'memory_available_bytes',
    'Available memory in bytes'
)

disk_usage_bytes = Gauge(
    'disk_usage_bytes',
    'Disk usage in bytes',
    ['mount_point']
)

# 应用信息
app_info = Info(
    'app_info',
    'Application information'
)


async def metrics():
    """
    Prometheus metrics 端点

    Returns:
        Response: Prometheus 格式的 metrics
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class HTTPRequestMetrics:
    """HTTP 请求指标记录器"""

    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time = time.time()

    def record(self, status: int):
        """记录请求指标"""
        duration = time.time() - self.start_time
        http_requests_total.labels(
            method=self.method,
            endpoint=self.endpoint,
            status=status
        ).inc()
        http_request_duration_seconds.labels(
            method=self.method,
            endpoint=self.endpoint
        ).observe(duration)


class DatabaseMetrics:
    """数据库指标记录器"""

    @staticmethod
    def update_connections(active: int, idle: int):
        """更新数据库连接指标"""
        db_connections_active.set(active)
        db_connections_idle.set(idle)

    @staticmethod
    def record_query(operation: str, duration: float):
        """记录数据库查询指标"""
        db_query_duration_seconds.labels(operation=operation).observe(duration)


class RedisMetrics:
    """Redis 指标记录器"""

    @staticmethod
    def record_hit(key_pattern: str):
        """记录缓存命中"""
        redis_cache_hits.labels(key_pattern=key_pattern).inc()
        RedisMetrics._update_hit_ratio(key_pattern)

    @staticmethod
    def record_miss(key_pattern: str):
        """记录缓存未命中"""
        redis_cache_misses.labels(key_pattern=key_pattern).inc()
        RedisMetrics._update_hit_ratio(key_pattern)

    @staticmethod
    def _update_hit_ratio(key_pattern: str):
        """更新缓存命中率"""
        hits = redis_cache_hits.labels(key_pattern=key_pattern)._value.get()
        misses = redis_cache_misses.labels(key_pattern=key_pattern)._value.get()
        total = hits + misses
        if total > 0:
            ratio = hits / total
            redis_cache_hit_ratio.labels(key_pattern=key_pattern).set(ratio)


class BusinessMetrics:
    """业务指标记录器"""

    @staticmethod
    def record_checkin(status: str):
        """记录签到指标"""
        checkin_requests_total.labels(status=status).inc()

    @staticmethod
    def record_sos(status: str):
        """记录 SOS 指标"""
        sos_requests_total.labels(status=status).inc()

    @staticmethod
    def record_user_registration(status: str):
        """记录用户注册指标"""
        user_registrations_total.labels(status=status).inc()

    @staticmethod
    def update_active_users(count: int):
        """更新活跃用户数"""
        active_users_total.set(count)

    @staticmethod
    def update_healthcheck(service: str, status: int):
        """更新健康检查状态"""
        healthcheck_status.labels(service=service).set(status)
