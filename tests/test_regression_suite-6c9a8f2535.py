"""
回归测试 - 起了吗App历史功能验证

验证新代码不影响已有功能的正确性和稳定性
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.user import User
from app.models.user_setting import LoginRecord
from app.models.emergency_contact import EmergencyContact
from app.models.checkin import CheckIn
from app.models.alert import Alert
from app.models.sos_request import SOSRequest
from app.services.user_service import UserService
from app.services.emergency_contact_service import EmergencyContactService
from app.services.checkin_service import CheckInService
from app.services.alert_service import AlertService
from app.services.sos_service import SOSService


class TestRegressionSuite:
    """回归测试套件 - 历史功能验证"""

    def test_regression_user_login_stability(self, db_session, test_user):
        """回归测试: 用户登录稳定性"""
        user_service = UserService(db_session)

        # 多次登录验证稳定性
        for i in range(10):
            login_result = user_service.login(
                phone=test_user.phone,
                password="SecurePass123"
            )
            assert login_result["access_token"] is not None
            assert login_result["user_id"] == test_user.id

    def test_regression_emergency_contact_operations(self, db_session, test_user):
        """回归测试: 紧急联系人操作"""
        contact_service = EmergencyContactService(db_session)

        # 1. 添加联系人
        contact = contact_service.add_contact(
            user_id=test_user.id,
            name="回归测试联系人",
            phone="13900139888",
            relationship="朋友",
            priority=1
        )
        assert contact is not None

        # 2. 查询联系人
        contacts = contact_service.get_user_contacts(test_user.id)
        assert len(contacts) >= 1

        # 3. 更新联系人
        updated_contact = contact_service.update_contact(
            contact_id=contact.id,
            name="更新后的联系人"
        )
        assert updated_contact.name == "更新后的联系人"

        # 4. 删除联系人
        contact_service.delete_contact(contact.id)
        contacts = contact_service.get_user_contacts(test_user.id)
        # 验证删除后数量减少
        deleted_contact = db_session.query(EmergencyContact).filter(
            EmergencyContact.id == contact.id
        ).first()
        assert deleted_contact.is_deleted == True

    def test_regression_checkin_daily_limit(self, db_session, test_user):
        """回归测试: 每日签到限制"""
        checkin_service = CheckInService(db_session)

        # 1. 首次签到应该成功
        checkin1 = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin1 is not None
        assert checkin1.is_first_checkin == True

        # 2. 同天第二次签到应该失败
        checkin2 = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin2 is None

    def test_regression_alert_trigger_logic(self, db_session, test_user):
        """回归测试: 预警触发逻辑"""
        alert_service = AlertService(db_session)
        checkin_service = CheckInService(db_session)

        # 1. 设置预警阈值为24小时
        alert_setting = alert_service.create_alert_setting(
            user_id=test_user.id,
            alert_threshold_hours=24,
            notification_enabled=True
        )
        assert alert_setting is not None

        # 2. 模拟23小时前签到(不应该触发预警)
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        checkin.checkin_time = datetime.utcnow() - timedelta(hours=23)
        db_session.commit()

        alert = alert_service.check_user_alert(test_user.id)
        assert alert is None  # 23小时不应该触发预警

        # 3. 模拟25小时前签到(应该触发预警)
        checkin.checkin_time = datetime.utcnow() - timedelta(hours=25)
        db_session.commit()

        alert = alert_service.check_user_alert(test_user.id)
        assert alert is not None  # 25小时应该触发预警
        assert alert.is_active == True

    def test_regression_sos_status_transition(self, db_session, test_user):
        """回归测试: SOS状态转换"""
        sos_service = SOSService(db_session)

        # 1. 创建SOS(状态: 待救援)
        sos = sos_service.create_sos_request(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区",
            message="测试SOS"
        )
        assert sos.status == "PENDING"

        # 2. 更新状态为救援中
        updated_sos = sos_service.update_sos_status(
            sos_id=sos.id,
            status="RESCUING"
        )
        assert updated_sos.status == "RESCUING"

        # 3. 取消SOS
        cancelled_sos = sos_service.cancel_sos_request(
            sos_id=sos.id,
            user_id=test_user.id,
            reason="测试取消"
        )
        assert cancelled_sos is not None
        assert cancelled_sos.status == "CANCELLED"

    def test_regression_data_integrity(self, db_session, test_user):
        """回归测试: 数据完整性"""
        # 1. 创建紧急联系人
        contact_service = EmergencyContactService(db_session)
        contact = contact_service.add_contact(
            user_id=test_user.id,
            name="数据完整性测试",
            phone="13900139999",
            relationship="家人",
            priority=1
        )

        # 2. 验证外键约束
        assert contact.user_id == test_user.id
        assert contact.name == "数据完整性测试"

        # 3. 创建签到记录
        checkin_service = CheckInService(db_session)
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin.user_id == test_user.id

        # 4. 验证关联查询
        user_contacts = db_session.query(EmergencyContact).filter(
            EmergencyContact.user_id == test_user.id
        ).all()
        assert len(user_contacts) >= 1

        user_checkins = db_session.query(CheckIn).filter(
            CheckIn.user_id == test_user.id
        ).all()
        assert len(user_checkins) >= 1

    def test_regression_password_security(self, db_session, test_user):
        """回归测试: 密码安全"""
        user_service = UserService(db_session)

        # 1. 验证密码加密
        assert test_user.password_hash != "SecurePass123"

        # 2. 验证正确密码可以登录
        login_result = user_service.login(
            phone=test_user.phone,
            password="SecurePass123"
        )
        assert login_result["access_token"] is not None

        # 3. 验证错误密码无法登录
        login_result = user_service.login(
            phone=test_user.phone,
            password="WrongPassword"
        )
        assert login_result is None

        # 4. 修改密码
        updated_user = user_service.change_password(
            user_id=test_user.id,
            old_password="SecurePass123",
            new_password="NewPassword123"
        )
        assert updated_user is not None

        # 5. 验证新密码可以登录
        login_result = user_service.login(
            phone=test_user.phone,
            password="NewPassword123"
        )
        assert login_result["access_token"] is not None

    def test_regression_query_performance(self, db_session, test_user):
        """回归测试: 查询性能"""
        import time

        # 1. 批量创建签到记录
        checkin_service = CheckInService(db_session)
        for i in range(100):
            checkin_service.create_checkin(
                user_id=test_user.id,
                latitude=39.908823 + (i * 0.0001),
                longitude=116.397470 + (i * 0.0001),
                location=f"测试地点{i}"
            )

        # 2. 查询性能测试
        start_time = time.time()
        history = checkin_service.get_checkin_history(
            user_id=test_user.id,
            days=30
        )
        end_time = time.time()

        assert len(history) >= 100
        assert (end_time - start_time) < 1.0  # 查询应在1秒内完成

    def test_regression_concurrent_operations(self, db_session, test_user):
        """回归测试: 并发操作"""
        import threading

        def create_checkin(user_id):
            checkin_service = CheckInService(db_session)
            checkin_service.create_checkin(
                user_id=user_id,
                latitude=39.908823,
                longitude=116.397470,
                location="北京市朝阳区"
            )

        # 1. 模拟并发签到(只有一个应该成功)
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_checkin, args=(test_user.id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 2. 验证只有一个签到成功
        checkins = db_session.query(CheckIn).filter(
            CheckIn.user_id == test_user.id,
            CheckIn.checkin_date == datetime.utcnow().date()
        ).all()
        assert len(checkins) == 1

    def test_regression_notification_delivery(self, db_session, test_user):
        """回归测试: 通知投递"""
        from app.services.notification_service import NotificationService
        from app.models.notification import NotificationType

        notification_service = NotificationService(db_session)

        # 1. 发送多个通知
        for i in range(10):
            notification = notification_service.send_notification(
                user_id=test_user.id,
                notification_type=NotificationType.CHECKIN_REMINDER,
                title=f"测试通知{i}",
                content=f"测试内容{i}"
            )
            assert notification is not None

        # 2. 查询通知列表
        notifications = notification_service.get_user_notifications(test_user.id)
        assert len(notifications) >= 10

        # 3. 标记所有通知为已读
        for notification in notifications:
            notification_service.mark_as_read(notification.id)

        # 4. 验证未读数量为0
        unread_count = notification_service.get_unread_count(test_user.id)
        assert unread_count == 0

    def test_regression_alert_cooldown(self, db_session, test_user):
        """回归测试: 预警冷却机制"""
        alert_service = AlertService(db_session)
        checkin_service = CheckInService(db_session)

        # 1. 设置预警阈值
        alert_setting = alert_service.create_alert_setting(
            user_id=test_user.id,
            alert_threshold_hours=24,
            notification_enabled=True
        )

        # 2. 模拟25小时未签到,触发预警
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        checkin.checkin_time = datetime.utcnow() - timedelta(hours=25)
        db_session.commit()

        alert1 = alert_service.check_user_alert(test_user.id)
        assert alert1 is not None

        # 3. 再次检查(应该返回同一个预警,不重复触发)
        alert2 = alert_service.check_user_alert(test_user.id)
        assert alert2 is not None
        assert alert2.id == alert1.id  # 应该是同一个预警

        # 4. 签到后解除预警
        checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        alert_service.resolve_alert(alert1.id, reason="用户已签到")

    def test_regression_device_data_sync(self, db_session, test_user):
        """回归测试: 设备数据同步"""
        from app.services.device_service import DeviceService
        from app.models.device import DeviceStatus

        device_service = DeviceService(db_session)

        # 1. 绑定设备
        device = device_service.bind_device(
            user_id=test_user.id,
            device_name="回归测试设备",
            device_type="smartwatch",
            mac_address="00:1A:2B:3C:4D:6F"
        )
        assert device.status == DeviceStatus.ONLINE

        # 2. 同步设备数据
        for i in range(50):
            device_data = device_service.sync_device_data(
                device_id=device.id,
                data_type="heart_rate",
                value=70 + (i % 30),
                timestamp=datetime.utcnow()
            )
            assert device_data is not None

        # 3. 查询设备数据
        status = device_service.get_device_status(device.id)
        assert status is not None
        assert status["status"] == DeviceStatus.ONLINE

    def test_regression_anomaly_detection_accuracy(self, db_session, test_user):
        """回归测试: 异常检测准确性"""
        from app.services.anomaly_service import AnomalyService
        from app.services.device_service import DeviceService

        device_service = DeviceService(db_session)
        anomaly_service = AnomalyService(db_session)

        # 1. 绑定设备
        device = device_service.bind_device(
            user_id=test_user.id,
            device_name="异常检测测试设备",
            device_type="smartwatch",
            mac_address="00:1A:2B:3C:4D:7F"
        )

        # 2. 正常心率(不应该触发异常)
        for i in range(100):
            anomaly = anomaly_service.detect_heart_rate_anomaly(
                device_id=device.id,
                user_id=test_user.id,
                heart_rate=70,
                timestamp=datetime.utcnow()
            )
            assert anomaly is None

        # 3. 异常心率(应该触发异常)
        anomaly = anomaly_service.detect_heart_rate_anomaly(
            device_id=device.id,
            user_id=test_user.id,
            heart_rate=180,
            timestamp=datetime.utcnow()
        )
        assert anomaly is not None

    def test_regression_health_record_encryption(self, db_session, test_user):
        """回归测试: 健康档案加密"""
        from app.services.health_record_service import HealthRecordService

        health_service = HealthRecordService(db_session)

        # 1. 创建健康档案
        health_record = health_service.create_health_record(
            user_id=test_user.id,
            blood_type="A",
            height=175,
            weight=70,
            allergies="青霉素"
        )
        assert health_record.is_encrypted == True

        # 2. 添加病史
        medical_record = health_service.add_medical_record(
            health_record_id=health_record.id,
            disease="高血压",
            diagnosis_date="2020-01-01",
            treatment_status="持续治疗中"
        )
        assert medical_record is not None

        # 3. 生成摘要
        summary = health_service.generate_summary(health_record.id)
        assert summary is not None
        assert "高血压" in summary

    def test_regression_emergency_resource_search(self, db_session):
        """回归测试: 急救资源搜索"""
        from app.services.emergency_resource_service import EmergencyResourceService
        from app.models.emergency_resource import ResourceType

        resource_service = EmergencyResourceService(db_session)

        # 1. 添加多个急救资源
        for i in range(20):
            resource = resource_service.add_resource(
                name=f"测试医院{i}",
                resource_type=ResourceType.HOSPITAL,
                latitude=39.908823 + (i * 0.001),
                longitude=116.397470 + (i * 0.001),
                address=f"测试地址{i}",
                phone=f"010-1234{i:04d}"
            )
            assert resource is not None

        # 2. 搜索周边资源
        resources = resource_service.search_nearby_resources(
            latitude=39.908823,
            longitude=116.397470,
            radius=5000
        )
        assert len(resources) >= 20

    def test_regression_120_integration_stability(self, db_session, test_user):
        """回归测试: 120对接稳定性"""
        from app.services.emergency_center_service import EmergencyCenterService

        center_service = EmergencyCenterService(db_session)

        # 1. 添加急救中心
        center = center_service.add_center(
            name="测试急救中心",
            phone="120",
            address="测试地址"
        )
        assert center is not None

        # 2. 创建急救呼叫
        call = center_service.create_emergency_call(
            user_id=test_user.id,
            center_id=center.id,
            health_record_id=None,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert call is not None

        # 3. 追踪救护车
        ambulance_location = center_service.track_ambulance(
            call_id=call.id,
            ambulance_latitude=39.918823,
            ambulance_longitude=116.407470
        )
        assert ambulance_location is not None


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
        nickname="回归测试用户",
        gender="male",
        birth_date="1990-01-01"
    )
    return user
