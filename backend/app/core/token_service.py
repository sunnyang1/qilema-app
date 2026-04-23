"""
Token Service (Phase 5)

JWT 双 Token 机制：短期 Access Token + 长期 Refresh Token。
Refresh Token 存储在 Redis 中，支持撤销（登出）。
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings
from app.core.redis import redis_manager


class TokenPair:
    """Token 对"""

    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token


class TokenService:
    """Token 服务

    提供 Access Token / Refresh Token 的创建、验证和撤销能力。
    """

    ACCESS_TTL = timedelta(minutes=15)
    REFRESH_TTL = timedelta(days=7)

    @classmethod
    def create_token_pair(cls, user_id: str) -> TokenPair:
        """创建 Access + Refresh Token 对

        Args:
            user_id: 用户ID

        Returns:
            TokenPair: Token 对
        """
        access_token = cls._create_access_token(user_id)
        refresh_token = cls._create_refresh_token(user_id)

        # 存储 refresh token 指纹到 Redis（用于撤销）
        cls._store_refresh_token(refresh_token, user_id)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    def _create_access_token(cls, user_id: str) -> str:
        """创建 Access Token"""
        expire = datetime.utcnow() + cls.ACCESS_TTL
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @classmethod
    def _create_refresh_token(cls, user_id: str) -> str:
        """创建 Refresh Token"""
        jti = uuid4().hex
        expire = datetime.utcnow() + cls.REFRESH_TTL
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": jti,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @classmethod
    def _store_refresh_token(cls, refresh_token: str, user_id: str):
        """存储 Refresh Token 指纹到 Redis"""
        try:
            redis_client = redis_manager.get_sync_client()
            if redis_client:
                fingerprint = refresh_token[:32]
                ttl = int(cls.REFRESH_TTL.total_seconds())
                redis_client.setex(f"refresh:{fingerprint}", ttl, str(user_id))
        except Exception:
            pass  # Redis 不可用时不阻断登录

    @classmethod
    def revoke_refresh_token(cls, refresh_token: str) -> bool:
        """撤销 Refresh Token（登出）

        Args:
            refresh_token: Refresh Token

        Returns:
            是否成功撤销
        """
        try:
            redis_client = redis_manager.get_sync_client()
            if redis_client:
                fingerprint = refresh_token[:32]
                redis_client.delete(f"refresh:{fingerprint}")
                return True
        except Exception:
            pass
        return False

    @classmethod
    def verify_access_token(cls, token: str) -> Optional[str]:
        """验证 Access Token

        Args:
            token: Access Token

        Returns:
            用户ID 或 None（验证失败）
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[TokenPair]:
        """使用 Refresh Token 刷新 Access Token

        Args:
            refresh_token: Refresh Token

        Returns:
            新的 TokenPair 或 None（刷新失败）
        """
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # 验证 Refresh Token 是否在 Redis 中（未被撤销）
            if not cls._is_refresh_token_valid(refresh_token):
                return None

            # 创建新的 Token 对
            return cls.create_token_pair(user_id)

        except JWTError:
            return None

    @classmethod
    def _is_refresh_token_valid(cls, refresh_token: str) -> bool:
        """检查 Refresh Token 是否有效（未被撤销）"""
        try:
            redis_client = redis_manager.get_sync_client()
            if redis_client:
                fingerprint = refresh_token[:32]
                return redis_client.exists(f"refresh:{fingerprint}") > 0
        except Exception:
            pass
        # Redis 不可用时，直接通过 JWT 验证
        return True
