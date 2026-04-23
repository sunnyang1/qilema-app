"""
Redis Streams 消息队列

基于已有 Redis 基础设施，提供事件发布/消费能力。
使用 Consumer Group 保证 at-least-once 语义。
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class MessageQueue:
    """Redis Streams 消息队列

    利用已有 Redis 基础设施，无需引入新组件。
    支持事件发布、消费和确认（ACK）。
    """

    # Stream 名称常量
    STREAM_SOS = "stream:sos"
    STREAM_NOTIFICATION = "stream:notification"
    STREAM_CHECKIN_ALERT = "stream:checkin_alert"
    STREAM_REPORT_GENERATION = "stream:report_generation"

    def __init__(self, redis: Optional[Redis] = None):
        """初始化消息队列

        Args:
            redis: Redis 异步客户端，如果为 None 则自动创建
        """
        self._redis = redis
        self._local_redis = redis is None

    @property
    async def redis(self) -> Redis:
        """获取 Redis 客户端（懒加载）"""
        if self._redis is None:
            self._redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,
            )
        return self._redis

    async def publish(
        self,
        stream: str,
        event_type: str,
        payload: Dict[str, Any],
        maxlen: int = 10000,
    ) -> str:
        """发布事件到 Stream

        Args:
            stream: Stream 名称
            event_type: 事件类型
            payload: 事件载荷
            maxlen: 最大保留消息数

        Returns:
            消息 ID
        """
        client = await self.redis
        message_id = await client.xadd(
            stream,
            {
                "event_type": event_type,
                "payload": json.dumps(payload, default=str),
                "timestamp": int(asyncio.get_event_loop().time() * 1000),
            },
            maxlen=maxlen,
        )
        logger.info(f"事件已发布: {event_type} -> {stream} (id={message_id})")
        return message_id

    async def ensure_consumer_group(
        self, stream: str, group: str, mkstream: bool = True
    ) -> bool:
        """确保 Consumer Group 存在

        Args:
            stream: Stream 名称
            group: Consumer Group 名称
            mkstream: 不存在时自动创建 Stream

        Returns:
            是否成功创建/确认
        """
        client = await self.redis
        try:
            await client.xgroup_create(stream, group, id="0", mkstream=mkstream)
            logger.info(f"Consumer Group 创建成功: {group} -> {stream}")
            return True
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.debug(f"Consumer Group 已存在: {group}")
                return True
            logger.error(f"创建 Consumer Group 失败: {e}")
            return False

    async def consume(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block_ms: int = 2000,
    ) -> list:
        """消费 Stream 消息（Consumer Group 模式）

        Args:
            stream: Stream 名称
            group: Consumer Group 名称
            consumer: Consumer 名称
            count: 每次读取消息数
            block_ms: 阻塞等待时间（毫秒）

        Returns:
            消息列表，格式: [(stream_name, [(msg_id, fields), ...]), ...]
        """
        client = await self.redis
        messages = await client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=count,
            block=block_ms,
        )
        return messages or []

    async def ack(self, stream: str, group: str, message_id: str) -> bool:
        """确认消息已处理

        Args:
            stream: Stream 名称
            group: Consumer Group 名称
            message_id: 消息 ID

        Returns:
            是否成功确认
        """
        client = await self.redis
        try:
            await client.xack(stream, group, message_id)
            return True
        except Exception as e:
            logger.error(f"ACK 消息失败: {message_id} -> {e}")
            return False

    async def pending_info(self, stream: str, group: str) -> dict:
        """获取待处理消息信息

        Args:
            stream: Stream 名称
            group: Consumer Group 名称

        Returns:
            待处理消息统计
        """
        client = await self.redis
        return await client.xpending(stream, group)

    async def get_backlog(self, stream: str, group: str) -> int:
        """获取消息队列积压数量

        Args:
            stream: Stream 名称
            group: Consumer Group 名称

        Returns:
            积压消息数
        """
        info = await self.pending_info(stream, group)
        return info.get("pending", 0)

    async def close(self):
        """关闭 Redis 连接"""
        if self._redis and self._local_redis:
            await self._redis.close()
            self._redis = None
