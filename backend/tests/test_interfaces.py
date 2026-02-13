"""
服务接口单元测试
"""

import pytest
from abc import ABC
from unittest.mock import Mock, MagicMock

from app.core.interfaces import (
    ICheckInService,
    IUserService,
    IEmergencyContactService,
    ISosService,
    IHealthRecordService,
    INotificationService,
    IDeviceService,
    IAlertService
)


class TestICheckInService:
    """ICheckInService接口测试"""

    def test_is_abstract_class(self):
        """测试ICheckInService是抽象类"""
        assert issubclass(ICheckInService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_checkin',
            'get_user_checkins',
            'get_checkin_stats',
            'get_checkin_status',
            'check_today_checked_in'
        ]

        for method in required_methods:
            assert hasattr(ICheckInService, method)

    def test_cannot_instantiate(self):
        """测试不能直接实例化接口"""
        with pytest.raises(TypeError):
            ICheckInService()

    def test_implementation_class_can_instantiate(self):
        """测试实现类可以实例化"""

        class CheckInServiceImpl(ICheckInService):
            def create_checkin(self, db, user_id, checkin_data):
                return Mock()

            def get_user_checkins(self, db, user_id, offset=0, limit=20):
                return []

            def get_checkin_stats(self, db, user_id):
                return Mock()

            def get_checkin_status(self, db, user_id):
                return Mock()

            def check_today_checked_in(self, db, user_id):
                return False

        # 应该可以实例化
        service = CheckInServiceImpl()
        assert isinstance(service, ICheckInService)


class TestIUserService:
    """IUserService接口测试"""

    def test_is_abstract_class(self):
        """测试IUserService是抽象类"""
        assert issubclass(IUserService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_user',
            'get_user_by_id',
            'get_user_by_phone',
            'update_user',
            'authenticate',
            'delete_user',
            'get_all_users'
        ]

        for method in required_methods:
            assert hasattr(IUserService, method)


class TestIEmergencyContactService:
    """IEmergencyContactService接口测试"""

    def test_is_abstract_class(self):
        """测试IEmergencyContactService是抽象类"""
        assert issubclass(IEmergencyContactService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_emergency_contact',
            'get_emergency_contacts',
            'get_emergency_contact_by_id',
            'update_emergency_contact',
            'delete_emergency_contact',
            'delete_user_emergency_contacts'
        ]

        for method in required_methods:
            assert hasattr(IEmergencyContactService, method)


class TestISosService:
    """ISosService接口测试"""

    def test_is_abstract_class(self):
        """测试ISosService是抽象类"""
        assert issubclass(ISosService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_sos_request',
            'get_sos_request',
            'get_user_sos_requests',
            'cancel_sos_request',
            'update_sos_status',
            'get_active_sos_requests'
        ]

        for method in required_methods:
            assert hasattr(ISosService, method)


class TestIHealthRecordService:
    """IHealthRecordService接口测试"""

    def test_is_abstract_class(self):
        """测试IHealthRecordService是抽象类"""
        assert issubclass(IHealthRecordService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_health_record',
            'get_health_records',
            'get_health_record_by_id',
            'update_health_record',
            'delete_health_record',
            'get_latest_records'
        ]

        for method in required_methods:
            assert hasattr(IHealthRecordService, method)


class TestINotificationService:
    """INotificationService接口测试"""

    def test_is_abstract_class(self):
        """测试INotificationService是抽象类"""
        assert issubclass(INotificationService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'send_notification',
            'get_user_notifications',
            'mark_as_read',
            'mark_all_as_read',
            'delete_notification'
        ]

        for method in required_methods:
            assert hasattr(INotificationService, method)


class TestIDeviceService:
    """IDeviceService接口测试"""

    def test_is_abstract_class(self):
        """测试IDeviceService是抽象类"""
        assert issubclass(IDeviceService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'register_device',
            'get_user_devices',
            'update_device',
            'delete_device',
            'update_device_status'
        ]

        for method in required_methods:
            assert hasattr(IDeviceService, method)


class TestIAlertService:
    """IAlertService接口测试"""

    def test_is_abstract_class(self):
        """测试IAlertService是抽象类"""
        assert issubclass(IAlertService, ABC)

    def test_has_required_methods(self):
        """测试接口有必需的方法"""
        required_methods = [
            'create_alert',
            'get_alerts',
            'get_alert_by_id',
            'update_alert_status',
            'get_active_alerts'
        ]

        for method in required_methods:
            assert hasattr(IAlertService, method)
