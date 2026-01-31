import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserRegister, UserLogin
from datetime import datetime
from unittest.mock import Mock, patch
import redis

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_redis():
    """Mock Redis客户端"""
    with patch('app.services.user_service.redis_manager') as mock_redis_mgr:
        with patch('app.services.user_service.redis_manager.check_health', return_value=True):
            mock_client = Mock()
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            mock_client.delete.return_value = True
            mock_redis_mgr.get_sync_client.return_value = mock_client
            yield mock_client

class TestUserService:
    """用户服务测试"""
    
    def test_register_user_success(self, db, mock_redis):
        """测试用户注册成功"""
        # Mock验证码验证
        mock_redis.get.return_value = "123456"

        register_data = UserRegister(
            phone="13800138000",
            password="123456",
            verify_code="123456",
            nickname="测试用户"
        )

        user = UserService.create_user(db, register_data.model_dump())

        assert user.phone == "13800138000"
        assert user.nickname == "测试用户"
        assert user.user_id is not None
        assert user.password_hash != "123456"  # 密码应该被哈希
    
    def test_register_user_duplicate_phone(self, db, mock_redis):
        """测试注册重复手机号"""
        mock_redis.get.return_value = "123456"

        register_data = UserRegister(
            phone="13800138001",
            password="123456",
            verify_code="123456"
        )

        # 第一次注册成功
        UserService.create_user(db, register_data.model_dump())

        # 第二次注册应该失败
        with pytest.raises(ValueError, match="手机号已注册"):
            UserService.create_user(db, register_data.model_dump())
    
    def test_register_user_invalid_code(self, db, mock_redis):
        """测试注册时验证码错误"""
        mock_redis.get.return_value = "654321"  # 返回不同的验证码

        register_data = UserRegister(
            phone="13800138002",
            password="123456",
            verify_code="123456"  # 用户输入错误的验证码
        )

        with pytest.raises(ValueError, match="验证码错误或已过期"):
            UserService.create_user(db, register_data.model_dump())
    
    def test_login_user_success(self, db, mock_redis):
        """测试用户登录成功"""
        mock_redis.get.return_value = "123456"

        # 先注册用户
        register_data = UserRegister(
            phone="13800138003",
            password="123456",
            verify_code="123456"
        )
        UserService.create_user(db, register_data.model_dump())

        # 登录
        user = UserService.login_user(db, phone="13800138003", password="123456")

        assert user.phone == "13800138003"
        assert user.last_sign_in is not None
    
    def test_login_user_wrong_password(self, db, mock_redis):
        """测试登录时密码错误"""
        mock_redis.get.return_value = "123456"

        # 注册用户
        register_data = UserRegister(
            phone="13800138004",
            password="123456",
            verify_code="123456"
        )
        UserService.create_user(db, register_data.model_dump())

        # 使用错误密码登录
        with pytest.raises(ValueError, match="密码错误"):
            UserService.login_user(db, phone="13800138004", password="wrongpw")
    
    def test_login_user_not_exist(self, db):
        """测试登录用户不存在"""
        with pytest.raises(ValueError, match="用户不存在"):
            UserService.login_user(db, phone="13800138005", password="123456")
    
    def test_generate_verify_code(self, mock_redis):
        """测试生成验证码"""
        code = UserService.generate_verify_code("13800138006")
        
        assert code is not None
        assert len(code) == 6
        assert code.isdigit()
        mock_redis.setex.assert_called_once()
    
    def test_verify_code_success(self, mock_redis):
        """测试验证码验证成功"""
        mock_redis.get.return_value = "123456"

        with patch('app.services.user_service.invalidate_cache') as mock_invalidate:
            result = UserService.verify_code("13800138007", "123456")

            assert result is True
            # verify_code 应该调用 invalidate_cache
            mock_invalidate.assert_called_once_with("verify_code:13800138007")
    
    def test_verify_code_failure(self, mock_redis):
        """测试验证码验证失败"""
        mock_redis.get.return_value = None
        
        result = UserService.verify_code("13800138008", "123456")
        
        assert result is False

class TestUserModel:
    """用户模型测试"""
    
    def test_user_to_dict(self, db):
        """测试用户模型转换为字典"""
        user = User(
            user_id="test-id",
            phone="13800138009",
            password_hash="hashed_password",
            nickname="测试用户"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["user_id"] == "test-id"
        assert user_dict["phone"] == "13800138009"
        assert user_dict["nickname"] == "测试用户"
        assert "password_hash" not in user_dict  # 不应该包含密码哈希