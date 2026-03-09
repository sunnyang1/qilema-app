"""
120急救中心对接服务单元测试

测试120一键拨打、位置发送、健康档案摘要、救护车追踪等核心功能
"""

import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from app.core.database import Base
from app.models.anomaly import Anomaly, AnomalyTypeEnum, SeverityLevel
from app.models.device import Device
from app.models.device_data import DeviceData
from app.models.emergency_center_model import EmergencyCall, EmergencyCenter
from app.models.emergency_contact import EmergencyContact
from app.models.health_record import HealthRecord
from app.models.sos_request import SOSRequest, SOSStatusEnum, SOSTypeEnum
from app.models.user import BloodTypeEnum, GenderEnum, User
from app.schemas.emergency_center import (
    AmbulanceLocation,
    AmbulanceStatus,
    Call120Request,
    EmergencyCallStatus,
    RescueRecordCreate,
)
from app.services.emergency_center_service import EmergencyCenterService
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ========== 测试数据库设置 ==========

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def emergency_center_service():
    """创建服务实例"""
    # 设置测试用的加密密钥
    test_key = Fernet.generate_key().decode()
    os.environ["ENCRYPTION_KEY"] = test_key
    try:
        yield EmergencyCenterService()
    finally:
        # 清理环境变量
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]


# ========== 测试数据准备 ==========


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User(
        user_id="user_test_001",
        phone="13800138001",
        password_hash="hashed_password",
        nickname="测试用户",
        gender=GenderEnum.MALE,
        blood_type=BloodTypeEnum.O,
        height=175,
        weight=70,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_emergency_center(db):
    """创建测试急救中心"""
    center = EmergencyCenter(
        center_name="北京市急救中心",
        center_code="BJ120",
        city="北京",
        province="北京市",
        phone="120",
        emergency_phone="120",
        service_area="北京市全域",
        service_radius=50000,
        is_active=True,
        is_24h=True,
        has_ambulance_tracking=True,
        has_auto_dispatch=True,
    )
    db.add(center)
    db.commit()
    db.refresh(center)
    return center


@pytest.fixture
def test_emergency_contact(db, test_user):
    """创建测试紧急联系人"""
    contact = EmergencyContact(
        user_id=test_user.user_id,
        name="张三",
        phone="13900139001",
        relationship="配偶",
        priority=1,
        is_primary=True,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@pytest.fixture
def test_health_record(db, test_user):
    """创建测试健康档案"""
    record = HealthRecord(
        user_id=test_user.user_id,
        real_name="测试用户",
        gender="男",
        blood_type="O",
        height=175.0,
        weight=70.0,
        age=30,
        allergies_json='["青霉素", "磺胺类"]',
        chronic_diseases_json='["高血压", "糖尿病"]',
        current_medications_json='["降压药", "胰岛素"]',
        surgeries_json='["阑尾切除术"]',
        blood_transfusion_history=0,
        organ_transplant_history=0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@pytest.fixture
def test_sos_request(db, test_user):
    """创建测试SOS请求"""
    sos = SOSRequest(
        user_id=test_user.user_id,
        sos_type=SOSTypeEnum.MANUAL,
        status=SOSStatusEnum.PENDING,
        latitude=39.9042,
        longitude=116.4074,
        emergency_reason="测试紧急情况",
    )
    db.add(sos)
    db.commit()
    db.refresh(sos)
    return sos


@pytest.fixture
def test_device(db, test_user):
    """创建测试设备"""
    device = Device(
        device_id="device_test_001",
        user_id=test_user.user_id,
        device_type="smartwatch",
        device_name="智能手表",
        device_brand="华为",
        device_model="Watch GT 3",
        status="active",
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@pytest.fixture
def test_device_data(db, test_device, test_user):
    """创建测试设备数据"""
    data = DeviceData(
        data_id="data_test_001",
        device_id=test_device.device_id,
        user_id=test_user.user_id,
        data_type="health",
        data_value={
            "heart_rate": 75,
            "blood_pressure": {"systolic": 120, "diastolic": 80},
            "blood_oxygen": 98.5,
        },
        heart_rate=75,
        blood_oxygen=98.5,
        systolic_pressure=120,
        diastolic_pressure=80,
        steps=5000,
        sleep_duration=7.5,
        data_timestamp=datetime.utcnow(),
        upload_time=datetime.utcnow(),
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@pytest.fixture
def test_anomaly(db, test_user):
    """创建测试异常记录"""
    anomaly = Anomaly(
        user_id=test_user.user_id,
        anomaly_type=AnomalyTypeEnum.HEART_RATE_HIGH,
        severity=SeverityLevel.HIGH,
        anomaly_value=180.0,
        threshold_value=100.0,
        detected_at=datetime.utcnow(),
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly


# ========== 120一键拨打测试 ==========


def test_call_120_success(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试成功拨打120"""
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )

    response = emergency_center_service.call_120(db, request)

    assert response.call_id is not None
    assert response.call_status in [
        EmergencyCallStatus.CONNECTED.value,
        EmergencyCallStatus.DIALING.value,
    ]
    assert response.dialed_at is not None
    assert response.location_sent is True
    assert response.health_summary_sent is True


def test_call_120_without_health_summary(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试拨打120不发送健康档案"""
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=False,
    )

    response = emergency_center_service.call_120(db, request)

    assert response.health_summary_sent is False


def test_call_120_invalid_location(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试拨打120位置格式错误"""
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="invalid_location",
        send_health_summary=True,
    )

    response = emergency_center_service.call_120(db, request)

    # 应该仍然成功拨打,但位置发送失败
    assert response.call_id is not None
    assert response.location_sent is False


def test_call_120_with_sos_request(
    db, emergency_center_service, test_user, test_emergency_center, test_sos_request
):
    """测试拨打120关联SOS请求"""
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=str(test_sos_request.id),
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )

    response = emergency_center_service.call_120(db, request)

    call = db.query(EmergencyCall).filter(EmergencyCall.id == response.call_id).first()
    assert call.sos_request_id == str(test_sos_request.id)


def test_call_120_no_emergency_center(db, emergency_center_service, test_user):
    """测试没有急救中心时拨打120"""
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )

    response = emergency_center_service.call_120(db, request)

    # 应该仍然成功拨打,使用默认120
    assert response.call_id is not None
    assert response.emergency_center_id is None


# ========== 健康档案摘要测试 ==========


def test_generate_health_summary(
    db,
    emergency_center_service,
    test_user,
    test_health_record,
    test_emergency_contact,
    test_device_data,
):
    """测试生成健康档案摘要"""
    summary = emergency_center_service.generate_health_summary(db, test_user.user_id)

    assert summary.user_id == test_user.user_id
    assert summary.user_name == test_user.nickname
    assert summary.blood_type == test_user.blood_type.value
    assert summary.latest_heart_rate == test_device_data.heart_rate
    assert len(summary.emergency_contacts) >= 1


def test_generate_health_summary_with_anomalies(
    db,
    emergency_center_service,
    test_user,
    test_health_record,
    test_emergency_contact,
    test_device_data,
    test_anomaly,
):
    """测试生成健康档案摘要包含异常记录"""
    summary = emergency_center_service.generate_health_summary(db, test_user.user_id)

    assert len(summary.recent_anomalies) >= 1
    assert (
        summary.recent_anomalies[0]["anomaly_type"] == test_anomaly.anomaly_type.value
    )


def test_generate_health_summary_user_not_found(db, emergency_center_service):
    """测试用户不存在"""
    with pytest.raises(ValueError, match="用户不存在"):
        emergency_center_service.generate_health_summary(db, "invalid_user_id")


def test_generate_health_summary_no_health_record(
    db, emergency_center_service, test_user, test_emergency_contact, test_device_data
):
    """测试没有健康档案时生成摘要"""
    summary = emergency_center_service.generate_health_summary(db, test_user.user_id)

    assert summary.user_id == test_user.user_id
    assert summary.chronic_diseases is None
    assert summary.allergies is None


# ========== 救护车管理测试 ==========


def test_dispatch_ambulance(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试派出救护车"""
    # 先创建急救呼叫
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )
    call_response = emergency_center_service.call_120(db, request)

    # 派出救护车
    ambulance = emergency_center_service.dispatch_ambulance(db, call_response.call_id)

    assert ambulance.id is not None
    assert ambulance.emergency_call_id == call_response.call_id
    assert ambulance.status == AmbulanceStatus.ON_ROUTE
    assert ambulance.ambulance_number is not None
    assert ambulance.dispatched_at is not None
    assert ambulance.eta_minutes == 15


def test_update_ambulance_location(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试更新救护车位置"""
    # 先创建急救呼叫和救护车
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )
    call_response = emergency_center_service.call_120(db, request)
    ambulance = emergency_center_service.dispatch_ambulance(db, call_response.call_id)

    # 更新位置
    location_data = AmbulanceLocation(
        ambulance_id=ambulance.id,
        latitude=39.9100,
        longitude=116.4100,
        address="北京市朝阳区",
        timestamp=datetime.utcnow(),
    )

    updated_ambulance = emergency_center_service.update_ambulance_location(
        db, location_data
    )

    assert updated_ambulance.current_latitude == 39.9100
    assert updated_ambulance.current_longitude == 116.4100
    assert updated_ambulance.current_address == "北京市朝阳区"
    assert updated_ambulance.location_updated_at is not None


def test_track_ambulance(
    db, emergency_center_service, test_user, test_emergency_center
):
    """测试追踪救护车"""
    # 先创建急救呼叫和救护车
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )
    call_response = emergency_center_service.call_120(db, request)
    ambulance = emergency_center_service.dispatch_ambulance(db, call_response.call_id)

    # 更新位置
    location_data = AmbulanceLocation(
        ambulance_id=ambulance.id,
        latitude=39.9100,
        longitude=116.4100,
        address="北京市朝阳区",
        timestamp=datetime.utcnow(),
    )
    emergency_center_service.update_ambulance_location(db, location_data)

    # 追踪救护车
    tracking = emergency_center_service.track_ambulance(db, call_response.call_id)

    assert tracking.ambulance_id == ambulance.id
    assert tracking.ambulance_number == ambulance.ambulance_number
    assert tracking.status == ambulance.status
    assert tracking.current_location["latitude"] == 39.9100
    assert tracking.current_location["longitude"] == 116.4100
    assert tracking.eta_minutes == 15


def test_track_ambulance_not_found(db, emergency_center_service):
    """测试追踪不存在的救护车"""
    with pytest.raises(ValueError, match="救护车不存在"):
        emergency_center_service.track_ambulance(db, 99999)


# ========== 救援记录管理测试 ==========


def test_create_rescue_record(
    db, emergency_center_service, test_user, test_sos_request
):
    """测试创建救援记录"""
    record_data = RescueRecordCreate(
        user_id=test_user.user_id,
        sos_request_id=test_sos_request.id,
        emergency_call_id=None,
        rescue_type="意外伤害",
        urgency_level="紧急",
        incident_time=datetime.utcnow(),
        alarm_time=datetime.utcnow(),
        incident_location="116.4074,39.9042",
        incident_address="北京市朝阳区",
    )

    record = emergency_center_service.create_rescue_record(db, record_data)

    assert record.id is not None
    assert record.user_id == test_user.user_id
    assert record.sos_request_id == test_sos_request.id
    assert record.rescue_type == "意外伤害"
    assert record.urgency_level == "紧急"


def test_update_rescue_record(
    db, emergency_center_service, test_user, test_sos_request
):
    """测试更新救援记录"""
    # 先创建救援记录
    incident_time = datetime.utcnow()
    alarm_time = datetime.utcnow()
    record_data = RescueRecordCreate(
        user_id=test_user.user_id,
        sos_request_id=test_sos_request.id,
        emergency_call_id=None,
        rescue_type="意外伤害",
        urgency_level="紧急",
        incident_time=incident_time,
        alarm_time=alarm_time,
        incident_location="116.4074,39.9042",
        incident_address="北京市朝阳区",
    )
    record = emergency_center_service.create_rescue_record(db, record_data)

    # 更新救援记录
    arrival_time = datetime.utcnow()
    completion_time = datetime.utcnow()
    from app.schemas.emergency_center import RescueRecordUpdate

    update_data = RescueRecordUpdate(
        arrival_time=arrival_time,
        completion_time=completion_time,
        outcome="成功救援",
        patient_status="稳定",
        ambulance_cost=500.0,
        medical_cost=2000.0,
        user_feedback="救援及时",
        user_rating=5,
    )

    updated_record = emergency_center_service.update_rescue_record(
        db, record.id, update_data
    )

    assert updated_record.arrival_time == arrival_time
    assert updated_record.completion_time == completion_time
    assert updated_record.outcome == "成功救援"
    assert updated_record.patient_status == "稳定"
    assert updated_record.ambulance_cost == 500.0
    assert updated_record.medical_cost == 2000.0
    assert updated_record.user_feedback == "救援及时"
    assert updated_record.user_rating == 5
    assert updated_record.response_time_minutes is not None
    assert updated_record.overall_duration_minutes is not None


def test_update_rescue_record_not_found(db, emergency_center_service):
    """测试更新不存在的救援记录"""
    from app.schemas.emergency_center import RescueRecordUpdate

    update_data = RescueRecordUpdate(outcome="测试")

    result = emergency_center_service.update_rescue_record(db, 99999, update_data)
    assert result is None


# ========== 急救中心管理测试 ==========


def test_create_emergency_center(db, emergency_center_service):
    """测试创建急救中心"""
    from app.schemas.emergency_center import EmergencyCenterCreate

    center_data = EmergencyCenterCreate(
        center_name="上海市急救中心",
        center_code="SH120",
        city="上海",
        province="上海市",
        phone="120",
        service_area="上海市全域",
        service_radius=60000,
        is_active=1,
        is_24h=1,
    )

    center = emergency_center_service.create_emergency_center(db, center_data)

    assert center.id is not None
    assert center.center_name == "上海市急救中心"
    assert center.center_code == "SH120"
    assert center.city == "上海"
    assert center.is_active == 1


def test_get_emergency_centers(db, emergency_center_service, test_emergency_center):
    """测试获取急救中心列表"""
    centers = emergency_center_service.get_emergency_centers(db, active_only=True)

    assert len(centers) >= 1
    assert any(c.id == test_emergency_center.id for c in centers)


def test_get_emergency_centers_include_inactive(
    db, emergency_center_service, test_emergency_center
):
    """测试获取所有急救中心(包含未启用的)"""
    # 创建一个未启用的急救中心
    from app.schemas.emergency_center import EmergencyCenterCreate

    inactive_center_data = EmergencyCenterCreate(
        center_name="测试急救中心",
        center_code="TEST120",
        city="北京",
        phone="120",
        is_active=False,
    )
    emergency_center_service.create_emergency_center(db, inactive_center_data)

    # 只获取启用的
    active_centers = emergency_center_service.get_emergency_centers(
        db, active_only=True
    )
    assert not any(c.center_code == "TEST120" for c in active_centers)

    # 获取所有
    all_centers = emergency_center_service.get_emergency_centers(db, active_only=False)
    assert any(c.center_code == "TEST120" for c in all_centers)


# ========== 集成测试 ==========


def test_full_emergency_call_flow(
    db,
    emergency_center_service,
    test_user,
    test_emergency_center,
    test_health_record,
    test_emergency_contact,
    test_device_data,
):
    """测试完整的急救呼叫流程"""
    # 1. 拨打120
    request = Call120Request(
        user_id=test_user.user_id,
        sos_request_id=None,
        caller_location="116.4074,39.9042",
        send_health_summary=True,
    )
    call_response = emergency_center_service.call_120(db, request)

    assert call_response.call_id is not None
    assert call_response.location_sent is True
    assert call_response.health_summary_sent is True

    # 2. 派出救护车
    ambulance = emergency_center_service.dispatch_ambulance(db, call_response.call_id)
    assert ambulance.id is not None

    # 3. 更新救护车位置
    location_data = AmbulanceLocation(
        ambulance_id=ambulance.id,
        latitude=39.9100,
        longitude=116.4100,
        address="北京市朝阳区",
        timestamp=datetime.utcnow(),
    )
    emergency_center_service.update_ambulance_location(db, location_data)

    # 4. 追踪救护车
    tracking = emergency_center_service.track_ambulance(db, call_response.call_id)
    assert tracking.ambulance_id == ambulance.id
    assert tracking.current_location["latitude"] == 39.9100

    # 5. 创建救援记录
    record_data = RescueRecordCreate(
        user_id=test_user.user_id,
        sos_request_id=None,
        emergency_call_id=call_response.call_id,
        rescue_type="意外伤害",
        urgency_level="紧急",
        incident_time=datetime.utcnow(),
        alarm_time=datetime.utcnow(),
        incident_location="116.4074,39.9042",
        incident_address="北京市朝阳区",
    )
    record = emergency_center_service.create_rescue_record(db, record_data)
    assert record.id is not None

    # 6. 更新救援记录
    from app.schemas.emergency_center import RescueRecordUpdate

    update_data = RescueRecordUpdate(
        arrival_time=datetime.utcnow(),
        completion_time=datetime.utcnow(),
        outcome="成功救援",
    )
    updated_record = emergency_center_service.update_rescue_record(
        db, record.id, update_data
    )
    assert updated_record.outcome == "成功救援"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
