"""
高负载测试 - 验证熔断器和重试机制在高负载下的表现
"""

import gc
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

import pytest
from app.models.notification_model import Notification
from app.services.notification_service import NotificationService
from conftest import TEST_CONFIG


class TestHighLoadPerformance:
    """高负载性能测试"""

    def test_concurrent_notifications_with_circuit_breaker(self):
        """测试并发通知请求下的熔断器性能"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 10
        # 使用配置文件中的超时时间
        test_timeout = TEST_CONFIG["timeout"]["integration_test"]

        # 创建模拟的通知对象
        notifications = [
            Notification(
                user_id=f"user_{i}",
                title=f"Test {i}",
                content=f"Content {i}",
                channel="push",
                retry_count=0,
            )
            for i in range(50)
        ]

        # 模拟前10次成功，后40次失败
        with patch.object(
            service,
            "_try_send_by_channel",
            side_effect=[{"success": True}] * 10
            + [{"success": False, "error": "Fail"}] * 40,
        ):
            with patch.object(service, "_mark_notification_sent"):
                with patch.object(service, "_mark_notification_failed"):
                    # 并发发送50个通知
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        futures = [
                            executor.submit(
                                service._send_notification_directly,
                                notification,
                                "push",
                            )
                            for notification in notifications
                        ]

                        # 等待所有任务完成
                        for future in as_completed(futures):
                            try:
                                future.result(timeout=test_timeout)
                            except Exception as e:
                                pass

        # 验证熔断器已打开
        assert service._check_circuit_breaker("push") is False

        # 验证失败计数正确
        assert service._circuit_breaker_failures.get("push", 0) >= 10

    def test_retry_performance_under_load(self):
        """测试高负载下的重试性能"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 100  # 提高阈值以避免熔断

        # 创建100个通知对象
        notifications = [
            Notification(
                user_id=f"user_{i}",
                title=f"Test {i}",
                content=f"Content {i}",
                channel="push",
                retry_count=0,
            )
            for i in range(100)
        ]

        # 模拟所有请求都需要重试
        call_count = [0]

        def mock_try_send(notification, channel):
            call_count[0] += 1
            # 前50次返回失败，后50次返回成功
            if call_count[0] <= 50:
                return {"success": False, "error": "Fail"}
            else:
                return {"success": True}

        # 使用配置文件中的超时时间
        test_timeout = TEST_CONFIG["timeout"]["stress_test"]

        with patch.object(service, "_try_send_by_channel", mock_try_send):
            with patch.object(service, "_mark_notification_sent"):
                with patch.object(service, "_mark_notification_failed"):
                    start_time = time.time()

                    # 并发发送100个通知
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        futures = [
                            executor.submit(
                                service._send_notification_directly,
                                notification,
                                "push",
                            )
                            for notification in notifications
                        ]

                        # 等待所有任务完成
                        for future in as_completed(futures):
                            try:
                                future.result(timeout=test_timeout)
                            except Exception as e:
                                pass

                    end_time = time.time()
                    duration = end_time - start_time

        # 验证性能：100个请求在超时时间内完成
        assert duration < test_timeout, f"耗时 {duration:.2f} 秒，超过预期 {test_timeout} 秒"

    def test_circuit_breaker_recovery_under_load(self):
        """测试高负载下熔断器恢复性能"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 5
        # 使用配置文件中的超时时间
        test_timeout = 1  # 可以根据需要调整为 TEST_CONFIG["timeout"]["unit_test"]

        # 创建20个通知对象
        notifications = [
            Notification(
                user_id=f"user_{i}",
                title=f"Test {i}",
                content=f"Content {i}",
                channel="push",
                retry_count=0,
            )
            for i in range(20)
        ]

        # 阶段1：触发熔断器（前5次失败）
        with patch.object(
            service,
            "_try_send_by_channel",
            return_value={"success": False, "error": "Fail"},
        ):
            with patch.object(service, "_mark_notification_failed"):
                for i in range(5):
                    try:
                        service._send_notification_directly(notifications[i], "push")
                    except Exception:
                        pass

        # 验证熔断器已打开
        assert service._check_circuit_breaker("push") is False

        # 等待熔断器恢复（额外加0.5秒以确保时间充足）
        time.sleep(test_timeout + 0.5)

        # 验证熔断器已恢复
        assert service._check_circuit_breaker("push") is True

        # 阶段2：熔断器恢复后继续发送
        success_count = [0]

        def mock_try_send_after_recovery(notification, channel):
            success_count[0] += 1
            return {"success": True}

        with patch.object(
            service, "_try_send_by_channel", mock_try_send_after_recovery
        ):
            with patch.object(service, "_mark_notification_sent"):
                for i in range(5, 10):
                    service._send_notification_directly(notifications[i], "push")

        # 验证熔断器恢复后可以正常发送
        assert success_count[0] == 5

    def test_exponential_backoff_performance(self):
        """测试指数退退在高负载下的性能"""
        service = NotificationService()
        service.CIRCUIT_BREAKER_THRESHOLD = 100

        # 创建10个需要重试的通知
        notifications = [
            Notification(
                user_id=f"user_{i}",
                title=f"Test {i}",
                content=f"Content {i}",
                channel="push",
                retry_count=0,
            )
            for i in range(10)
        ]

        # 模拟所有请求都需要重试2次
        call_count = [0]

        def mock_try_send(notification, channel):
            call_count[0] += 1
            # 每个请求前2次失败，第3次成功
            if call_count[0] % 3 != 0:
                return {"success": False, "error": "Fail"}
            else:
                return {"success": True}

        with patch.object(service, "_try_send_by_channel", mock_try_send):
            with patch.object(service, "_mark_notification_sent"):
                with patch.object(service, "_mark_notification_failed"):
                    start_time = time.time()

                    # 顺序发送10个通知
                    for notification in notifications:
                        try:
                            service._send_notification_directly(notification, "push")
                        except Exception as e:
                            pass

                    end_time = time.time()
                    duration = end_time - start_time

        # 验证性能：10个请求（每个重试2次）应该在合理时间内完成
        # 预期大约 10 * (0 + 1 + 2) = 30秒（最后一次成功不需要等待）
        # 我们设置一个宽松的阈值：35秒
        assert duration < 35, f"耗时 {duration:.2f} 秒，超过预期"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
