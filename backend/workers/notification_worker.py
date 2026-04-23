"""
通知 Worker

消费 Redis Streams 中的通知事件，并行发送短信/推送/电话。
SOS 触发后，API 立即返回 200，通知由 Worker 异步处理。
"""

import asyncio
import json
import logging
import os
import signal

from app.core.message_queue import MessageQueue

logger = logging.getLogger(__name__)

# Worker 标识
WORKER_ID = os.environ.get("WORKER_ID", "notification-worker-1")
CONSUMER_GROUP = "notification-workers"


class NotificationWorker:
    """通知发送 Worker

    消费 stream:notification 和 stream:sos，
    执行实际的通知发送操作（短信、推送、电话）。
    """

    def __init__(self, queue: MessageQueue):
        self.queue = queue
        self.running = False
        self._shutdown_event = asyncio.Event()

    async def run(self):
        """Worker 主循环"""
        self.running = True
        logger.info(f"通知 Worker 启动: {WORKER_ID}")

        # 注册信号处理
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(sig, self._signal_handler)

        # 确保 Consumer Group 存在
        await self.queue.ensure_consumer_group(
            MessageQueue.STREAM_NOTIFICATION, CONSUMER_GROUP
        )
        await self.queue.ensure_consumer_group(MessageQueue.STREAM_SOS, CONSUMER_GROUP)

        while self.running:
            try:
                # 消费 SOS Stream（高优先级）
                await self._consume_stream(MessageQueue.STREAM_SOS)

                # 消费通知 Stream
                await self._consume_stream(MessageQueue.STREAM_NOTIFICATION)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker 消费循环异常: {e}", exc_info=True)
                await asyncio.sleep(1)

        logger.info(f"通知 Worker 已停止: {WORKER_ID}")

    def _signal_handler(self):
        """信号处理：优雅关闭"""
        logger.info("收到关闭信号，正在优雅停止...")
        self.running = False
        self._shutdown_event.set()

    async def _consume_stream(self, stream: str):
        """消费指定 Stream 的消息"""
        messages = await self.queue.consume(
            stream=stream,
            group=CONSUMER_GROUP,
            consumer=WORKER_ID,
            count=10,
            block_ms=1000,
        )

        for stream_name, msgs in messages:
            for msg_id, fields in msgs:
                await self._process_message(stream, msg_id, fields)

    async def _process_message(self, stream: str, msg_id: bytes, fields: dict):
        """处理单条消息"""
        try:
            event_type = self._decode_field(fields.get(b"event_type", b""))
            payload = json.loads(self._decode_field(fields.get(b"payload", b"{}")))

            logger.info(f"处理事件: {event_type} (msg_id={msg_id})")

            if event_type == "sos.triggered":
                await self._handle_sos_triggered(payload)
            elif event_type == "checkin.overdue":
                await self._handle_checkin_overdue(payload)
            elif event_type == "notification.send":
                await self._handle_notification_send(payload)
            else:
                logger.warning(f"未知事件类型: {event_type}")

            # 确认消息已处理
            await self.queue.ack(stream, CONSUMER_GROUP, msg_id)
            logger.info(f"事件处理完成: {event_type}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}", exc_info=True)
            # 不 ACK，等待 PEL 超时后重试

    def _decode_field(self, value) -> str:
        """解码字段值"""
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    async def _handle_sos_triggered(self, payload: dict):
        """处理 SOS 触发事件

        并行发送：短信 + 推送 + 电话给紧急联系人
        """
        user_id = payload.get("user_id")
        sos_id = payload.get("sos_id")
        location = payload.get("location", {})

        logger.info(f"发送 SOS 通知: user_id={user_id}, sos_id={sos_id}")

        # TODO: Phase 3 完整实现时接入 NotificationService
        # 当前记录事件，实际发送逻辑在 Phase 3 扩展
        await asyncio.sleep(0.1)  # 模拟通知发送耗时

    async def _handle_checkin_overdue(self, payload: dict):
        """处理签到超期事件"""
        user_id = payload.get("user_id")
        last_checkin = payload.get("last_checkin")

        logger.info(f"发送签到超期通知: user_id={user_id}, last_checkin={last_checkin}")
        await asyncio.sleep(0.1)

    async def _handle_notification_send(self, payload: dict):
        """处理通用通知发送事件"""
        channel = payload.get("channel")
        recipient = payload.get("recipient")
        content = payload.get("content")

        logger.info(f"发送通知: channel={channel}, recipient={recipient}")
        await asyncio.sleep(0.05)


async def main():
    """Worker 入口函数"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    queue = MessageQueue()
    worker = NotificationWorker(queue)

    try:
        await worker.run()
    finally:
        await queue.close()


if __name__ == "__main__":
    asyncio.run(main())
