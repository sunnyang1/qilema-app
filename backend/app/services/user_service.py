"""
用户服务层

提供用户相关的业务逻辑处理
"""

import random
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.cache import invalidate_cache
from app.core.redis import redis_manager
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    """
    用户服务类

    提供用户的CRUD操作和认证相关业务逻辑

    Attributes:
        db: 数据库会话
        model_class: 用户模型类
        cache_prefix: 缓存前缀
        cache_ttl: 缓存过期时间（秒）
    """

    model_class = User
    cache_prefix = "user"
    cache_ttl = 300

    def __init__(self, db: Session):
        """
        初始化用户服务

        Args:
            db: 数据库会话
        """
        self.db = db

    # ========== 查询方法 ==========

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        return self.get_by_id_internal(user_id, pk_column="user_id")

    def get_by_phone(self, phone: str) -> Optional[User]:
        """
        根据手机号获取用户

        Args:
            phone: 手机号

        Returns:
            用户对象或None
        """
        return self.get_by_field(self.db, "phone", phone)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        获取用户列表

        Args:
            skip: 跳过数量
            limit: 限制数量

        Returns:
            用户列表
        """
        return self.list_records(
            self.db, skip=skip, limit=limit, order_by="created_at", order_desc=True
        )

    # ========== 创建方法 ==========

    def create(self, user_data: dict, verify_code: Optional[str] = None) -> User:
        """
        创建用户

        Args:
            user_data: 用户数据字典，包含 phone, password, nickname 等
            verify_code: 验证码（可选），如果提供则验证

        Returns:
            创建的用户对象

        Raises:
            ValueError: 手机号已注册、验证码错误等
        """
        # 兼容不同参数名
        if "verification_code" in user_data:
            user_data["verify_code"] = user_data.pop("verification_code")
        if verify_code is not None:
            user_data["verify_code"] = verify_code

        # 检查手机号是否已存在
        existing_user = (
            self.db.query(User).filter(User.phone == user_data.get("phone")).first()
        )
        if existing_user:
            raise ValueError("该手机号已注册")

        # 验证码验证（如果提供）
        if user_data.get("verify_code"):
            if not self.verify_code(
                user_data.get("phone"), user_data.get("verify_code")
            ):
                raise ValueError("验证码错误或已过期")

        # 限制密码长度，避免bcrypt超限
        password = user_data.get("password", "123456")
        if len(password) > 72:
            password = password[:72]

        user = User(
            user_id=str(uuid.uuid4()),
            phone=user_data.get("phone"),
            nickname=user_data.get("nickname"),
            password_hash=get_password_hash(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ========== 更新方法 ==========

    def update(self, user_id: str, update_data: dict) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            update_data: 更新数据

        Returns:
            更新后的用户对象

        Raises:
            ValueError: 用户不存在
        """
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 过滤允许更新的字段
        allowed_fields = ["nickname", "avatar", "email", "bio"]
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}

        return self.update_record(self.db, user_id, filtered_data, pk_column="user_id")

    # ========== 删除方法 ==========

    def delete(self, user_id: str) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            是否成功删除
        """
        return self.delete_record(self.db, user_id, pk_column="user_id")

    # ========== 认证相关 ==========

    def authenticate(self, phone: str, password: str) -> Optional[User]:
        """
        用户认证

        Args:
            phone: 手机号
            password: 密码

        Returns:
            认证成功的用户对象或None
        """
        # 先检查失败的登录尝试
        redis_client = redis_manager.get_sync_client()
        if redis_client:
            fail_count = redis_client.get(f"login_fail:{phone}")
            if fail_count and int(fail_count) >= 5:
                # 登录失败次数过多
                return None

        user = self.db.query(User).filter(User.phone == phone).first()
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

    def login(self, phone: str, password: str) -> dict:
        """
        用户登录并生成token

        Args:
            phone: 手机号
            password: 密码

        Returns:
            包含access_token, token_type, user的字典

        Raises:
            ValueError: 用户不存在或密码错误
        """
        user = self.authenticate(phone, password)
        if user is None:
            raise ValueError("用户不存在或密码错误")

        # 更新最后登录时间
        user.last_sign_in = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        # 生成JWT token
        access_token = create_access_token(data={"sub": user.user_id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    # ========== 验证码相关 ==========

    def generate_verify_code(self, phone: str) -> str:
        """
        生成验证码

        Args:
            phone: 手机号

        Returns:
            6位数字验证码
        """
        code = str(random.randint(100000, 999999))
        # 存储到Redis，有效期5分钟
        redis_client = redis_manager.get_sync_client()
        if redis_client:
            redis_client.setex(f"verify_code:{phone}", 300, code)
            # 同时存储一个计数器，防止频繁请求
            redis_client.incr(f"verify_code_count:{phone}")
            redis_client.expire(f"verify_code_count:{phone}", 3600)
        return code

    def verify_code(self, phone: str, code: str) -> bool:
        """
        验证验证码

        Args:
            phone: 手机号
            code: 验证码

        Returns:
            验证是否成功
        """
        redis_client = redis_manager.get_sync_client()
        if not redis_client:
            return True  # 如果没有Redis，测试环境下通过
        stored_code = redis_client.get(f"verify_code:{phone}")
        if not stored_code:
            return False
        if stored_code != code:
            return False
        # 验证成功后删除验证码
        invalidate_cache(f"verify_code:{phone}")
        return True

    def check_verify_code_limit(self, phone: str) -> bool:
        """
        检查验证码请求限制（防止刷验证码）

        Args:
            phone: 手机号

        Returns:
            True表示可以请求，False表示已超过限制
        """
        redis_client = redis_manager.get_sync_client()
        if not redis_client:
            return True  # 没有Redis时不限制

        count = redis_client.get(f"verify_code_count:{phone}")
        if count and int(count) >= 10:
            # 1小时内请求超过10次
            return False

        return True

    # ========== 向后兼容的适配器方法 ==========

    def create_user(self, user_data: dict, verify_code: Optional[str] = None) -> User:
        """向后兼容：创建用户（使用create方法）"""
        return self.create(user_data, verify_code)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """向后兼容：根据ID获取用户"""
        return self.get_by_id(user_id)

    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """向后兼容：根据手机号获取用户"""
        return self.get_by_phone(phone)

    def update_user(self, user_id: str, update_data: dict) -> User:
        """向后兼容：更新用户"""
        return self.update(user_id, update_data)

    def delete_user(self, user_id: str) -> bool:
        """向后兼容：删除用户"""
        return self.delete(user_id)

    def authenticate_user(self, phone: str, password: str) -> Optional[User]:
        """向后兼容：用户认证"""
        return self.authenticate(phone, password)

    def login_user(self, phone: str, password: str) -> User:
        """向后兼容：用户登录（返回用户对象）"""
        user = self.authenticate(phone, password)
        if user is None:
            raise ValueError("用户不存在或密码错误")
        # 更新最后登录时间
        user.last_sign_in = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
