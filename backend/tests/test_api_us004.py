"""
US-004：API 路由集中注册、版本发现、响应头与公开路径策略。
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_versions_discovery(client):
    r = client.get("/api/versions")
    assert r.status_code == 200
    body = r.json()
    assert body["current"] == "v1"
    assert body["prefix"] == "/api/v1"
    assert any(
        v.get("name") == "v1" and v.get("status") == "current" for v in body["versions"]
    )


def test_x_api_version_header_on_v1_routes(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "1"
    assert "X-Request-ID" in r.headers


def test_auth_policy_public_paths():
    from app.core.auth_policy import is_public_path

    assert is_public_path("/api/v1/auth/login") is True
    assert is_public_path("/api/v1/users/register") is True
    assert is_public_path("/health") is True
    assert is_public_path("/api/versions") is True
    assert is_public_path("/api/v1/users/me") is False


def test_create_api_v1_router_matches_settings():
    from app.api.routes import create_api_v1_router
    from app.core.config import settings

    router = create_api_v1_router()
    assert router.prefix == settings.API_V1_PREFIX


def test_unauthorized_includes_www_authenticate(client):
    """OAuth2 依赖在未带 Bearer 时应返回 401 且保留 WWW-Authenticate（code review P0）。"""
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401
    www = r.headers.get("www-authenticate")
    assert www is not None
    assert "bearer" in www.lower()


@pytest.mark.asyncio
async def test_value_error_handler_includes_request_id():
    """数据库/通用类异常经 merge 后应带 request_id（code review）。"""
    import json
    from unittest.mock import MagicMock

    from app.core.error_handlers import value_error_handler

    req = MagicMock()
    req.state.request_id = "correlation-xyz"
    resp = await value_error_handler(req, ValueError("bad"))
    body = json.loads(resp.body.decode())
    assert body.get("request_id") == "correlation-xyz"


def test_incoming_x_request_id_strips_control_chars(client):
    r = client.get("/health", headers={"X-Request-ID": "ab\x00cd\nef"})
    rid = r.headers.get("X-Request-ID")
    assert rid == "abcdef"


def test_get_user_by_id_requires_auth(client):
    r = client.get("/api/v1/users/00000000-0000-0000-0000-000000000001")
    assert r.status_code == 401


def test_get_user_by_id_forbidden_when_not_self_or_admin():
    from unittest.mock import MagicMock

    from app.core.security import get_current_user
    from main import app

    u1 = MagicMock()
    u1.user_id = "user-a"

    async def override_user():
        return u1

    app.dependency_overrides[get_current_user] = override_user
    try:
        c = TestClient(app)
        r = c.get("/api/v1/users/user-b")
        assert r.status_code == 403
        assert "无权" in r.json().get("message", "") or "无权" in str(r.json())
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sqlalchemy_handler_omits_raw_details_when_debug_off():
    import json
    from unittest.mock import MagicMock, patch

    from sqlalchemy.exc import SQLAlchemyError

    from app.core.error_handlers import sqlalchemy_exception_handler

    req = MagicMock()
    req.state.request_id = "rid-db"
    exc = SQLAlchemyError("internal table leak")
    with patch("app.core.error_handlers.settings") as mock_settings:
        mock_settings.DEBUG = False
        resp = await sqlalchemy_exception_handler(req, exc)
    body = json.loads(resp.body.decode())
    assert body.get("details") is None


@pytest.mark.asyncio
async def test_integrity_handler_omits_raw_details_when_debug_off():
    import json
    from unittest.mock import MagicMock, patch

    from sqlalchemy.exc import IntegrityError

    from app.core.error_handlers import integrity_error_handler

    req = MagicMock()
    req.state.request_id = "rid-int"
    orig_exc = Exception("UNIQUE constraint failed: users.phone")
    exc = IntegrityError("stmt", {}, orig_exc)
    with patch("app.core.error_handlers.settings") as mock_settings:
        mock_settings.DEBUG = False
        resp = await integrity_error_handler(req, exc)
    body = json.loads(resp.body.decode())
    assert body.get("details") is None
