"""
核心模块
"""

from dependency_injector import containers, providers

from app.core.cache_mixin import CacheMixin, CacheWarmer
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine, get_db
from app.core.query_builder import BatchQueryBuilder, QueryBuilder, paginate
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

__all__ = [
    "containers",
    "providers",
    "settings",
    "engine",
    "Base",
    "get_db",
    "SessionLocal",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "CacheMixin",
    "CacheWarmer",
    "QueryBuilder",
    "BatchQueryBuilder",
    "paginate",
]
