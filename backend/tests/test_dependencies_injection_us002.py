"""
US-002：FastAPI 依赖工厂与 Protocol 结构化子类型。
"""

from unittest.mock import MagicMock

from app.api.dependencies import get_user_service
from app.core.service_protocols import UserServiceProtocol
from app.services.user_service import UserService


def test_user_service_satisfies_user_service_protocol():
    db = MagicMock()
    svc = UserService(db)
    assert isinstance(svc, UserServiceProtocol)


def test_get_user_service_returns_protocol_compatible_instance():
    db = MagicMock()
    svc = get_user_service(db)
    assert isinstance(svc, UserService)
    assert isinstance(svc, UserServiceProtocol)
