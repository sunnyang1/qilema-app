"""SOS求助服务单元测试"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.models.user import User
from app.models.sos_request import SOSRequest, SOSLocationHistory, SOSStatusEnum, SOSTypeEnum
from app.models.checkin import CheckIn
from app.models.alert import Alert, AlertSetting
from app.models.emergency_contact import EmergencyContact
from app.services.sos_service import SOSService
from app.services.location_service import LocationService
from app.services.emergency_service import EmergencyService
from app.schemas.sos_request import (
    SOSRequestCreate, SOSRequestUpdate, SOSLocationUpdate,
    SOSCancelRequest, SOSStatusUpdateRequest
)


# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        user_id="test_user_001",
        phone="13800138000",
        password_hash="hashed_password_test",
        nickname="测试用户"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_emergency_contact(db_session, test_user):
    """创建测试紧急联系人"""
    contact = EmergencyContact(
        user_id=test_user.user_id,
        name="张三",
        phone="13900139000",
        relationship="父亲",
        priority=1
    )
    db_session.add(contact)
    db_session.commit()
    return contact


class TestSOSService:
    """SOS服务测试类"""

    def test_create_sos_request(self, db_session, test_user):
        """测试创建SOS请求"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号",
            location_accuracy=10.0
        )
        sos_request = SOSService.create_sos_request(db_session, sos_data)

        assert sos_request.id is not None
        assert sos_request.user_id == test_user.user_id
        assert sos_request.sos_type == SOSTypeEnum.MANUAL.value
        assert sos_request.status == SOSStatusEnum.PENDING.value
        assert sos_request.latitude == 39.9042
        assert sos_request.longitude == 116.4074

    def test_get_sos_request(self, db_session, test_user):
        """测试查询SOS请求"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        created_sos = SOSService.create_sos_request(db_session, sos_data)
        found_sos = SOSService.get_sos_request(db_session, created_sos.id, test_user.user_id)

        assert found_sos is not None
        assert found_sos.id == created_sos.id

    def test_get_active_sos(self, db_session, test_user):
        """测试获取活动SOS请求"""
        # 创建pending状态的SOS
        sos_data1 = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos1 = SOSService.create_sos_request(db_session, sos_data1)

        # 查询活动SOS
        active_sos = SOSService.get_active_sos(db_session, test_user.user_id)
        assert active_sos is not None
        assert active_sos.id == sos1.id
        assert active_sos.status == SOSStatusEnum.PENDING.value

    def test_update_sos_status(self, db_session, test_user):
        """测试更新SOS状态"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos = SOSService.create_sos_request(db_session, sos_data)

        # 更新状态为救援中
        update_data = SOSStatusUpdateRequest(
            status=SOSStatusEnum.RESCUING.value,
            status_change_reason="救护车已出发",
            ambulance_contact="13800138001",
            ambulance_eta=15
        )
        updated_sos = SOSService.update_sos_status(db_session, sos.id, test_user.user_id, update_data)

        assert updated_sos.status == SOSStatusEnum.RESCUING.value
        assert updated_sos.status_change_reason == "救护车已出发"
        assert updated_sos.ambulance_contact == "13800138001"
        assert updated_sos.ambulance_eta == 15
        assert updated_sos.rescue_start_time is not None

    def test_cancel_sos_request(self, db_session, test_user):
        """测试取消SOS请求"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos = SOSService.create_sos_request(db_session, sos_data)

        # 取消SOS
        cancel_data = SOSCancelRequest(
            cancel_reason="误触取消",
            confirm_code="1234"
        )
        cancelled_sos = SOSService.cancel_sos_request(db_session, sos.id, test_user.user_id, cancel_data)

        assert cancelled_sos.status == SOSStatusEnum.CANCELLED.value
        assert cancelled_sos.status_change_reason == "误触取消"
        assert cancelled_sos.resolve_time is not None

    def test_cancel_sos_request_invalid_status(self, db_session, test_user):
        """测试取消非pending状态的SOS请求(应该失败)"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos = SOSService.create_sos_request(db_session, sos_data)

        # 更新状态为救援中
        update_data = SOSStatusUpdateRequest(
            status=SOSStatusEnum.RESCUING.value
        )
        SOSService.update_sos_status(db_session, sos.id, test_user.user_id, update_data)

        # 尝试取消(应该失败)
        cancel_data = SOSCancelRequest(
            cancel_reason="误触取消",
            confirm_code="1234"
        )
        with pytest.raises(ValueError, match="只能取消待救援状态的SOS请求"):
            SOSService.cancel_sos_request(db_session, sos.id, test_user.user_id, cancel_data)

    def test_add_location_history(self, db_session, test_user):
        """测试添加位置历史记录"""
        sos_data = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos = SOSService.create_sos_request(db_session, sos_data)

        # 添加位置记录
        location_data = SOSLocationUpdate(
            sos_request_id=sos.id,
            latitude=39.9045,
            longitude=116.4078,
            address="北京市朝阳区建国路90号",
            location_accuracy=5.0
        )
        location = SOSService.add_location_history(db_session, sos.id, test_user.user_id, location_data)

        assert location is not None
        assert location.latitude == 39.9045
        assert location.longitude == 116.4078
        assert location.sos_request_id == sos.id

    def test_get_sos_history(self, db_session, test_user):
        """测试查询SOS历史记录"""
        # 创建3个SOS请求
        for i in range(3):
            sos_data = SOSRequestCreate(
                user_id=test_user.user_id,
                sos_type=SOSTypeEnum.MANUAL.value,
                latitude=39.9042 + i * 0.001,
                longitude=116.4074 + i * 0.001,
                address=f"北京市朝阳区建国路{88 + i}号"
            )
            SOSService.create_sos_request(db_session, sos_data)

        # 查询历史记录
        sos_requests, total = SOSService.get_sos_history(db_session, test_user.user_id)

        assert total == 3
        assert len(sos_requests) == 3

    def test_get_emergency_contacts(self, db_session, test_user):
        """测试获取紧急联系人列表"""
        # 创建3个紧急联系人
        for i in range(3):
            contact = EmergencyContact(
                user_id=test_user.user_id,
                name=f"联系人{i+1}",
                phone=f"1390013900{i}",
                relationship=f"亲属{i+1}",
                priority=i + 1
            )
            db_session.add(contact)
        db_session.commit()

        # 查询紧急联系人
        contacts = SOSService.get_emergency_contacts(db_session, test_user.user_id)

        assert len(contacts) == 3
        # 验证按优先级排序
        assert contacts[0].priority == 1
        assert contacts[1].priority == 2
        assert contacts[2].priority == 3

    def test_get_sos_statistics(self, db_session, test_user):
        """测试获取SOS统计信息"""
        # 创建不同状态的SOS请求
        sos_data1 = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )
        sos1 = SOSService.create_sos_request(db_session, sos_data1)

        sos_data2 = SOSRequestCreate(
            user_id=test_user.user_id,
            sos_type=SOSTypeEnum.MANUAL.value,
            latitude=39.9043,
            longitude=116.4075,
            address="北京市朝阳区建国路89号"
        )
        sos2 = SOSService.create_sos_request(db_session, sos_data2)

        # 将一个标记为已解决
        update_data = SOSStatusUpdateRequest(
            status=SOSStatusEnum.RESOLVED.value
        )
        SOSService.update_sos_status(db_session, sos1.id, test_user.user_id, update_data)

        # 获取统计信息
        stats = SOSService.get_sos_statistics(db_session, test_user.user_id)

        assert stats['total_sos'] == 2
        assert stats['pending_sos'] == 1
        assert stats['resolved_sos'] == 1


