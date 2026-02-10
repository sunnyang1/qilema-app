"""
通知适配器工厂

提供统一的适配器创建接口，支持通过环境变量切换模拟器/真实服务
"""

import logging
import os
from typing import Dict, Any, Optional

from app.core.notification_simulators import (
    SMSNotificationSimulator,
    PushNotificationSimulator,
    PhoneNotificationSimulator,
    EmailNotificationSimulator
)
from app.core.adapters.aliyun_sms_adapter import AliyunSMSAdapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """通知适配器工厂类"""
    
    @staticmethod
    def create_sms_adapter(config: Optional[Dict[str, Any]] = None) -> SMSNotificationSimulator:
        """创建短信适配器
        
        根据环境变量SMS_USE_REAL_SERVICE决定使用真实服务还是模拟器
        
        Args:
            config: 配置字典
            
        Returns:
            SMSNotificationSimulator: 短信适配器实例
        """
        use_real = os.getenv("SMS_USE_REAL_SERVICE", "false").lower() == "true"
        
        if use_real:
            logger.info("使用阿里云短信真实服务")
            return AliyunSMSAdapter(**(config or {}))
        else:
            logger.info("使用短信模拟器")
            return SMSNotificationSimulator(**(config or {}))
    
    @staticmethod
    def create_push_adapter(config: Optional[Dict[str, Any]] = None) -> PushNotificationSimulator:
        """创建推送适配器
        
        Args:
            config: 配置字典
            
        Returns:
            PushNotificationSimulator: 推送适配器实例
        """
        use_real = os.getenv("PUSH_USE_REAL_SERVICE", "false").lower() == "true"
        
        if use_real:
            logger.info("使用极光推送真实服务")
            from app.core.adapters.jpush_adapter import JPushAdapter
            return JPushAdapter(**(config or {}))
        else:
            logger.info("使用推送模拟器")
            return PushNotificationSimulator(**(config or {}))
    
    @staticmethod
    def create_phone_adapter(config: Optional[Dict[str, Any]] = None) -> PhoneNotificationSimulator:
        """创建电话适配器
        
        Args:
            config: 配置字典
            
        Returns:
            PhoneNotificationSimulator: 电话适配器实例
        """
        use_real = os.getenv("PHONE_USE_REAL_SERVICE", "false").lower() == "true"
        
        if use_real:
            logger.info("使用阿里云语音真实服务")
            from app.core.adapters.aliyun_voice_adapter import AliyunVoiceAdapter
            return AliyunVoiceAdapter(**(config or {}))
        else:
            logger.info("使用电话模拟器")
            return PhoneNotificationSimulator(**(config or {}))
    
    @staticmethod
    def create_email_adapter(config: Optional[Dict[str, Any]] = None) -> EmailNotificationSimulator:
        """创建邮件适配器
        
        Args:
            config: 配置字典
            
        Returns:
            EmailNotificationSimulator: 邮件适配器实例
        """
        use_real = os.getenv("EMAIL_USE_REAL_SERVICE", "false").lower() == "true"
        
        if use_real:
            logger.info("使用SendGrid真实邮件服务")
            from app.core.adapters.sendgrid_adapter import SendGridAdapter
            return SendGridAdapter(**(config or {}))
        else:
            logger.info("使用邮件模拟器")
            return EmailNotificationSimulator(**(config or {}))


def get_adapter_config(channel: str) -> Dict[str, Any]:
    """从环境变量获取适配器配置
    
    Args:
        channel: 渠道名称（sms, push, phone, email）
        
    Returns:
        dict: 配置字典
    """
    prefix = f"NOTIFICATION_{channel.upper()}_"
    
    config = {
        "enabled": os.getenv(f"{prefix}ENABLED", "true").lower() == "true",
        "success_rate": float(os.getenv(f"{prefix}SUCCESS_RATE", "100.0")),
        "delay_ms": int(os.getenv(f"{prefix}DELAY_MS", "0")),
        "max_retries": int(os.getenv(f"{prefix}MAX_RETRIES", "3")),
        "retry_interval_ms": int(os.getenv(f"{prefix}RETRY_INTERVAL_MS", "1000"))
    }
    
    # 渠道特定配置
    if channel == "sms":
        config.update({
            "access_key_id": os.getenv("ALIYUN_ACCESS_KEY_ID"),
            "access_key_secret": os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
            "region_id": os.getenv("ALIYUN_SMS_REGION", "cn-hangzhou"),
            "sign_name": os.getenv("ALIYUN_SMS_SIGN_NAME")
        })
    elif channel == "push":
        config.update({
            "push_token": os.getenv("PUSH_TOKEN")
        })
    elif channel == "phone":
        config.update({
            "tts_voice": os.getenv("TTS_VOICE")
        })
    elif channel == "email":
        config.update({
            "smtp_server": os.getenv("SMTP_SERVER")
        })
    
    return config
