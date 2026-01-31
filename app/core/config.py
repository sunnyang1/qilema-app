"""
应用配置模块
"""
import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置类"""

    # ========== 环境配置 ==========
    ENVIRONMENT: str = "development"

    # ========== 应用基础信息 ==========
    APP_NAME: str = "起了吗App"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "为独居人群提供紧急医疗救助服务"

    # ========== 调试模式 ==========
    DEBUG: bool = False  # 默认False，根据ENVIRONMENT自动设置

    # ========== API配置 ==========
    API_V1_PREFIX: str = "/api/v1"

    # ========== CORS配置 ==========
    # 使用Union类型，接受字符串（环境变量）或列表（直接赋值）
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]
    CORS_ALLOW_METHODS: Union[str, List[str]] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: Union[str, List[str]] = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
    ]

    # ========== 数据库配置 ==========
    DATABASE_URL: str = "sqlite:///./qilema.db"

    # ========== JWT配置 ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ========== Redis配置 ==========
    REDIS_URL: str = "redis://localhost:6379/0"

    # ========== 短信服务配置 ==========
    SMS_ACCESS_KEY: str = ""
    SMS_SECRET_KEY: str = ""

    # ========== 签到配置 ==========
    DEFAULT_CHECKIN_HOURS: int = 24

    # ========== 紧急求助配置 ==========
    SOS_CONTACT_NOTIFY_CHANNELS: List[str] = ["push", "sms"]

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境变量是否为有效值

        Args:
            v: 环境变量值

        Returns:
            str: 验证通过的环境变量值

        Raises:
            ValueError: 当环境变量不是有效值时抛出
        """
        valid_envs = ["development", "testing", "production"]
        if v not in valid_envs:
            raise ValueError(f"ENVIRONMENT必须是: {', '.join(valid_envs)}")
        return v

    @field_validator("DEBUG", mode="before")
    @classmethod
    def set_debug_by_environment(cls, v, info) -> bool:
        """根据环境自动设置DEBUG模式

        Args:
            v: DEBUG值（字符串或布尔值）
            info: Pydantic验证信息对象

        Returns:
            bool: DEBUG值（根据环境自动设置）
        """
        # 记录是否显式设置了DEBUG
        explicitly_set = v is not None

        # 转换输入为布尔值
        if isinstance(v, str):
            v = v.lower() in ("true", "1", "yes", "on")
        elif v is None:
            v = False

        # 如果未显式设置DEBUG，根据环境自动设置
        if not explicitly_set:
            environment = info.data.get("ENVIRONMENT")
            if environment in ["development", "testing"]:
                v = True
            elif environment == "production":
                v = False

        # 如果显式设置了DEBUG为True，验证是否允许
        environment = info.data.get("ENVIRONMENT")
        if environment == "production" and v:
            raise ValueError("生产环境不能开启DEBUG模式")

        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v, info) -> List[str]:
        """解析CORS来源配置

        Args:
            v: CORS_ORIGINS值（字符串或列表）
            info: Pydantic验证信息对象

        Returns:
            List[str]: 解析后的CORS来源列表
        """
        # 如果是字符串，按逗号分隔
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            origins = v
        else:
            origins = []

        # 生产环境验证：不能使用通配符
        if info.data.get("ENVIRONMENT") == "production":
            if "*" in origins or (len(origins) == 1 and origins[0] == "*"):
                raise ValueError("生产环境CORS_ORIGINS不能使用通配符")

        return origins

    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def parse_cors_allow_methods(cls, v, info) -> List[str]:
        """解析允许的HTTP方法配置

        Args:
            v: CORS_ALLOW_METHODS值（字符串或列表）
            info: Pydantic验证信息对象

        Returns:
            List[str]: 解析后的允许方法列表
        """
        # 如果是字符串，按逗号分隔
        if isinstance(v, str):
            methods = [method.strip().upper() for method in v.split(",")]
        elif isinstance(v, list):
            methods = [str(method).upper() for method in v]
        else:
            methods = []

        # 生产环境验证：不能使用通配符
        if info.data.get("ENVIRONMENT") == "production":
            if "*" in methods or (len(methods) == 1 and methods[0] == "*"):
                raise ValueError("生产环境CORS_ALLOW_METHODS不能使用通配符")

        return methods

    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_cors_allow_headers(cls, v, info) -> List[str]:
        """解析允许的HTTP头部配置

        Args:
            v: CORS_ALLOW_HEADERS值（字符串或列表）
            info: Pydantic验证信息对象

        Returns:
            List[str]: 解析后的允许头部列表
        """
        # 如果是字符串，按逗号分隔
        if isinstance(v, str):
            headers = [header.strip() for header in v.split(",")]
        elif isinstance(v, list):
            headers = [str(header).strip() for header in v]
        else:
            headers = []

        # 生产环境验证：不能使用通配符
        if info.data.get("ENVIRONMENT") == "production":
            if "*" in headers or (len(headers) == 1 and headers[0] == "*"):
                raise ValueError("生产环境CORS_ALLOW_HEADERS不能使用通配符")

        return headers

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """验证SECRET_KEY是否安全

        Args:
            v: SECRET_KEY值
            info: Pydantic验证信息对象

        Returns:
            str: 验证通过的SECRET_KEY值

        Raises:
            ValueError: 当SECRET_KEY不安全时抛出
        """
        # 检查是否是默认值
        default_key = "your-secret-key-change-in-production"
        if v == default_key:
            raise ValueError(
                "SECRET_KEY不能使用默认值。"
                f"请使用以下命令生成强随机密钥: python scripts/generate_secret_key.py"
            )

        # 检查最小长度（64字节）
        min_length = 64
        key_bytes = v.encode('utf-8')
        if len(key_bytes) < min_length:
            raise ValueError(
                f"SECRET_KEY长度至少{min_length}字节，"
                f"当前{len(key_bytes)}字节。"
                f"请使用以下命令生成强随机密钥: python scripts/generate_secret_key.py"
            )

        # 生产环境额外检查
        if info.data.get("ENVIRONMENT") == "production":
            # 确保密钥强度足够
            import re
            has_upper = bool(re.search(r'[A-Z]', v))
            has_lower = bool(re.search(r'[a-z]', v))
            has_digit = bool(re.search(r'\d', v))
            has_special = bool(re.search(r'[^A-Za-z0-9]', v))

            char_types = sum([has_upper, has_lower, has_digit, has_special])
            if char_types < 3:
                raise ValueError(
                    f"生产环境SECRET_KEY强度不足，"
                    f"应该包含多种字符类型，当前满足{char_types}种。"
                    f"请使用以下命令生成强随机密钥: python scripts/generate_secret_key.py"
                )

        return v

    def validate_configuration(self) -> List[str]:
        """验证配置的正确性

        Returns:
            List[str]: 错误列表，如果为空则表示配置有效
        """
        errors = []

        # 验证SECRET_KEY
        if self.SECRET_KEY == "your-secret-key-change-in-production":
            errors.append(
                "SECRET_KEY不能使用默认值。"
                f"请使用以下命令生成强随机密钥: python scripts/generate_secret_key.py"
            )

        # 验证DEBUG模式
        if self.ENVIRONMENT == "production" and self.DEBUG:
            errors.append(
                "生产环境不能开启DEBUG模式，这会导致敏感信息泄露。"
                "请在配置文件中设置DEBUG=False"
            )

        # 验证数据库URL格式
        if self.DATABASE_URL and not (
            self.DATABASE_URL.startswith("sqlite:///") or
            self.DATABASE_URL.startswith("postgresql://") or
            self.DATABASE_URL.startswith("mysql://") or
            self.DATABASE_URL.startswith("mongodb://")
        ):
            errors.append(
                f"DATABASE_URL格式无效: {self.DATABASE_URL}。"
                "支持的格式: sqlite:///, postgresql://, mysql://, mongodb://"
            )

        # 生产环境额外验证
        if self.ENVIRONMENT == "production":
            # 验证CORS配置
            if "*" in self.CORS_ORIGINS:
                errors.append(
                    "生产环境CORS_ORIGINS不能使用通配符'*'。"
                    "请明确指定允许的域名列表。"
                )

            if "*" in self.CORS_ALLOW_METHODS:
                errors.append(
                    "生产环境CORS_ALLOW_METHODS不能使用通配符'*'。"
                    "请明确指定允许的HTTP方法。"
                )

            if "*" in self.CORS_ALLOW_HEADERS:
                errors.append(
                    "生产环境CORS_ALLOW_HEADERS不能使用通配符'*'。"
                    "请明确指定允许的HTTP头部。"
                )

            # 验证SECRET_KEY强度
            import re
            has_upper = bool(re.search(r'[A-Z]', self.SECRET_KEY))
            has_lower = bool(re.search(r'[a-z]', self.SECRET_KEY))
            has_digit = bool(re.search(r'\d', self.SECRET_KEY))
            has_special = bool(re.search(r'[^A-Za-z0-9]', self.SECRET_KEY))

            char_types = sum([has_upper, has_lower, has_digit, has_special])
            if char_types < 3:
                errors.append(
                    f"生产环境SECRET_KEY强度不足（仅满足{char_types}种字符类型），"
                    "建议包含大小写字母、数字和特殊字符。"
                    "请使用以下命令生成强随机密钥: python scripts/generate_secret_key.py"
                )

        return errors

    class Config:
        # 优先使用测试环境的.env文件
        if os.path.exists(".env.testing"):
            env_file = ".env.testing"
        else:
            env_file = ".env"
        case_sensitive = True
        # 环境变量优先于.env文件
        env_file_encoding = "utf-8"
        # 环境变量覆盖.env文件中的值
        env_prefix = ""


# 创建配置实例
settings = Settings()