class TestLocationService:
    """定位服务测试类"""

    def test_calculate_distance(self):
        """测试计算两点距离"""
        # 北京的两个点
        lat1, lon1 = 39.9042, 116.4074
        lat2, lon2 = 39.9142, 116.4174

        distance = LocationService.calculate_distance(lat1, lon1, lat2, lon2)

        # 距离应该是正数且合理(大约1-2公里)
        assert distance > 0
        assert distance < 5000

    def test_calculate_bearing(self):
        """测试计算方位角"""
        lat1, lon1 = 39.9042, 116.4074
        lat2, lon2 = 39.9142, 116.4074  # 正北方向

        bearing = LocationService.calculate_bearing(lat1, lon1, lat2, lon2)

        # 方位角应该在0-360之间,且接近0(正北)
        assert 0 <= bearing <= 360
        assert bearing < 10 or bearing > 350  # 允许误差

    def test_validate_location_valid(self):
        """测试验证有效经纬度"""
        assert LocationService.validate_location(39.9042, 116.4074) == True

    def test_validate_location_invalid(self):
        """测试验证无效经纬度"""
        # 纬度超出范围
        assert LocationService.validate_location(100, 116.4074) == False
        # 经度超出范围
        assert LocationService.validate_location(39.9042, 200) == False

    def test_simulate_location_update(self):
        """测试模拟位置更新"""
        base_lat, base_lon = 39.9042, 116.4074
        new_lat, new_lon = LocationService.simulate_location_update(
            base_lat, base_lon, distance_meters=100, angle_degrees=0
        )

        # 新位置应该与基准位置不同
        assert new_lat != base_lon  # 纬度应该改变
        # 新经纬度应该在合理范围内
        assert LocationService.validate_location(new_lat, new_lon)


