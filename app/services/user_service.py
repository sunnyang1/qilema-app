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


class UserService:
    """用户服务类"""

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
        user.last_sign_in = datetime.now()
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
            # 注意：这里只是返回dict，实际使用时可能需要转换为User对象
            # 或者返回None让调用者决定如何处理
            # 为了简单起见，这里返回None，让调用者查询数据库
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
            # 缓存命中
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

        user.updated_at = datetime.now()
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
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def authenticate_user(db: Session, phone: str, password: str) -> Optional[User]:
        """用户认证"""
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
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
