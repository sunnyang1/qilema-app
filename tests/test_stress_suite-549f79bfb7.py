"""
压力测试 - 起了吗App性能与稳定性测试

测试系统在高并发、大数据量下的性能表现
"""

import pytest
import sys
import os
import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.user import User
from app.models.checkin import CheckIn
from app.models.alert import Alert
from app.models.sos_request import SOSRequest
from app.models.notification import Notification
from app.services.user_service import UserService
from app.services.checkin_service import CheckInService
from app.services.alert_service import AlertService
from app.services.sos_service import SOSService
from app.services.notification_service import NotificationService


class TestStressSuite:
    """压力测试套件 - 性能与稳定性"""

    def test_stress_concurrent_user_registration(self, db_session):
        """压力测试: 并发用户注册"""
        user_service = UserService(db_session)

        def register_user(index):
            try:
                user = user_service.register_user(
                    phone=f"138{index:09d}",
                    password="SecurePass123",
                    verification_code="123456",
                    nickname=f"压力测试用户{index}",
                    gender="male",
                    birth_date="1990-01-01"
                )
                return user is not None
            except Exception as e:
                return False

        # 100个并发用户注册
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_user, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate > 0.95  # 成功率应大于95%

    def test_stress_concurrent_checkins(self, db_session, test_user):
        """压力测试: 并发签到"""
        checkin_service = CheckInService(db_session)

        def create_checkin(index):
            try:
                checkin = checkin_service.create_checkin(
                    user_id=test_user.id,
                    latitude=39.908823 + (index * 0.0001),
                    longitude=116.397470 + (index * 0.0001),
                    location=f"北京市朝阳区{index}"
                )
                return checkin is not None
            except Exception as e:
                return False

        # 50个并发签到请求(只有第一个应该成功)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_checkin, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]

        success_count = sum(results)
        assert success_count == 1  # 只有第一次签到应该成功

    def test_stress_bulk_checkin_operations(self, db_session, test_users):
        """压力测试: 批量签到操作"""
        checkin_service = CheckInService(db_session)

        start_time = time.time()

        # 1000次签到操作
        for i, user in enumerate(test_users):
            checkin = checkin_service.create_checkin(
                user_id=user.id,
                latitude=39.908823 + (i * 0.0001),
                longitude=116.397470 + (i * 0.0001),
                location=f"北京市朝阳区{i}"
            )
            assert checkin is not None

        end_time = time.time()
        duration = end_time - start_time

        # 1000次签到应在30秒内完成
        assert duration < 30.0
        print(f"1000次签到耗时: {duration:.2f}秒")

    def test_stress_concurrent_sos_requests(self, db_session, test_users):
        """压力测试: 并发SOS请求"""
        sos_service = SOSService(db_session)

        def create_sos(index, user):
            try:
                sos = sos_service.create_sos_request(
                    user_id=user.id,
                    latitude=39.908823 + (index * 0.0001),
                    longitude=116.397470 + (index * 0.0001),
                    location=f"北京市朝阳区{index}",
                    message=f"测试SOS{index}"
                )
                return sos is not None
            except Exception as e:
                return False

        # 50个并发SOS请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_sos, i, test_users[i]) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate > 0.95  # 成功率应大于95%

    def test_stress_bulk_notification_delivery(self, db_session, test_users):
        """压力测试: 批量通知投递"""
        notification_service = NotificationService(db_session)

        start_time = time.time()

        # 1000条通知
        for i, user in enumerate(test_users):
            notification = notification_service.send_notification(
                user_id=user.id,
                notification_type="CHECKIN_REMINDER",
                title=f"测试通知{i}",
                content=f"测试内容{i}"
            )
            assert notification is not None

        end_time = time.time()
        duration = end_time - start_time

        # 1000条通知应在20秒内完成
        assert duration < 20.0
        print(f"1000条通知投递耗时: {duration:.2f}秒")

    def test_stress_concurrent_notification_queries(self, db_session, test_users):
        """压力测试: 并发通知查询"""
        notification_service = NotificationService(db_session)

        # 先创建500条通知
        for i, user in enumerate(test_users[:10]):
            for j in range(50):
                notification = notification_service.send_notification(
                    user_id=user.id,
                    notification_type="SYSTEM_MESSAGE",
                    title=f"测试通知{i}_{j}",
                    content=f"测试内容{i}_{j}"
                )

        def query_notifications(user):
            try:
                notifications = notification_service.get_user_notifications(user.id)
                return len(notifications)
            except Exception as e:
                return 0

        # 50个并发查询请求
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(query_notifications, test_users[i]) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        duration = end_time - start_time

        # 50个查询应在5秒内完成
        assert duration < 5.0
        print(f"50个并发查询耗时: {duration:.2f}秒")

    def test_stress_alert_detection_performance(self, db_session, test_users):
        """压力测试: 预警检测性能"""
        alert_service = AlertService(db_session)
        checkin_service = CheckInService(db_session)

        # 为100个用户设置预警阈值
        for user in test_users[:100]:
            alert_setting = alert_service.create_alert_setting(
                user_id=user.id,
                alert_threshold_hours=24,
                notification_enabled=True
            )

        # 模拟25小时前签到
        for user in test_users[:100]:
            checkin = checkin_service.create_checkin(
                user_id=user.id,
                latitude=39.908823,
                longitude=116.397470,
                location="北京市朝阳区"
            )
            checkin.checkin_time = datetime.utcnow() - timedelta(hours=25)
            db_session.commit()

        # 批量检测预警
        start_time = time.time()
        for user in test_users[:100]:
            alert = alert_service.check_user_alert(user.id)
            assert alert is not None

        end_time = time.time()
        duration = end_time - start_time

        # 100次预警检测应在10秒内完成
        assert duration < 10.0
        print(f"100次预警检测耗时: {duration:.2f}秒")

    def test_stress_large_dataset_query(self, db_session, test_user):
        """压力测试: 大数据集查询"""
        checkin_service = CheckInService(db_session)

        # 创建10000条签到记录
        print("正在创建10000条签到记录...")
        start_time = time.time()
        for i in range(10000):
            checkin = checkin_service.create_checkin(
                user_id=test_user.id,
                latitude=39.908823 + (i * 0.000001),
                longitude=116.397470 + (i * 0.000001),
                location=f"北京市朝阳区{i}"
            )
        end_time = time.time()
        create_duration = end_time - start_time
        print(f"创建10000条记录耗时: {create_duration:.2f}秒")

        # 查询历史记录
        start_time = time.time()
        history = checkin_service.get_checkin_history(
            user_id=test_user.id,
            days=30
        )
        end_time = time.time()
        query_duration = end_time - start_time

        # 查询应在2秒内完成
        assert query_duration < 2.0
        print(f"查询10000条记录耗时: {query_duration:.2f}秒")

    def test_stress_concurrent_database_operations(self, db_session, test_users):
        """压力测试: 并发数据库操作"""
        def perform_database_operations(index, user):
            try:
                checkin_service = CheckInService(db_session)
                alert_service = AlertService(db_session)

                # 签到
                checkin = checkin_service.create_checkin(
                    user_id=user.id,
                    latitude=39.908823,
                    longitude=116.397470,
                    location="北京市朝阳区"
                )

                # 设置预警
                alert_setting = alert_service.create_alert_setting(
                    user_id=user.id,
                    alert_threshold_hours=24,
                    notification_enabled=True
                )

                # 检测预警
                alert = alert_service.check_user_alert(user.id)

                return checkin is not None and alert_setting is not None
            except Exception as e:
                return False

        # 100个并发数据库操作
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(perform_database_operations, i, test_users[i]) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        duration = end_time - start_time

        success_rate = sum(results) / len(results)
        assert success_rate > 0.95  # 成功率应大于95%
        assert duration < 30.0  # 应在30秒内完成
        print(f"100个并发操作耗时: {duration:.2f}秒")

    def test_stress_api_response_time(self, db_session, test_user):
        """压力测试: API响应时间"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 登录获取token
        response = client.post(
            "/api/v1/users/login",
            json={"phone": test_user.phone, "password": "SecurePass123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 测试API响应时间
        api_tests = [
            ("GET", f"/api/v1/users/{test_user.id}", {}),
            ("GET", f"/api/v1/checkins/user/{test_user.id}/history?days=7", {}),
            ("GET", f"/api/v1/notifications/user/{test_user.id}", {}),
        ]

        for method, url, data in api_tests:
            start_time = time.time()
            if method == "GET":
                response = client.get(url, headers=headers)
            elif method == "POST":
                response = client.post(url, json=data, headers=headers)

            end_time = time.time()
            response_time = end_time - start_time

            # API响应时间应小于1秒
            assert response.status_code == 200
            assert response_time < 1.0
            print(f"{method} {url} 响应时间: {response_time:.3f}秒")

    def test_stress_memory_usage(self, db_session, test_user):
        """压力测试: 内存使用"""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 执行大量操作
        checkin_service = CheckInService(db_session)
        for i in range(1000):
            checkin = checkin_service.create_checkin(
                user_id=test_user.id,
                latitude=39.908823 + (i * 0.0001),
                longitude=116.397470 + (i * 0.0001),
                location=f"北京市朝阳区{i}"
            )

        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 内存增长应小于100MB
        assert memory_increase < 100
        print(f"内存增长: {memory_increase:.2f}MB")

    def test_stress_long_running_stability(self, db_session, test_users):
        """压力测试: 长时间运行稳定性"""
        checkin_service = CheckInService(db_session)

        start_time = time.time()
        iterations = 0

        # 持续运行10分钟
        while time.time() - start_time < 600:
            for user in test_users[:10]:
                checkin = checkin_service.create_checkin(
                    user_id=user.id,
                    latitude=39.908823,
                    longitude=116.397470,
                    location="北京市朝阳区"
                )
            iterations += 1

        duration = time.time() - start_time
        print(f"10分钟内完成 {iterations} 轮签到")
        assert iterations >= 10

    def test_stress_connection_pool(self, db_session, test_users):
        """压力测试: 数据库连接池"""
        def query_user_data(user):
            try:
                checkin_service = CheckInService(db_session)
                history = checkin_service.get_checkin_history(user_id=user.id, days=7)
                return len(history)
            except Exception as e:
                return 0

        # 200个并发数据库查询
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(query_user_data, user) for user in test_users[:200]]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()
        duration = end_time - start_time

        # 200个查询应在10秒内完成
        assert duration < 10.0
        print(f"200个并发查询耗时: {duration:.2f}秒")

    def test_stress_transaction_isolation(self, db_session, test_users):
        """压力测试: 事务隔离"""
        def update_user_preference(index, user):
            try:
                from app.services.user_setting_service import UserSettingService
                setting_service = UserSettingService(db_session)

                setting = setting_service.create_user_setting(
                    user_id=user.id,
                    language="zh_CN",
                    region="CN",
                    theme="light"
                )

                # 模拟并发更新
                updated_setting = setting_service.update_language(
                    setting_id=setting.id,
                    language="en_US"
                )

                return updated_setting is not None
            except Exception as e:
                return False

        # 50个并发更新
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(update_user_preference, i, test_users[i]) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]

        success_rate = sum(results) / len(results)
        assert success_rate > 0.95  # 成功率应大于95%

    def test_stress_cache_performance(self, db_session, test_user):
        """压力测试: 缓存性能"""
        checkin_service = CheckInService(db_session)

        # 首次查询(无缓存)
        start_time = time.time()
        history1 = checkin_service.get_checkin_history(user_id=test_user.id, days=7)
        first_query_time = time.time() - start_time

        # 后续查询(有缓存)
        start_time = time.time()
        history2 = checkin_service.get_checkin_history(user_id=test_user.id, days=7)
        cached_query_time = time.time() - start_time

        print(f"首次查询耗时: {first_query_time:.3f}秒")
        print(f"缓存查询耗时: {cached_query_time:.3f}秒")

        # 缓存查询应该更快
        assert cached_query_time <= first_query_time

    def test_stress_error_handling(self, db_session, test_user):
        """压力测试: 错误处理"""
        def create_invalid_checkin(index):
            try:
                checkin_service = CheckInService(db_session)
                # 尝试使用无效用户ID
                checkin = checkin_service.create_checkin(
                    user_id=999999,
                    latitude=39.908823,
                    longitude=116.397470,
                    location="北京市朝阳区"
                )
                return checkin is None  # 应该返回None
            except Exception as e:
                return True  # 捕获异常也是正确的

        # 100个错误请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_invalid_checkin, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]

        # 所有请求都应该正确处理错误
        assert all(results)

    def test_stress_resource_cleanup(self, db_session, test_user):
        """压力测试: 资源清理"""
        checkin_service = CheckInService(db_session)

        # 创建大量数据
        for i in range(1000):
            checkin = checkin_service.create_checkin(
                user_id=test_user.id,
                latitude=39.908823 + (i * 0.0001),
                longitude=116.397470 + (i * 0.0001),
                location=f"北京市朝阳区{i}"
            )

        # 验证数据库连接正常
        history = checkin_service.get_checkin_history(user_id=test_user.id, days=30)
        assert len(history) >= 1000


# Pytest fixtures
@pytest.fixture
def db_session():
    """数据库会话fixture"""
    from app.core.database import get_db_session
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db_session):
    """测试用户fixture"""
    user_service = UserService(db_session)
    user = user_service.register_user(
        phone="13800138001",
        password="SecurePass123",
        verification_code="123456",
        nickname="压力测试用户",
        gender="male",
        birth_date="1990-01-01"
    )
    return user


@pytest.fixture
def test_users(db_session):
    """批量测试用户fixture"""
    user_service = UserService(db_session)
    users = []
    for i in range(200):
        user = user_service.register_user(
            phone=f"139{i:09d}",
            password="SecurePass123",
            verification_code="123456",
            nickname=f"压力测试用户{i}",
            gender="male" if i % 2 == 0 else "female",
            birth_date="1990-01-01"
        )
        users.append(user)
    return users
