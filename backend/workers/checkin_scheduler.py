"""
签到超期检测 Scheduler

每分钟扫描超期未签到用户，发布告警事件到消息队列。
由通知 Worker 消费并发送提醒。
"""

import asyncio
import logging
import os
import signal
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.message_queue import MessageQueue

logger = logging.getLogger(__name__)

WORKER_ID = os.environ.get("WORKER_ID", "checkin-scheduler-1")
SCAN_INTERVAL_SECONDS = int(os.environ.get("CHECKIN_SCAN_INTERVAL", "60"))


class CheckInScheduler:
    """签到超期检测调度器

    定期扫描超期未签到用户，发布告警事件到 Redis Streams，
    由 NotificationWorker 异步消费并发送通知。
    """

    def __init__(self, queue: MessageQueue):
        self.queue = queue
        self.running = False

    async def run(self):
        """调度器主循环"""
        self.running = True
        logger.info(
            f"签到调度器启动: {WORKER_ID}, "
            f"扫描间隔: {SCAN_INTERVAL_SECONDS}s, "
            f"超期阈值: {settings.DEFAULT_CHECKIN_HOURS}h"
        )

        # 注册信号处理
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(sig, self._signal_handler)

        while self.running:
            try:
                await self._scan_and_alert()
            except Exception as e:
                logger.error(f"签到扫描失败: {e}", exc_info=True)

            # 等待下一次扫描
            for _ in range(SCAN_INTERVAL_SECONDS):
                if not self.running:
                    break
                await asyncio.sleep(1)

        logger.info(f"签到调度器已停止: {WORKER_ID}")

    def _signal_handler(self):
        """信号处理：优雅关闭"""
        logger.info("签到调度器收到关闭信号，正在停止...")
        self.running = False

    async def _scan_and_alert(self):
        """扫描超期用户并发布告警事件

        注意：当前为骨架实现，Phase 3 完整实现时需接入：
        - 异步数据库查询（AsyncSession）
        - 用户最后签到时间查询
        - 紧急联系人信息查询
        """
        threshold = datetime.utcnow() - timedelta(hours=settings.DEFAULT_CHECKIN_HOURS)
        logger.debug(f"扫描超期签到用户 (阈值: {threshold.isoformat()})")

        # TODO: Phase 3 完整实现时接入异步数据库查询
        # 伪代码：
        # async with AsyncSessionLocal() as db:
        #     repo = CheckInRepository(db)
        #     overdue_users = await repo.get_overdue_users(threshold)
        #     for user in overdue_users:
        #         await self.queue.publish(
        #             MessageQueue.STREAM_CHECKIN_ALERT,
        #             "checkin.overdue",
        #             {
        #                 "user_id": user.user_id,
        #                 "last_checkin_at": user.last_checkin_at.isoformat(),
        #                 "threshold_hours": settings.DEFAULT_CHECKIN_HOURS,
        #             },
        #         )

        # 当前阶段：记录扫描事件，数据库查询在 Phase 3 扩展
        logger.info("签到扫描完成（骨架实现，待接入数据库查询）")


async def main():
    """Scheduler 入口函数"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    queue = MessageQueue()
    scheduler = CheckInScheduler(queue)

    try:
        await scheduler.run()
    finally:
        await queue.close()


if __name__ == "__main__":
    asyncio.run(main())
