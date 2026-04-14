"""
I-W2：预警设置 API 使用 AlertServiceDep（US-P03）。
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_alert_service
from app.core.security import get_current_user
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_alerts_me_settings_requires_auth(client):
    r = client.get("/api/v1/alerts/me/settings")
    assert r.status_code == 401


def test_get_alert_settings_empty(client):
    mock_user = MagicMock()
    mock_user.user_id = "user-iw2"

    mock_svc = MagicMock()
    mock_svc.get_setting.return_value = None

    async def override_user():
        return mock_user

    def override_alert():
        return mock_svc

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_alert_service] = override_alert
    try:
        r = client.get("/api/v1/alerts/me/settings")
        assert r.status_code == 200
        body = r.json()
        assert body.get("code") == 200
        assert body.get("data") is None
    finally:
        app.dependency_overrides.clear()


def test_put_alert_settings_create_or_update(client):
    mock_user = MagicMock()
    mock_user.user_id = "user-iw2"

    updated = SimpleNamespace(
        id=1,
        user_id="user-iw2",
        checkin_enabled=True,
        checkin_threshold_hours=48,
        abnormal_enabled=True,
        enable_notification=True,
        heart_rate_min=None,
        heart_rate_max=None,
        blood_pressure_systolic_min=None,
        blood_pressure_systolic_max=None,
        blood_pressure_diastolic_min=None,
        blood_pressure_diastolic_max=None,
        blood_oxygen_min=None,
        notification_channels="push,sms",
        emergency_contact_notify=True,
        auto_resolve=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_svc = MagicMock()
    mock_svc.create_or_update_setting.return_value = updated

    async def override_user():
        return mock_user

    def override_alert():
        return mock_svc

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_alert_service] = override_alert
    try:
        r = client.put(
            "/api/v1/alerts/me/settings",
            json={"checkin_threshold_hours": 48},
        )
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("checkin_threshold_hours") == 48
        assert body.get("data", {}).get("notification_channels") == ["push", "sms"]
        mock_svc.create_or_update_setting.assert_called_once()
    finally:
        app.dependency_overrides.clear()
