"""紧急联系人缓存失效测试"""

from unittest.mock import Mock, patch

import pytest

from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from app.services.emergency_contact_service import EmergencyContactService


class TestEmergencyContactCacheInvalidation:
    """测试紧急联系人缓存失效逻辑"""

    @pytest.fixture
    def service(self, mock_db):
        return EmergencyContactService(mock_db)

    @pytest.fixture
    def mock_db(self):
        """模拟数据库"""
        return Mock()

    @pytest.fixture
    def sample_user_id(self):
        return "test_user_123"

    @patch("app.services.emergency_contact_service.invalidate_cache")
    def test_create_emergency_contact_invalidates_list_cache(
        self, mock_invalidate, service, mock_db, sample_user_id
    ):
        """测试创建联系人时失效列表缓存"""
        # Given
        data = EmergencyContactCreate(
            user_id=sample_user_id,
            contact_name="张三",
            relationship="父亲",
            phone="13800138000",
            is_primary=False,
        )

        # When
        service.create_emergency_contact(data, sample_user_id)

        # Then
        mock_invalidate.assert_called_with(f"emergency:contacts:{sample_user_id}")

    @patch("app.services.emergency_contact_service.invalidate_cache")
    def test_update_emergency_contact_invalidates_caches(
        self, mock_invalidate, service, mock_db, sample_user_id
    ):
        """测试更新联系人时失效单个和列表缓存"""
        # Given
        contact_id = 1
        sample_contact = Mock(spec=EmergencyContact)
        sample_contact.id = contact_id
        sample_contact.user_id = sample_user_id

        # 模拟获取联系人
        with patch.object(
            service, "get_emergency_contact", return_value=sample_contact
        ):
            update_data = EmergencyContactUpdate(contact_name="李四")

            # When
            service.update_emergency_contact(contact_id, update_data, sample_user_id)

        # Then
        calls = mock_invalidate.call_args_list
        assert any(
            f"emergency:contact:{contact_id}:{sample_user_id}" in str(call)
            for call in calls
        )
        assert any(
            f"emergency:contacts:{sample_user_id}" in str(call) for call in calls
        )

    @patch("app.services.emergency_contact_service.invalidate_cache")
    def test_delete_emergency_contact_invalidates_caches(
        self, mock_invalidate, service, mock_db, sample_user_id
    ):
        """测试删除联系人时失效单个和列表缓存"""
        # Given
        contact_id = 1
        sample_contact = Mock(spec=EmergencyContact)
        sample_contact.id = contact_id
        sample_contact.user_id = sample_user_id

        # 模拟获取联系人
        with patch.object(
            service, "get_emergency_contact", return_value=sample_contact
        ):
            # When
            service.delete_emergency_contact(contact_id, sample_user_id)

        # Then
        calls = mock_invalidate.call_args_list
        assert any(
            f"emergency:contact:{contact_id}:{sample_user_id}" in str(call)
            for call in calls
        )
        assert any(
            f"emergency:contacts:{sample_user_id}" in str(call) for call in calls
        )

    @patch("app.services.emergency_contact_service.invalidate_cache")
    def test_set_primary_contact_invalidates_list_cache(
        self, mock_invalidate, service, mock_db, sample_user_id
    ):
        """测试设置主要联系人时失效列表缓存"""
        # Given
        contact_id = 1
        sample_contact = Mock(spec=EmergencyContact)
        sample_contact.id = contact_id
        sample_contact.user_id = sample_user_id
        sample_contact.is_primary = False

        # 模拟数据库查询和获取联系人
        mock_query = Mock()
        mock_query.filter.return_value.update.return_value = None
        mock_db.query.return_value = mock_query

        with patch.object(
            service, "get_emergency_contact", return_value=sample_contact
        ):
            # When
            service.set_primary_contact(contact_id, sample_user_id)

        # Then
        mock_invalidate.assert_called_with(f"emergency:contacts:{sample_user_id}")
