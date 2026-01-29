"""
应用配置模块
"""
import os
from typing import List, Optional
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
    DEBUG: bool = True

    # ========== API配置 ==========
    API_V1_PREFIX: str = "/api/v1"

    # ========== CORS配置 ==========
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
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

    @field_validator("DEBUG")
    @classmethod
    def validate_debug_for_production(cls, v: bool, info) -> bool:
        """生产环境必须关闭DEBUG模式

        Args:
            v: DEBUG值
            info: Pydantic验证信息对象

        Returns:
            bool: 验证通过的DEBUG值

        Raises:
            ValueError: 当生产环境开启DEBUG时抛出
        """
        if info.data.get("ENVIRONMENT") == "production" and v:
            raise ValueError("生产环境不能开启DEBUG模式")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
