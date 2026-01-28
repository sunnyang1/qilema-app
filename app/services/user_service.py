"""
用户服务层
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import redis

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.config import settings

# Redis客户端
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
        port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
        db=settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0,
        decode_responses=True
    )
except Exception:
    redis_client = None


class UserService:
    """用户服务类"""

    def __init__(self, db: Session = None):
        """初始化用户服务
        
        Args:
            db: 数据库会话(可选),为空时使用静态方法模式
        """
        self.db = db

    @staticmethod
    def register_user(db: Session, user_data: dict) -> User:
        """用户注册"""
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == user_data.get("phone")).first()
        if existing_user:
            raise ValueError("该手机号已注册")

        # 验证码验证
        verify_code = user_data.get("verify_code")
        if verify_code:
            if not UserService.verify_code(user_data.get("phone"), verify_code):
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
        """用户登录(实例方法)"""
        db = self.db
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            raise ValueError("用户不存在")
        if not verify_password(password, user.password_hash):
            raise ValueError("密码错误")

        # 更新最后登录时间
        user.last_sign_in = datetime.now()
        db.commit()
        db.refresh(user)

        # 生成JWT token
        from app.core.security import create_access_token
        access_token = create_access_token(data={"sub": user.user_id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }

    @staticmethod
    def login_user(db: Session, phone: str, password: str) -> Optional[User]:
        """用户登录"""
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            raise ValueError("用户不存在")
        if not verify_password(password, user.password_hash):
            raise ValueError("密码错误")
        
        # 更新最后登录时间
        user.last_sign_in = datetime.now()
        db.commit()
        db.refresh(user)
        
        return user

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """创建用户"""
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == user_data.get("phone")).first()
        if existing_user:
            raise ValueError("该手机号已注册")

        import uuid
        user = User(
            user_id=str(uuid.uuid4()),
            phone=user_data.get("phone"),
            nickname=user_data.get("nickname"),
            password_hash=get_password_hash(user_data.get("password", "123456")),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return db.query(User).filter(User.phone == phone).first()

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
        if redis_client:
            redis_client.setex(f"verify_code:{phone}", 300, code)
        return code

    @staticmethod
    def verify_code(phone: str, code: str) -> bool:
        """验证验证码"""
        if not redis_client:
            return True  # 如果没有Redis,测试环境下通过
        stored_code = redis_client.get(f"verify_code:{phone}")
        if not stored_code:
            return False
        if stored_code != code:
            return False
        redis_client.delete(f"verify_code:{phone}")
        return True
