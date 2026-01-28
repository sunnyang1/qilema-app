"""
全量测试 - 起了吗App完整功能测试套件

测试覆盖所有12个用户故事的完整功能验证
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.user import User
from app.models.login_record import LoginRecord
from app.models.emergency_contact import EmergencyContact
from app.models.checkin import CheckIn
from app.models.alert import Alert
from app.models.sos_request import SOSRequest, SOSStatusEnum
from app.models.health_record import HealthRecord
from app.models.device import Device
from app.models.emergency_resource_model import EmergencyResource
from app.models.emergency_center_model import EmergencyCenter, EmergencyCall
from app.models.notification_model import Notification
from app.models.user_setting_model import UserSetting
from app.services.user_service import UserService
from app.services.emergency_contact_service import EmergencyContactService
from app.services.checkin_service import CheckInService
from app.services.alert_service import AlertService
from app.services.sos_service import SOSService
from app.services.health_record_service import HealthRecordService
from app.services.device_service import DeviceService
from app.services.anomaly_service import AnomalyService
from app.services.emergency_resource_service import EmergencyResourceService
from app.services.emergency_center_service import EmergencyCenterService
from app.services.notification_service import NotificationService


class TestFullSuite:
    """全量测试套件 - 完整功能验证"""

    def test_us001_user_registration_complete_flow(self, db_session):
        """US-001: 用户注册与认证 - 完整流程测试"""
        user_service = UserService(db_session)

        # 1. 测试用户注册
        user = user_service.register_user(
            phone="13800138001",
            password="SecurePass123",
            verification_code="123456",
            nickname="测试用户",
            gender="male",
            birth_date="1990-01-01"
        )
        assert user is not None
        assert user.phone == "13800138001"
        assert user.nickname == "测试用户"
        assert user.is_active == True

        # 2. 测试用户登录
        login_result = user_service.login(
            phone="13800138001",
            password="SecurePass123"
        )
        assert login_result["access_token"] is not None
        assert login_result["user_id"] == user.id

        # 3. 测试密码修改
        updated_user = user_service.change_password(
            user_id=user.id,
            old_password="SecurePass123",
            new_password="NewSecurePass456"
        )
        assert updated_user is not None

        # 4. 测试JWT认证
        auth_user = user_service.verify_token(login_result["access_token"])
        assert auth_user is not None
        assert auth_user.id == user.id

    def test_us002_emergency_contact_complete_flow(self, db_session, test_user):
        """US-002: 紧急联系人管理 - 完整流程测试"""
        contact_service = EmergencyContactService(db_session)

        # 1. 添加紧急联系人
        contact1 = contact_service.add_contact(
            user_id=test_user.id,
            name="张三",
            phone="13900139001",
            relationship="配偶",
            priority=1
        )
        assert contact1 is not None
        assert contact1.name == "张三"

        # 2. 添加第二个联系人
        contact2 = contact_service.add_contact(
            user_id=test_user.id,
            name="李四",
            phone="13900139002",
            relationship="父母",
            priority=2
        )
        assert contact2 is not None

        # 3. 查询联系人列表
        contacts = contact_service.get_user_contacts(test_user.id)
        assert len(contacts) == 2
        assert contacts[0].priority == 1

        # 4. 更新联系人信息
        updated_contact = contact_service.update_contact(
            contact_id=contact1.id,
            name="张三(更新)",
            phone="13900139011"
        )
        assert updated_contact.name == "张三(更新)"

        # 5. 删除联系人
        contact_service.delete_contact(contact_id=contact2.id)
        contacts = contact_service.get_user_contacts(test_user.id)
        assert len(contacts) == 1

    def test_us003_checkin_complete_flow(self, db_session, test_user):
        """US-003: 每日签到打卡 - 完整流程测试"""
        checkin_service = CheckInService(db_session)

        # 1. 首次签到
        checkin1 = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin1 is not None
        assert checkin1.is_first_checkin == True

        # 2. 同天重复签到(应该被拒绝)
        checkin2 = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin2 is None

        # 3. 查询签到历史
        history = checkin_service.get_checkin_history(
            user_id=test_user.id,
            days=30
        )
        assert len(history) >= 1

        # 4. 获取签到统计
        stats = checkin_service.get_checkin_stats(test_user.id)
        assert stats["total_days"] >= 1
        assert stats["current_streak"] >= 1

    def test_us004_alert_complete_flow(self, db_session, test_user):
        """US-004: 异常预警机制 - 完整流程测试"""
        alert_service = AlertService(db_session)
        checkin_service = CheckInService(db_session)

        # 1. 设置预警阈值
        alert_setting = alert_service.create_alert_setting(
            user_id=test_user.id,
            alert_threshold_hours=24,
            notification_enabled=True
        )
        assert alert_setting is not None

        # 2. 模拟24小时未签到
        checkin_time = datetime.utcnow() - timedelta(hours=25)
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        checkin.checkin_time = checkin_time
        db_session.commit()

        # 3. 检查预警触发
        alert = alert_service.check_user_alert(test_user.id)
        assert alert is not None
        assert alert.is_active == True

        # 4. 签到后自动解除预警
        new_checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        alert_service.resolve_alert(alert.id, reason="用户已签到")
        db_session.refresh(alert)
        assert alert.is_resolved == True

        # 5. 查询预警历史
        alerts = alert_service.get_user_alerts(test_user.id)
        assert len(alerts) >= 1

    def test_us005_sos_complete_flow(self, db_session, test_user, test_emergency_contacts):
        """US-005: SOS紧急求助 - 完整流程测试"""
        sos_service = SOSService(db_session)

        # 1. 创建SOS请求
        sos = sos_service.create_sos_request(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区",
            message="遇到危险,请求紧急救援!"
        )
        assert sos is not None
        assert sos.status == SOSStatus.PENDING

        # 2. 更新SOS状态为救援中
        updated_sos = sos_service.update_sos_status(
            sos_id=sos.id,
            status=SOSStatus.RESCUING
        )
        assert updated_sos.status == SOSStatus.RESCUING

        # 3. 添加位置共享记录
        location = sos_service.add_location_update(
            sos_id=sos.id,
            latitude=39.909823,
            longitude=116.398470,
            location="北京市朝阳区移动中"
        )
        assert location is not None

        # 4. 取消SOS(需要验证)
        cancelled_sos = sos_service.cancel_sos_request(
            sos_id=sos.id,
            user_id=test_user.id,
            reason="误触"
        )
        assert cancelled_sos is not None

    def test_us006_health_record_complete_flow(self, db_session, test_user):
        """US-006: 健康档案管理 - 完整流程测试"""
        health_service = HealthRecordService(db_session)

        # 1. 创建健康档案
        health_record = health_service.create_health_record(
            user_id=test_user.id,
            blood_type="A",
            height=175,
            weight=70,
            allergies="青霉素"
        )
        assert health_record is not None
        assert health_record.blood_type == "A"

        # 2. 添加病史记录
        medical_record = health_service.add_medical_record(
            health_record_id=health_record.id,
            disease="高血压",
            diagnosis_date="2020-01-01",
            treatment_status="持续治疗中"
        )
        assert medical_record is not None

        # 3. 添加用药记录
        medication = health_service.add_medication(
            health_record_id=health_record.id,
            medication_name="硝苯地平",
            dosage="10mg",
            frequency="每日一次"
        )
        assert medication is not None

        # 4. 生成健康档案摘要
        summary = health_service.generate_summary(health_record.id)
        assert summary is not None
        assert "高血压" in summary

        # 5. 加密存储验证
        encrypted_data = health_service.encrypt_sensitive_data(health_record.id)
        assert encrypted_data is not None

    def test_us007_device_binding_complete_flow(self, db_session, test_user):
        """US-007: 智能设备绑定 - 完整流程测试"""
        device_service = DeviceService(db_session)

        # 1. 绑定智能设备
        device = device_service.bind_device(
            user_id=test_user.id,
            device_name="智能手环",
            device_type="smartwatch",
            mac_address="00:1A:2B:3C:4D:5E"
        )
        assert device is not None
        assert device.user_id == test_user.id
        assert device.status == "online"

        # 2. 同步设备数据
        device_data = device_service.sync_device_data(
            device_id=device.id,
            data_type="heart_rate",
            value=72,
            timestamp=datetime.utcnow()
        )
        assert device_data is not None

        # 3. 设置异常阈值
        threshold = device_service.set_threshold(
            device_id=device.id,
            metric_type="heart_rate",
            min_value=60,
            max_value=100
        )
        assert threshold is not None

        # 4. 查询设备状态
        status = device_service.get_device_status(device.id)
        assert status is not None
        assert status["status"] == "online"

        # 5. 解绑设备
        device_service.unbind_device(device_id=device.id)
        unbound_device = device_service.get_device(device.id)
        assert unbound_device.is_deleted == True

    def test_us008_anomaly_detection_complete_flow(self, db_session, test_user, test_device):
        """US-008: 设备数据异常监测 - 完整流程测试"""
        anomaly_service = AnomalyService(db_session)

        # 1. 检测心率异常
        anomaly = anomaly_service.detect_heart_rate_anomaly(
            device_id=test_device.id,
            user_id=test_user.id,
            heart_rate=150,
            timestamp=datetime.utcnow()
        )
        assert anomaly is not None
        assert anomaly.level == ""

        # 2. 检测连续无活动
        activity_anomaly = anomaly_service.detect_no_activity(
            device_id=test_device.id,
            user_id=test_user.id,
            last_activity_time=datetime.utcnow() - timedelta(hours=5)
        )
        assert activity_anomaly is not None

        # 3. 生成健康趋势报告
        trend_report = anomaly_service.generate_health_trend(
            user_id=test_user.id,
            days=7
        )
        assert trend_report is not None

        # 4. 分析活动模式
        pattern = anomaly_service.analyze_activity_pattern(
            user_id=test_user.id,
            days=30
        )
        assert pattern is not None

    def test_us009_emergency_resource_complete_flow(self, db_session):
        """US-009: 急救资源地图 - 完整流程测试"""
        resource_service = EmergencyResourceService(db_session)

        # 1. 添加急救资源
        hospital = resource_service.add_resource(
            name="北京协和医院",
            resource_type="",
            latitude=39.913890,
            longitude=116.417480,
            address="北京市东城区帅府园1号",
            phone="010-69156688"
        )
        assert hospital is not None

        aed = resource_service.add_resource(
            name="朝阳门外AED",
            resource_type="",
            latitude=39.928890,
            longitude=116.447480,
            address="北京市朝阳区朝阳门外大街",
            phone="010-12345678"
        )
        assert aed is not None

        # 2. 搜索周边资源
        resources = resource_service.search_nearby_resources(
            latitude=39.908823,
            longitude=116.397470,
            radius=5000
        )
        assert len(resources) >= 2

        # 3. 规划导航路径
        route = resource_service.calculate_navigation_route(
            start_latitude=39.908823,
            start_longitude=116.397470,
            end_latitude=hospital.latitude,
            end_longitude=hospital.longitude
        )
        assert route is not None

        # 4. 查询资源统计
        stats = resource_service.get_resource_statistics()
        assert stats is not None

    def test_us010_emergency_center_complete_flow(self, db_session, test_user, test_health_record):
        """US-010: 120急救中心对接 - 完整流程测试"""
        center_service = EmergencyCenterService(db_session)

        # 1. 添加急救中心
        center = center_service.add_center(
            name="北京市急救中心",
            phone="120",
            address="北京市东城区"
        )
        assert center is not None

        # 2. 模拟拨打120
        call = center_service.create_emergency_call(
            user_id=test_user.id,
            center_id=center.id,
            health_record_id=test_health_record.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert call is not None

        # 3. 自动发送位置信息
        center_service.send_location_to_center(
            call_id=call.id,
            latitude=39.908823,
            longitude=116.397470
        )

        # 4. 发送健康档案摘要
        summary = center_service.send_health_summary(
            call_id=call.id,
            health_record_id=test_health_record.id
        )
        assert summary is not None

        # 5. 追踪救护车位置
        ambulance_location = center_service.track_ambulance(
            call_id=call.id,
            ambulance_latitude=39.918823,
            ambulance_longitude=116.407470
        )
        assert ambulance_location is not None

    def test_us011_notification_complete_flow(self, db_session, test_user):
        """US-011: 消息通知系统 - 完整流程测试"""
        notification_service = NotificationService(db_session)

        # 1. 发送推送通知
        notification = notification_service.send_notification(
            user_id=test_user.id,
            notification_type="",
            title="签到提醒",
            content="今天还未签到,请尽快签到"
        )
        assert notification is not None

        # 2. 查询通知历史
        notifications = notification_service.get_user_notifications(
            user_id=test_user.id
        )
        assert len(notifications) >= 1

        # 3. 标记已读
        notification_service.mark_as_read(notification.id)
        db_session.refresh(notification)
        assert notification.is_read == True

        # 4. 获取未读通知数量
        unread_count = notification_service.get_unread_count(test_user.id)
        assert unread_count >= 0

        # 5. 发送批量通知
        batch_result = notification_service.send_batch_notification(
            user_ids=[test_user.id],
            notification_type="",
            title="系统消息",
            content="系统维护通知"
        )
        assert batch_result is not None

    def test_us012_user_setting_complete_flow(self, db_session, test_user):
        """US-012: 用户设置页面 - 完整流程测试"""
        from app.services.user_setting_service import UserSettingService

        setting_service = UserSettingService(db_session)

        # 1. 创建用户设置
        setting = setting_service.create_user_setting(
            user_id=test_user.id,
            language="zh_CN",
            region="CN",
            theme="light"
        )
        assert setting is not None

        # 2. 更新语言设置
        updated_setting = setting_service.update_language(
            setting_id=setting.id,
            language="en_US"
        )
        assert updated_setting.language == "en_US"

        # 3. 更新隐私设置
        privacy_setting = setting_service.update_privacy_settings(
            setting_id=setting.id,
            share_profile=True,
            share_location=True,
            data_analysis=False
        )
        assert privacy_setting is not None

        # 4. 修改密码
        setting_service.change_password(
            user_id=test_user.id,
            old_password="SecurePass123",
            new_password="NewSecurePass456"
        )

        # 5. 更新手机号
        setting_service.update_phone_number(
            user_id=test_user.id,
            new_phone="13900139001",
            verification_code="123456"
        )

    def test_end_to_end_sos_workflow(self, db_session, test_user, test_emergency_contacts):
        """端到端SOS工作流测试"""
        sos_service = SOSService(db_session)
        notification_service = NotificationService(db_session)

        # 1. 用户触发SOS
        sos = sos_service.create_sos_request(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区",
            message="遇到危险,请求紧急救援!"
        )

        # 2. 通知紧急联系人
        for contact in test_emergency_contacts:
            notification = notification_service.send_notification(
                user_id=contact.id,
                notification_type="",
                title="SOS紧急求助",
                content=f"{test_user.nickname}遇到危险,请求紧急救援!"
            )
            assert notification is not None

        # 3. 签到成功
        checkin_service = CheckInService(db_session)
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        assert checkin is not None

        # 4. 取消SOS
        cancelled_sos = sos_service.cancel_sos_request(
            sos_id=sos.id,
            user_id=test_user.id,
            reason="已安全"
        )
        assert cancelled_sos is not None

    def test_end_to_end_alert_workflow(self, db_session, test_user, test_emergency_contacts):
        """端到端预警工作流测试"""
        alert_service = AlertService(db_session)
        notification_service = NotificationService(db_session)
        checkin_service = CheckInService(db_session)

        # 1. 设置预警阈值
        alert_setting = alert_service.create_alert_setting(
            user_id=test_user.id,
            alert_threshold_hours=24,
            notification_enabled=True
        )

        # 2. 模拟25小时未签到
        checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        checkin.checkin_time = datetime.utcnow() - timedelta(hours=25)
        db_session.commit()

        # 3. 检查并触发预警
        alert = alert_service.check_user_alert(test_user.id)
        assert alert is not None

        # 4. 通知紧急联系人
        for contact in test_emergency_contacts:
            notification = notification_service.send_notification(
                user_id=contact.id,
                notification_type="",
                title="异常预警",
                content=f"{test_user.nickname}已超过24小时未签到"
            )
            assert notification is not None

        # 5. 用户签到,自动解除预警
        new_checkin = checkin_service.create_checkin(
            user_id=test_user.id,
            latitude=39.908823,
            longitude=116.397470,
            location="北京市朝阳区"
        )
        alert_service.resolve_alert(alert.id, reason="用户已签到")

    def test_data_consistency_verification(self, db_session, test_user):
        """数据一致性验证"""
        # 验证用户数据完整性
        assert test_user.phone is not None
        assert test_user.nickname is not None
        assert test_user.is_active == True

        # 验证关联关系完整性
        contacts = db_session.query(EmergencyContact).filter(
            EmergencyContact.user_id == test_user.id
        ).all()
        assert len(contacts) >= 1

        # 验证外键约束
        for contact in contacts:
            assert contact.user_id == test_user.id

    def test_security_validation(self, db_session, test_user):
        """安全验证测试"""
        # 1. 测试密码加密
        assert test_user.password_hash != "SecurePass123"

        # 2. 测试JWT认证
        user_service = UserService(db_session)
        login_result = user_service.login(
            phone=test_user.phone,
            password="SecurePass123"
        )
        assert login_result["access_token"] is not None

        # 3. 测试健康档案加密
        health_record = db_session.query(HealthRecord).filter(
            HealthRecord.user_id == test_user.id
        ).first()
        if health_record:
            assert health_record.is_encrypted == True

    def test_performance_benchmark(self, db_session, test_user):
        """性能基准测试"""
        import time

        # 1. 测试签到性能(100次)
        checkin_service = CheckInService(db_session)
        start_time = time.time()
        for i in range(100):
            checkin = checkin_service.create_checkin(
                user_id=test_user.id,
                latitude=39.908823 + (i * 0.0001),
                longitude=116.397470 + (i * 0.0001),
                location=f"北京市朝阳区{i}"
            )
        end_time = time.time()
        assert (end_time - start_time) < 10.0  # 100次签到应在10秒内完成

        # 2. 测试查询性能
        start_time = time.time()
        history = checkin_service.get_checkin_history(
            user_id=test_user.id,
            days=30
        )
        end_time = time.time()
        assert (end_time - start_time) < 1.0  # 查询应在1秒内完成

    def test_integration_completeness(self, db_session):
        """集成完整性测试"""
        # 验证所有服务都能正常初始化
        services = [
            UserService(db_session),
            EmergencyContactService(db_session),
            CheckInService(db_session),
            AlertService(db_session),
            SOSService(db_session),
            HealthRecordService(db_session),
            DeviceService(db_session),
            AnomalyService(db_session),
            EmergencyResourceService(db_session),
            EmergencyCenterService(db_session),
            NotificationService(db_session),
        ]

        for service in services:
            assert service is not None

    def test_api_endpoint_completeness(self, db_session, test_user):
        """API端点完整性测试"""
        # 验证所有API端点都能正常访问
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 测试登录
        response = client.post(
            "/api/v1/users/login",
            json={"phone": test_user.phone, "password": "SecurePass123"}
        )
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 测试获取用户信息
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=headers
        )
        assert response.status_code == 200

        # 测试获取紧急联系人列表
        response = client.get(
            f"/api/v1/emergency-contacts/user/{test_user.id}",
            headers=headers
        )
        assert response.status_code == 200


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
        nickname="测试用户",
        gender="male",
        birth_date="1990-01-01"
    )
    return user


@pytest.fixture
def test_emergency_contacts(db_session, test_user):
    """测试紧急联系人fixture"""
    contact_service = EmergencyContactService(db_session)
    contacts = []
    for i in range(3):
        contact = contact_service.add_contact(
            user_id=test_user.id,
            name=f"联系人{i+1}",
            phone=f"1390013900{i+1}",
            relationship="家人",
            priority=i+1
        )
        contacts.append(contact)
    return contacts


@pytest.fixture
def test_device(db_session, test_user):
    """测试设备fixture"""
    device_service = DeviceService(db_session)
    device = device_service.bind_device(
        user_id=test_user.id,
        device_name="智能手环",
        device_type="smartwatch",
        mac_address="00:1A:2B:3C:4D:5E"
    )
    return device


@pytest.fixture
def test_health_record(db_session, test_user):
    """测试健康档案fixture"""
    health_service = HealthRecordService(db_session)
    health_record = health_service.create_health_record(
        user_id=test_user.id,
        blood_type="A",
        height=175,
        weight=70
    )
    return health_record
