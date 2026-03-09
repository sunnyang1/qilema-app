"""
安全工具模块测试

测试密码哈希、JWT令牌、用户认证等安全功能
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    oauth2_scheme,
    verify_password,
)
from app.models.user import User
from fastapi import HTTPException, status


class TestPasswordHashing:
    """密码哈希测试"""

    def test_get_password_hash(self):
        """测试获取密码哈希"""
        password = "test_password_123"

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证哈希不为空
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password

    def test_verify_password_correct(self):
        """测试验证正确的密码"""
        password = "correct_password"

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证密码
        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect(self):
        """测试验证错误的密码"""
        password = "correct_password"
        wrong_password = "wrong_password"

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证错误密码
        result = verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_different_hashes(self):
        """测试不同密码生成不同哈希"""
        password1 = "password_1"
        password2 = "password_2"

        # 生成两个哈希
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        # 验证哈希不同（因为bcrypt的随机盐值）
        assert hash1 != hash2

    def test_verify_password_empty_string(self):
        """测试空字符串密码"""
        password = ""

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证空字符串密码
        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_long_password(self):
        """测试长密码（超过72字节）"""
        # bcrypt最多处理72字节
        password = "a" * 100

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证长密码（只使用前72字节）
        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_special_characters(self):
        """测试包含特殊字符的密码"""
        password = "p@ssw0rd!#$%^&*()"

        # 生成哈希
        hashed = get_password_hash(password)

        # 验证特殊字符密码
        result = verify_password(password, hashed)

        assert result is True


class TestAccessToken:
    """访问令牌测试"""

    def test_create_access_token_default_expiry(self):
        """测试创建默认过期时间的令牌"""
        data = {"sub": "user123", "role": "user"}

        # 创建令牌
        token = create_access_token(data)

        # 验证令牌不为空
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """测试创建自定义过期时间的令牌"""
        data = {"sub": "user123", "role": "user"}
        expires_delta = timedelta(hours=1)

        # 创建令牌
        token = create_access_token(data, expires_delta)

        # 验证令牌不为空
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_different_data(self):
        """测试创建不同数据的令牌"""
        data1 = {"sub": "user1", "role": "admin"}
        data2 = {"sub": "user2", "role": "user"}

        # 创建两个令牌
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)

        # 验证令牌不同
        assert token1 != token2

    def test_decode_access_token_valid(self):
        """测试解码有效的令牌"""
        data = {"sub": "user123", "role": "admin"}

        # 创建令牌
        token = create_access_token(data)

        # 解码令牌
        payload = decode_access_token(token)

        # 验证解码结果
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"

    def test_decode_access_token_invalid(self):
        """测试解码无效的令牌"""
        invalid_token = "invalid.token.string"

        # 解码令牌
        payload = decode_access_token(invalid_token)

        # 验证返回None
        assert payload is None

    def test_decode_access_token_empty_string(self):
        """测试解码空字符串令牌"""
        # 解码空令牌
        payload = decode_access_token("")

        # 验证返回None
        assert payload is None

    def test_access_token_contains_expiry(self):
        """测试令牌包含过期时间"""
        data = {"sub": "user123"}

        # 创建令牌
        token = create_access_token(data)

        # 解码令牌
        payload = decode_access_token(token)

        # 验证包含exp字段
        assert "exp" in payload

        # 验证过期时间在未来
        exp_timestamp = payload["exp"]
        current_timestamp = datetime.utcnow().timestamp()
        assert exp_timestamp > current_timestamp


class TestGetCurrentUser:
    """获取当前用户测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库"""
        db = Mock()
        return db

    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = Mock(spec=User)
        user.user_id = "test_user_id"
        user.username = "test_user"
        return user

    @pytest.fixture
    def valid_token(self):
        """有效的访问令牌"""
        data = {"sub": "test_user_id"}
        return create_access_token(data)

    @pytest.fixture
    def invalid_token(self):
        """无效的访问令牌"""
        return "invalid_token_string"

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_db, mock_user, valid_token):
        """测试成功获取当前用户"""
        # 模拟数据库查询返回用户
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query

        # 获取当前用户
        user = await get_current_user(token=valid_token, db=mock_db)

        # 验证返回用户
        assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db, invalid_token):
        """测试无效令牌"""
        # 验证抛出HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=mock_db)

        # 验证状态码
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_no_sub_in_payload(self, mock_db):
        """测试令牌中没有sub字段"""
        # 创建没有sub字段的令牌
        data = {"role": "admin"}
        token = create_access_token(data)

        # 验证抛出HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)

        # 验证状态码
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, mock_db, valid_token):
        """测试用户不存在"""
        # 模拟数据库查询返回None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # 验证抛出HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=valid_token, db=mock_db)

        # 验证状态码
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenExpiry:
    """令牌过期测试"""

    def test_expired_token(self):
        """测试过期的令牌"""
        # 创建一个已经过期的令牌
        data = {"sub": "user123"}
        expires_delta = timedelta(seconds=-1)  # 过去1秒
        token = create_access_token(data, expires_delta)

        # 解码过期令牌
        payload = decode_access_token(token)

        # 验证返回None
        assert payload is None

    def test_expiring_soon_token(self):
        """测试即将过期的令牌"""
        # 创建一个即将过期的令牌
        data = {"sub": "user123"}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta)

        # 解码令牌
        payload = decode_access_token(token)

        # 验证仍然可以解码（但即将过期）
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_long_expiration_token(self):
        """测试长过期时间的令牌"""
        # 创建一个长时间有效的令牌
        data = {"sub": "user123"}
        expires_delta = timedelta(days=30)
        token = create_access_token(data, expires_delta)

        # 解码令牌
        payload = decode_access_token(token)

        # 验证解码成功
        assert payload is not None

        # 验证过期时间在未来30天左右
        exp_timestamp = payload["exp"]
        current_timestamp = datetime.utcnow().timestamp()
        time_until_expiry = exp_timestamp - current_timestamp

        # 30天 = 2592000秒，验证过期时间在未来
        assert time_until_expiry > 2580000  # 约等于30天


class TestOAuth2Scheme:
    """OAuth2方案测试"""

    def test_oauth2_scheme_initialized(self):
        """测试OAuth2方案初始化"""
        # 验证scheme对象存在
        assert oauth2_scheme is not None
        # 验证scheme_name属性
        assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
