"""
应用配置模块
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础信息
    APP_NAME: str = "起了吗App"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "为独居人群提供紧急医疗救助服务"
    DEBUG: bool = True
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./qilema.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 短信服务配置
    SMS_ACCESS_KEY: str = ""
    SMS_SECRET_KEY: str = ""
    
    # 签到配置
    DEFAULT_CHECKIN_HOURS: int = 24
    
    # 紧急求助配置
    SOS_CONTACT_NOTIFY_CHANNELS: List[str] = ["push", "sms"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()
