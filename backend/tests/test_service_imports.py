"""服务导入测试"""


def test_all_services_can_be_imported():
    """测试所有服务可以从app.services统一导入"""
    # When
    from app.services import (
        AlertService,
        AnomalyService,
        BaseService,
        CheckInService,
        DeviceService,
        EmergencyCenterService,
        EmergencyContactService,
        EmergencyResourceService,
        EmergencyService,
        HealthRecordService,
        LocationService,
        NotificationService,
        SOSService,
        UserService,
    )

    # Then: 所有服务都应该成功导入
    assert BaseService is not None
    assert UserService is not None
    assert AlertService is not None
    assert CheckInService is not None
    assert DeviceService is not None
    assert HealthRecordService is not None
    assert NotificationService is not None
    assert AnomalyService is not None
    assert EmergencyCenterService is not None
    assert EmergencyResourceService is not None
    assert SOSService is not None
    assert LocationService is not None
    assert EmergencyService is not None
    assert EmergencyContactService is not None


def test_all_list_contains_all_services():
    """测试__all__列表包含所有服务类"""
    # When
    from app.services import __all__

    # Then
    expected_services = [
        "BaseService",
        "UserService",
        "AlertService",
        "CheckInService",
        "DeviceService",
        "HealthRecordService",
        "NotificationService",
        "AnomalyService",
        "EmergencyCenterService",
        "EmergencyResourceService",
        "SOSService",
        "LocationService",
        "EmergencyService",
        "EmergencyContactService",
    ]

    for service in expected_services:
        assert service in __all__, f"{service} should be in __all__"
