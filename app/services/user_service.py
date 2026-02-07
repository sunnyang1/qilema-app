"""
用户服务层
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.core.cache import cache, invalidate_cache, cache_result
from app.core.redis import redis_manager
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    """用户服务类"""
    
    model_class = User
    cache_prefix = "user"
    cache_ttl = 300

    def __init__(self, db: Session = None):
        """初始化用户服务
        
        Args:
            db: 数据库会话(可选),为空时使用静态方法模式
        """
        self.db = db

    @staticmethod
    def create_user(db: Session, user_data: dict, verify_code: Optional[str] = None) -> User:
        """创建用户（统一方法）

        Args:
            db: 数据库会话
            user_data: 用户数据字典，包含 phone, password, nickname 等
            verify_code: 验证码（可选），如果提供则验证

        Returns:
            User: 创建的用户对象

        Raises:
            ValueError: 手机号已注册、验证码错误等
        """
        # 兼容不同参数名
        if 'verification_code' in user_data:
            user_data['verify_code'] = user_data.pop('verification_code')
        if verify_code is not None:
            user_data['verify_code'] = verify_code

        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == user_data.get("phone")).first()
        if existing_user:
            raise ValueError("该手机号已注册")

        # 验证码验证（如果提供）
        if user_data.get("verify_code"):
            if not UserService.verify_code(user_data.get("phone"), user_data.get("verify_code")):
                raise ValueError("验证码错误或已过期")

        # 限制密码长度,避免bcrypt超限
        password = user_data.get("password", "123456")
        if len(password) > 72:
            password = password[:72]

        import uuid
        user = User(
            user_id=str(uuid.uuid4()),
            phone=user_data.get("phone"),
            nickname=user_data.get("nickname"),
            password_hash=get_password_hash(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, phone: str, password: str) -> dict:
        """用户登录并生成token（实例方法）

        Args:
            phone: 手机号
            password: 密码

        Returns:
            dict: 包含access_token, token_type, user的字典

        Raises:
            ValueError: 用户不存在或密码错误
        """
        user = UserService.login_user(self.db, phone, password)

        # 生成JWT token
        from app.core.security import create_access_token
        access_token = create_access_token(data={"sub": user.user_id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }

    @staticmethod
    def login_user(db: Session, phone: str, password: str) -> User:
        """用户登录并更新登录时间（静态方法）

        Args:
            db: 数据库会话
            phone: 手机号
            password: 密码

        Returns:
            User: 用户对象

        Raises:
            ValueError: 用户不存在或密码错误
        """
        user = UserService.authenticate_user(db, phone, password)
        if user is None:
            raise ValueError("用户不存在或密码错误")

        # 更新最后登录时间
        user.last_sign_in = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        # 尝试从缓存获取
        from app.core.cache import get_cached
        cached_user_data = get_cached(f"user:id:{user_id}")
        if cached_user_data:
            # 缓存命中，转换为User对象
            try:
                user_dict = cached_user_data
                if isinstance(user_dict, dict):
                    # 从字典创建User对象
                    user = User()
                    for key, value in user_dict.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    return user
            except (AttributeError, KeyError, ValueError) as e:
                # 缓存数据格式错误，继续查询数据库
                pass

        # 查询数据库
        user = db.query(User).filter(User.user_id == user_id).first()
        # 如果找到用户，缓存结果
        if user:
            cache_result(f"user:id:{user_id}", user.to_dict(), ttl=300)
        return user

    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        # 尝试从缓存获取
        from app.core.cache import get_cached
        cached_user_data = get_cached(f"user:phone:{phone}")
        if cached_user_data:
            # 缓存命中，转换为User对象
            try:
                user_dict = cached_user_data
                if isinstance(user_dict, dict):
                    # 从字典创建User对象
                    user = User()
                    for key, value in user_dict.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    return user
            except (AttributeError, KeyError, ValueError) as e:
                # 缓存数据格式错误，继续查询数据库
                pass

        # 查询数据库
        user = db.query(User).filter(User.phone == phone).first()
        # 如果找到用户，缓存结果
        if user:
            cache_result(f"user:phone:{phone}", user.to_dict(), ttl=300)
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, update_data: dict) -> User:
        """更新用户信息"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        for field in ["nickname", "avatar", "email", "bio"]:
            if field in update_data:
                setattr(user, field, update_data[field])

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        # 失效相关缓存
        invalidate_cache(f"user:id:{user_id}")
        if user.phone:
            invalidate_cache(f"user:phone:{user.phone}")

        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """删除用户"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        # 使用缓存装饰器，较短的TTL因为列表可能变化
        @cache(ttl=60, key_prefix="user", key_builder=lambda *args, **kwargs: f"list:{skip}:{limit}")
        def _list_users():
            return db.query(User).offset(skip).limit(limit).all()

        return _list_users()

    @staticmethod
    def authenticate_user(db: Session, phone: str, password: str) -> Optional[User]:
        """用户认证"""
        # 先检查失败的登录尝试
        redis_client = redis_manager.get_sync_client()
        if redis_client:
            fail_count = redis_client.get(f"login_fail:{phone}")
            if fail_count and int(fail_count) >= 5:
                # 登录失败次数过多
                return None

        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            # 记录失败
            if redis_client:
                redis_client.incr(f"login_fail:{phone}")
                redis_client.expire(f"login_fail:{phone}", 1800)  # 30分钟
            return None

        if not verify_password(password, user.password_hash):
            # 记录失败
            if redis_client:
                redis_client.incr(f"login_fail:{phone}")
                redis_client.expire(f"login_fail:{phone}", 1800)  # 30分钟
            return None

        # 登录成功，清除失败计数
        if redis_client:
            redis_client.delete(f"login_fail:{phone}")

        return user

    @staticmethod
    def generate_verify_code(phone: str) -> str:
        """生成验证码"""
        import random
        code = str(random.randint(100000, 999999))
        # 存储到Redis,有效期5分钟
        redis_client = redis_manager.get_sync_client()
        if redis_client:
            redis_client.setex(f"verify_code:{phone}", 300, code)
            # 同时存储一个计数器，防止频繁请求
            redis_client.incr(f"verify_code_count:{phone}")
            redis_client.expire(f"verify_code_count:{phone}", 3600)
        return code

    @staticmethod
    def verify_code(phone: str, code: str) -> bool:
        """验证验证码"""
        redis_client = redis_manager.get_sync_client()
        if not redis_client:
            return True  # 如果没有Redis,测试环境下通过
        stored_code = redis_client.get(f"verify_code:{phone}")
        if not stored_code:
            return False
        if stored_code != code:
            return False
        # 验证成功后删除验证码
        invalidate_cache(f"verify_code:{phone}")
        return True

    @staticmethod
    def check_verify_code_limit(phone: str) -> bool:
        """检查验证码请求限制（防止刷验证码）

        Args:
            phone: 手机号

        Returns:
            bool: True表示可以请求，False表示已超过限制
        """
        redis_client = redis_manager.get_sync_client()
        if not redis_client:
            return True  # 没有Redis时不限制

        count = redis_client.get(f"verify_code_count:{phone}")
        if count and int(count) >= 10:
            # 1小时内请求超过10次
            return False

        return True