class TestEmergencyService:
    """120急救服务测试类"""

    def test_call_emergency_center(self):
        """测试拨打120急救中心"""
        response = EmergencyService.call_emergency_center(
            phone="13800138000",
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号",
            user_info={"nickname": "测试用户"}
        )

        assert response['success'] == True
        assert 'ambulance_id' in response
        assert 'eta' in response
        assert 'ambulance_phone' in response
        assert 'call_id' in response

    def test_send_location_to_ambulance(self):
        """测试发送位置给救护车"""
        response = EmergencyService.send_location_to_ambulance(
            call_id="CALL12345",
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        )

        assert response['success'] == True

    def test_get_nearest_hospitals(self):
        """测试获取附近医院"""
        hospitals = EmergencyService.get_nearest_hospitals(
            latitude=39.9042,
            longitude=116.4074,
            radius_km=5.0,
            limit=3
        )

        assert len(hospitals) > 0
        assert 'name' in hospitals[0]
        assert 'address' in hospitals[0]
        assert 'distance' in hospitals[0]
        assert 'phone' in hospitals[0]

    def test_generate_health_summary(self):
        """测试生成健康档案摘要"""
        user_info = {
            "nickname": "张三",
            "age": 30,
            "gender": "男",
            "blood_type": "A型",
            "phone": "13800138000",
            "address": "北京市朝阳区建国路88号"
        }
        emergency_contacts = [
            {"name": "李四", "phone": "13900139000", "relationship": "父亲"}
        ]

        summary = EmergencyService.generate_health_summary(user_info, emergency_contacts)

        assert summary['user_name'] == "张三"
        assert summary['age'] == 30
        assert len(summary['emergency_contacts']) == 1

    def test_cancel_emergency_call(self):
        """测试取消急救呼叫"""
        response = EmergencyService.cancel_emergency_call(
            call_id="CALL12345",
            reason="误触"
        )

        assert response['success'] == True
        assert response['reason'] == "误触"

    def test_verify_emergency_call_limit(self):
        """测试验证急救呼叫限制"""
        response = EmergencyService.verify_emergency_call_limit("user_001")

        assert response['allowed'] == True
        assert 'remaining_calls' in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
