"""
安全工具模块
"""

from datetime import datetime, timedelta
from typing import Any, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # bcrypt的checkpw需要bytes类型
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # bcrypt最多处理72字节的密码
    password_bytes = password.encode("utf-8")[:72]
    # 生成盐值并哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌（显式验证过期时间）"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},  # 显式验证过期时间
        )
        return payload
    except JWTError:
        return None


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _user_from_access_token(token: str, db: Session) -> Optional[Any]:
    """由 Bearer token 解析并加载 User；token 无效或用户不存在时返回 None。"""
    from app.models.user import User

    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return db.query(User).filter(User.user_id == user_id).first()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Any:
    """
    获取当前用户（返回 ORM 对象）

    Returns:
        Any: 用户 ORM 对象

    Raises:
        HTTPException: 当 token 无效或用户不存在时
    """
    user = _user_from_access_token(token, db)
    if user is None:
        raise _credentials_exception()
    return user


async def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Any:
    """
    获取当前活跃用户（验证账号状态）

    Returns:
        Any: 用户 ORM 对象（已激活）

    Raises:
        HTTPException: 当 token 无效、用户不存在或用户未激活时
    """
    user = _user_from_access_token(token, db)
    if user is None:
        raise _credentials_exception()
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户账号未激活")
    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Any:
    """
    获取当前管理员用户

    Returns:
        Any: 用户 ORM 对象（管理员权限）

    Raises:
        HTTPException: 当 token 无效、用户不存在或无管理员权限时
    """
    user = _user_from_access_token(token, db)
    if user is None:
        raise _credentials_exception()
    if user.user_id not in settings.ADMIN_USER_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user
