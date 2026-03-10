"""
熔断器服务

提供熔断器模式实现，防止服务雪崩
支持 Redis 持久化和线程安全
"""

import json
import logging
import threading
from datetime import datetime
from typing import Dict, Optional

from app.core.notification_simulators import NotificationServiceConfig

logger = logging.getLogger(__name__)


class CircuitBreakerService:
    """
    熔断器服务

    实现熔断器模式，防止服务雪崩：
    - 当某个渠道连续失败达到阈值时，熔断器开启，禁止发送
    - 超过熔断恢复时间后，熔断器关闭，允许重试
    - 支持 Redis 持久化，重启后状态不丢失
    - 线程安全

    使用示例:
        >>> circuit_breaker = CircuitBreakerService()
        >>> if circuit_breaker.check("sms"):
        ...     # 熔断器关闭，可以发送
        ...     result = send_sms()
        ...     if result.success:
        ...         circuit_breaker.record_success("sms")
        ...     else:
        ...         circuit_breaker.record_failure("sms")
        ... else:
        ...     # 熔断器开启，跳过发送
        ...     pass
    """

    def __init__(self, config: Optional[NotificationServiceConfig] = None):
        """
        初始化熔断器服务

        Args:
            config: 通知服务配置对象，如果为None则使用默认配置
        """
        self.config = config or NotificationServiceConfig()

        # 熔断器配置
        self.threshold = self.config.get_circuit_breaker_threshold()
        self.timeout = self.config.get_circuit_breaker_timeout()
        self.persist_enabled = self.config.is_circuit_breaker_persist_enabled()

        # 熔断器状态
        self._failures: Dict[str, int] = {}  # 每个渠道的连续失败计数
        self._last_failure: Dict[str, datetime] = {}  # 每个渠道的最后失败时间
        self._lock = threading.Lock()  # 熔断器状态的线程锁

        # 如果启用了持久化，尝试从 Redis 加载熔断器状态
        if self.persist_enabled:
            self._load_from_redis()

    def check(self, channel: str) -> bool:
        """
        检查熔断器状态（线程安全）

        Args:
            channel: 渠道标识

        Returns:
            bool: True 表示熔断器关闭（可以执行），False 表示熔断器开启（禁止执行）
        """
        channel_str = str(channel)

        with self._lock:
            # 检查是否达到熔断阈值
            if channel_str not in self._failures:
                return True

            failures = self._failures[channel_str]
            last_failure = self._last_failure.get(channel_str)

            # 如果失败次数超过阈值
            if failures >= self.threshold:
                # 检查是否超过熔断恢复时间
                time_since_failure = (datetime.utcnow() - last_failure).total_seconds()
                if time_since_failure < self.timeout:
                    logger.warning(
                        f"熔断器开启（渠道: {channel_str}），"
                        f"连续失败 {failures} 次，"
                        f"距离上次失败 {time_since_failure:.0f} 秒，"
                        f"还需等待 {self.timeout - time_since_failure:.0f} 秒"
                    )
                    return False
                else:
                    # 超过熔断恢复时间，重置熔断器
                    logger.info(f"熔断器恢复（渠道: {channel_str}）")
                    self._failures[channel_str] = 0

            return True

    def record_failure(self, channel: str) -> None:
        """
        记录失败（线程安全，支持持久化）

        Args:
            channel: 渠道标识
        """
        channel_str = str(channel)
        with self._lock:
            self._failures[channel_str] = self._failures.get(channel_str, 0) + 1
            self._last_failure[channel_str] = datetime.utcnow()
            logger.warning(
                f"熔断器记录失败（渠道: {channel_str}，" f"失败次数: {self._failures[channel_str]}）"
            )

            # 如果启用了持久化，保存到 Redis
            if self.persist_enabled:
                self._save_to_redis(channel_str)

    def record_success(self, channel: str) -> None:
        """
        记录成功（线程安全，支持持久化）

        Args:
            channel: 渠道标识
        """
        channel_str = str(channel)
        with self._lock:
            if channel_str in self._failures:
                self._failures[channel_str] = 0
                logger.info(f"熔断器重置（渠道: {channel_str}）")

                # 如果启用了持久化，清除 Redis 中的状态
                if self.persist_enabled:
                    self._clear_from_redis(channel_str)

    def get_state(self, channel: str) -> Dict[str, any]:
        """
        获取熔断器状态

        Args:
            channel: 渠道标识

        Returns:
            dict: 包含 failures、last_failure、is_open 的状态字典
        """
        channel_str = str(channel)
        with self._lock:
            failures = self._failures.get(channel_str, 0)
            last_failure = self._last_failure.get(channel_str)
            is_open = failures >= self.threshold and last_failure is not None

            if is_open:
                time_since_failure = (datetime.utcnow() - last_failure).total_seconds()
                is_open = time_since_failure < self.timeout

            return {
                "channel": channel_str,
                "failures": failures,
                "last_failure": last_failure.isoformat() if last_failure else None,
                "is_open": is_open,
                "threshold": self.threshold,
                "timeout": self.timeout,
            }

    def reset(self, channel: Optional[str] = None) -> None:
        """
        重置熔断器状态

        Args:
            channel: 渠道标识，如果为None则重置所有渠道
        """
        with self._lock:
            if channel:
                channel_str = str(channel)
                self._failures.pop(channel_str, None)
                self._last_failure.pop(channel_str, None)
                logger.info(f"熔断器手动重置（渠道: {channel_str}）")
                if self.persist_enabled:
                    self._clear_from_redis(channel_str)
            else:
                self._failures.clear()
                self._last_failure.clear()
                logger.info("熔断器手动重置（所有渠道）")
                if self.persist_enabled:
                    self._clear_all_from_redis()

    def _load_from_redis(self) -> None:
        """
        从 Redis 加载熔断器状态

        注意：这是一个可选功能，如果 Redis 不可用则静默失败
        """
        try:
            from app.core.redis import redis_manager

            redis_mgr = redis_manager

            if not redis_mgr.is_healthy():
                logger.warning("Redis 不可用，无法加载熔断器状态")
                return

            # 获取所有熔断器状态的 key
            pattern = "circuit_breaker:*"
            keys = redis_mgr.redis_client.keys(pattern)

            if not keys:
                return

            # 加载所有熔断器状态
            for key in keys:
                try:
                    data = redis_mgr.redis_client.get(key)
                    if data:
                        state = json.loads(data)
                        channel = key.decode("utf-8").replace("circuit_breaker:", "")
                        self._failures[channel] = state.get("failures", 0)
                        last_failure_time = state.get("last_failure_time")
                        if last_failure_time:
                            self._last_failure[channel] = datetime.fromisoformat(
                                last_failure_time
                            )
                except Exception as e:
                    logger.error(f"加载熔断器状态失败（key: {key}）：{str(e)}")
                    continue

            logger.info(f"从 Redis 加载了 {len(keys)} 个熔断器状态")
        except Exception as e:
            logger.warning(f"加载熔断器状态失败：{str(e)}")

    def _save_to_redis(self, channel: str) -> None:
        """
        保存熔断器状态到 Redis

        Args:
            channel: 渠道标识
        """
        try:
            from app.core.redis import redis_manager

            redis_mgr = redis_manager

            if not redis_mgr.is_healthy():
                return

            key = f"circuit_breaker:{channel}"
            state = {
                "failures": self._failures.get(channel, 0),
                "last_failure_time": None,
            }

            last_failure = self._last_failure.get(channel)
            if last_failure:
                state["last_failure_time"] = last_failure.isoformat()

            # 保存状态（设置过期时间为超时时间的 2 倍）
            expiry = self.timeout * 2
            redis_mgr.redis_client.setex(key, expiry, json.dumps(state))
        except Exception as e:
            logger.error(f"保存熔断器状态失败（channel: {channel}）：{str(e)}")

    def _clear_from_redis(self, channel: str) -> None:
        """
        清除 Redis 中的熔断器状态

        Args:
            channel: 渠道标识
        """
        try:
            from app.core.redis import redis_manager

            redis_mgr = redis_manager

            if not redis_mgr.is_healthy():
                return

            key = f"circuit_breaker:{channel}"
            redis_mgr.redis_client.delete(key)
        except Exception as e:
            logger.error(f"清除熔断器状态失败（channel: {channel}）：{str(e)}")

    def _clear_all_from_redis(self) -> None:
        """
        清除 Redis 中的所有熔断器状态
        """
        try:
            from app.core.redis import redis_manager

            redis_mgr = redis_manager

            if not redis_mgr.is_healthy():
                return

            pattern = "circuit_breaker:*"
            keys = redis_mgr.redis_client.keys(pattern)
            if keys:
                redis_mgr.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"清除所有熔断器状态失败：{str(e)}")
