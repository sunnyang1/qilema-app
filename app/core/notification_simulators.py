"""
通知模拟器模块

提供推送、短信、电话、邮件四种通知渠道的模拟实现
用于开发、测试环境，不依赖真实第三方SDK
"""

import time
import random
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from app.schemas.notification import NotificationChannelEnum
from app.core.config import settings


logger = logging.getLogger(__name__)


class NotificationSimulator(ABC):
    """通知模拟器基类"""

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000
    ):
        """
        初始化模拟器

        Args:
            enabled: 是否启用
            success_rate: 成功率（0-100），默认100%
            delay_ms: 模拟延迟（毫秒），默认0
            max_retries: 最大重试次数，默认3次
            retry_interval_ms: 重试间隔（毫秒），默认1000ms
        """
        self.enabled = enabled
        self.success_rate = max(0.0, min(100.0, success_rate))
        self.delay_ms = delay_ms
        self.max_retries = max_retries
        self.retry_interval_ms = retry_interval_ms
        self.retryable_errors = ["network_error", "timeout", "service_unavailable"]

    @abstractmethod
    def _send(self, **kwargs) -> Dict[str, Any]:
        """
        发送通知的具体实现（由子类实现）

        Returns:
            dict: 包含status, message, data等字段
        """
        pass

    def send(self, **kwargs) -> Dict[str, Any]:
        """
        发送通知（带重试和延迟模拟）

        Args:
            **kwargs: 通知参数

        Returns:
            dict: 发送结果，包含status, message, data等字段
        """
        if not self.enabled:
            logger.warning(f"{self.__class__.__name__}服务未启用")
            return {
                "status": "disabled",
                "message": f"{self.__class__.__name__}服务未启用"
            }

        # 模拟延迟
        if self.delay_ms > 0:
            logger.info(f"{self.__class__.__name__}模拟延迟{self.delay_ms}ms")
            time.sleep(self.delay_ms / 1000.0)

        # 执行重试逻辑
        last_result = None
        for attempt in range(1, self.max_retries + 1):
            result = self._send(**kwargs)

            if result.get("status") == "success":
                logger.info(f"{self.__class__.__name__}发送成功（尝试{attempt}次）")
                return result

            # 判断是否可重试
            if attempt < self.max_retries and self._should_retry(result):
                logger.warning(
                    f"{self.__class__.__name__}发送失败，将在{self.retry_interval_ms}ms后重试（尝试{attempt}/{self.max_retries}）：{result.get('message')}"
                )
                time.sleep(self.retry_interval_ms / 1000.0)
                last_result = result
            else:
                logger.error(f"{self.__class__.__name__}发送失败（尝试{attempt}/{self.max_retries}）：{result.get('message')}")
                return result

        return last_result

    def _should_retry(self, result: Dict[str, Any]) -> bool:
        """
        判断是否应该重试

        Args:
            result: 发送结果

        Returns:
            bool: 是否应该重试
        """
        error_code = result.get("error_code", "")
        return error_code in self.retryable_errors

    def _simulate_success_failure(self) -> bool:
        """
        根据成功率模拟成功或失败

        Returns:
            bool: True表示成功，False表示失败
        """
        return random.random() * 100 < self.success_rate


class PushNotificationSimulator(NotificationSimulator):
    """推送通知模拟器"""

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        push_token: Optional[str] = None
    ):
        """
        初始化推送通知模拟器

        Args:
            push_token: 推送token（可选）
        """
        super().__init__(enabled, success_rate, delay_ms, max_retries, retry_interval_ms)
        self.push_token = push_token

    def _send(
        self,
        user_id: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送推送通知

        Args:
            user_id: 用户ID
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            dict: 发送结果
        """
        if self._simulate_success_failure():
            logger.info(
                f"推送通知成功 - 用户:{user_id}, 标题:{title}, "
                f"内容:{content[:50]}..."
            )
            return {
                "status": "success",
                "message": "推送通知发送成功",
                "data": {
                    "user_id": user_id,
                    "title": title,
                    "content": content,
                    "push_token": self.push_token,
                    "message_id": f"msg_{random.randint(100000, 999999)}"
                }
            }
        else:
            error_types = [
                {"error_code": "device_not_found", "message": "设备不存在或token失效"},
                {"error_code": "rate_limit_exceeded", "message": "推送频率超限"},
                {"error_code": "service_error", "message": "推送服务错误"},
                {"error_code": "network_error", "message": "网络连接失败"},
                {"error_code": "timeout", "message": "请求超时"}
            ]
            error = random.choice(error_types)
            logger.error(
                f"推送通知失败 - 用户:{user_id}, "
                f"错误:{error['message']}"
            )
            return {
                "status": "failed",
                "message": error["message"],
                "error_code": error["error_code"],
                "data": {
                    "user_id": user_id,
                    "error_type": error["error_code"]
                }
            }

    def send_batch(
        self,
        user_ids: List[str],
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量发送推送通知

        Args:
            user_ids: 用户ID列表
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            list: 发送结果列表
        """
        results = []
        for user_id in user_ids:
            result = self.send(user_id=user_id, title=title, content=content, data=data)
            results.append(result)
        return results


class SMSNotificationSimulator(NotificationSimulator):
    """短信通知模拟器"""

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        phone_number: Optional[str] = None
    ):
        """
        初始化短信通知模拟器

        Args:
            phone_number: 默认手机号（用于日志）
        """
        super().__init__(enabled, success_rate, delay_ms, max_retries, retry_interval_ms)
        self.phone_number = phone_number

    def _send(
        self,
        phone_number: str,
        content: str,
        template_code: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送短信通知

        Args:
            phone_number: 手机号
            content: 短信内容
            template_code: 模板代码（可选）
            template_params: 模板参数（可选）

        Returns:
            dict: 发送结果
        """
        # 模板变量替换
        final_content = content
        if template_code and template_params:
            for key, value in template_params.items():
                placeholder = f"{{{{{key}}}}}"
                final_content = final_content.replace(placeholder, str(value))

        # 隐私保护：手机号脱敏
        masked_phone = self._mask_phone_number(phone_number)

        if self._simulate_success_failure():
            logger.info(
                f"短信通知成功 - 手机:{masked_phone}, "
                f"内容:{final_content[:50]}..., "
                f"模板:{template_code or '无模板'}"
            )
            return {
                "status": "success",
                "message": "短信发送成功",
                "data": {
                    "phone_number": phone_number,
                    "masked_phone": masked_phone,
                    "content": final_content,
                    "template_code": template_code,
                    "message_id": f"sms_{random.randint(100000, 999999)}",
                    "cost": 0.05
                }
            }
        else:
            error_types = [
                {"error_code": "insufficient_balance", "message": "短信余额不足"},
                {"error_code": "invalid_phone", "message": "手机号格式错误"},
                {"error_code": "content_sensitive", "message": "短信内容包含敏感词"},
                {"error_code": "rate_limit_exceeded", "message": "短信频率超限"},
                {"error_code": "network_error", "message": "网络连接失败"},
                {"error_code": "timeout", "message": "请求超时"}
            ]
            error = random.choice(error_types)
            logger.error(
                f"短信通知失败 - 手机:{masked_phone}, "
                f"错误:{error['message']}"
            )
            return {
                "status": "failed",
                "message": error["message"],
                "error_code": error["error_code"],
                "data": {
                    "phone_number": phone_number,
                    "masked_phone": masked_phone,
                    "error_type": error["error_code"]
                }
            }

    @staticmethod
    def _mask_phone_number(phone_number: str) -> str:
        """
        手机号脱敏处理

        Args:
            phone_number: 原始手机号

        Returns:
            str: 脱敏后的手机号（保留前3后4位）
        """
        if len(phone_number) > 7:
            return phone_number[:3] + "****" + phone_number[-4:]
        return phone_number


class PhoneNotificationSimulator(NotificationSimulator):
    """电话通知模拟器"""

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        tts_voice: Optional[str] = None
    ):
        """
        初始化电话通知模拟器

        Args:
            tts_voice: TTS语音类型（可选）
        """
        super().__init__(enabled, success_rate, delay_ms, max_retries, retry_interval_ms)
        self.tts_voice = tts_voice

    def _send(
        self,
        phone_number: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送电话通知

        Args:
            phone_number: 手机号
            content: 语音播报内容

        Returns:
            dict: 发送结果
        """
        masked_phone = SMSNotificationSimulator._mask_phone_number(phone_number)

        if self._simulate_success_failure():
            # 模拟接通和挂断
            call_duration = random.randint(5, 30)  # 随机通话时长5-30秒
            logger.info(
                f"电话通知成功 - 手机:{masked_phone}, "
                f"内容:{content[:50]}..., "
                f"通话时长:{call_duration}秒"
            )
            return {
                "status": "success",
                "message": "电话通知发送成功",
                "data": {
                    "phone_number": phone_number,
                    "masked_phone": masked_phone,
                    "content": content,
                    "call_duration": call_duration,
                    "call_id": f"call_{random.randint(100000, 999999)}",
                    "cost": 0.15
                }
            }
        else:
            error_types = [
                {"error_code": "busy", "message": "线路忙"},
                {"error_code": "no_answer", "message": "无人接听"},
                {"error_code": "invalid_phone", "message": "手机号无效"},
                {"error_code": "call_rejected", "message": "拒接"},
                {"error_code": "network_error", "message": "网络连接失败"},
                {"error_code": "timeout", "message": "请求超时"}
            ]
            error = random.choice(error_types)
            logger.error(
                f"电话通知失败 - 手机:{masked_phone}, "
                f"错误:{error['message']}"
            )
            return {
                "status": "failed",
                "message": error["message"],
                "error_code": error["error_code"],
                "data": {
                    "phone_number": phone_number,
                    "masked_phone": masked_phone,
                    "error_type": error["error_code"]
                }
            }

    def call(self, phone_number: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        发送电话通知（兼容方法名）

        Args:
            phone_number: 手机号
            content: 语音播报内容

        Returns:
            dict: 发送结果
        """
        return self.send(phone_number=phone_number, content=content, **kwargs)


class EmailNotificationSimulator(NotificationSimulator):
    """邮件通知模拟器"""

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        smtp_server: Optional[str] = None
    ):
        """
        初始化邮件通知模拟器

        Args:
            smtp_server: SMTP服务器（可选）
        """
        super().__init__(enabled, success_rate, delay_ms, max_retries, retry_interval_ms)
        self.smtp_server = smtp_server

    def _send(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送邮件通知

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 纯文本内容
            html_content: HTML内容（可选）
            attachments: 附件列表（可选）

        Returns:
            dict: 发送结果
        """
        # 邮箱脱敏
        masked_email = self._mask_email(to_email)

        # 使用HTML内容或纯文本
        final_content = html_content if html_content else content

        if self._simulate_success_failure():
            logger.info(
                f"邮件通知成功 - 收件人:{masked_email}, "
                f"主题:{subject}, "
                f"附件数量:{len(attachments or [])}"
            )
            return {
                "status": "success",
                "message": "邮件发送成功",
                "data": {
                    "to_email": to_email,
                    "masked_email": masked_email,
                    "subject": subject,
                    "content": final_content[:100],
                    "has_html": html_content is not None,
                    "attachment_count": len(attachments or []),
                    "message_id": f"email_{random.randint(100000, 999999)}",
                    "size_kb": random.randint(10, 500)
                }
            }
        else:
            error_types = [
                {"error_code": "invalid_email", "message": "邮箱地址无效"},
                {"error_code": "smtp_auth_failed", "message": "SMTP认证失败"},
                {"error_code": "smtp_connection_failed", "message": "SMTP连接失败"},
                {"error_code": "attachment_too_large", "message": "附件过大"},
                {"error_code": "spam_rejected", "message": "邮件被标记为垃圾邮件"},
                {"error_code": "network_error", "message": "网络连接失败"},
                {"error_code": "timeout", "message": "请求超时"}
            ]
            error = random.choice(error_types)
            logger.error(
                f"邮件通知失败 - 收件人:{masked_email}, "
                f"错误:{error['message']}"
            )
            return {
                "status": "failed",
                "message": error["message"],
                "error_code": error["error_code"],
                "data": {
                    "to_email": to_email,
                    "masked_email": masked_email,
                    "error_type": error["error_code"]
                }
            }

    @staticmethod
    def _mask_email(email: str) -> str:
        """
        邮箱脱敏处理

        Args:
            email: 原始邮箱

        Returns:
            str: 脱敏后的邮箱（保留首字母和域名）
        """
        if "@" in email:
            username, domain = email.split("@", 1)
            masked_username = username[0] + "***" if len(username) > 1 else username
            return f"{masked_username}@{domain}"
        return email


class NotificationServiceConfig:
    """通知服务配置管理类"""

    def __init__(self, settings_obj=None):
        """
        初始化通知服务配置

        Args:
            settings_obj: 配置对象，如果为None则使用默认settings
        """
        self.settings = settings_obj or settings

    def get_push_simulator_config(self) -> Dict[str, Any]:
        """
        获取推送通知模拟器配置

        Returns:
            dict: 推送通知配置
        """
        return {
            "enabled": self.settings.NOTIFICATION_PUSH_ENABLED,
            "success_rate": self.settings.NOTIFICATION_PUSH_SUCCESS_RATE,
            "delay_ms": self.settings.NOTIFICATION_PUSH_DELAY_MS,
            "max_retries": self.settings.NOTIFICATION_PUSH_MAX_RETRIES,
            "retry_interval_ms": self.settings.NOTIFICATION_PUSH_RETRY_INTERVAL_MS
        }

    def get_sms_simulator_config(self) -> Dict[str, Any]:
        """
        获取短信通知模拟器配置

        Returns:
            dict: 短信通知配置
        """
        return {
            "enabled": self.settings.NOTIFICATION_SMS_ENABLED,
            "success_rate": self.settings.NOTIFICATION_SMS_SUCCESS_RATE,
            "delay_ms": self.settings.NOTIFICATION_SMS_DELAY_MS,
            "max_retries": self.settings.NOTIFICATION_SMS_MAX_RETRIES,
            "retry_interval_ms": self.settings.NOTIFICATION_SMS_RETRY_INTERVAL_MS
        }

    def get_phone_simulator_config(self) -> Dict[str, Any]:
        """
        获取电话通知模拟器配置

        Returns:
            dict: 电话通知配置
        """
        return {
            "enabled": self.settings.NOTIFICATION_PHONE_ENABLED,
            "success_rate": self.settings.NOTIFICATION_PHONE_SUCCESS_RATE,
            "delay_ms": self.settings.NOTIFICATION_PHONE_DELAY_MS,
            "max_retries": self.settings.NOTIFICATION_PHONE_MAX_RETRIES,
            "retry_interval_ms": self.settings.NOTIFICATION_PHONE_RETRY_INTERVAL_MS
        }

    def get_email_simulator_config(self) -> Dict[str, Any]:
        """
        获取邮件通知模拟器配置

        Returns:
            dict: 邮件通知配置
        """
        return {
            "enabled": self.settings.NOTIFICATION_EMAIL_ENABLED,
            "success_rate": self.settings.NOTIFICATION_EMAIL_SUCCESS_RATE,
            "delay_ms": self.settings.NOTIFICATION_EMAIL_DELAY_MS,
            "max_retries": self.settings.NOTIFICATION_EMAIL_MAX_RETRIES,
            "retry_interval_ms": self.settings.NOTIFICATION_EMAIL_RETRY_INTERVAL_MS
        }

    def is_degradation_enabled(self) -> bool:
        """
        检查降级策略是否启用

        Returns:
            bool: 降级策略是否启用
        """
        return self.settings.NOTIFICATION_DEGRADATION_ENABLED

    def get_channel_priority(self) -> List[str]:
        """
        获取通知渠道优先级

        Returns:
            list: 通知渠道优先级列表
        """
        return self.settings.NOTIFICATION_CHANNEL_PRIORITY


def create_push_simulator(config: Optional[NotificationServiceConfig] = None) -> PushNotificationSimulator:
    """
    创建推送通知模拟器

    Args:
        config: 通知服务配置对象

    Returns:
        PushNotificationSimulator: 推送通知模拟器实例
    """
    if config is None:
        config = NotificationServiceConfig()
    simulator_config = config.get_push_simulator_config()
    return PushNotificationSimulator(**simulator_config)


def create_sms_simulator(config: Optional[NotificationServiceConfig] = None) -> SMSNotificationSimulator:
    """
    创建短信通知模拟器

    Args:
        config: 通知服务配置对象

    Returns:
        SMSNotificationSimulator: 短信通知模拟器实例
    """
    if config is None:
        config = NotificationServiceConfig()
    simulator_config = config.get_sms_simulator_config()
    return SMSNotificationSimulator(**simulator_config)


def create_phone_simulator(config: Optional[NotificationServiceConfig] = None) -> PhoneNotificationSimulator:
    """
    创建电话通知模拟器

    Args:
        config: 通知服务配置对象

    Returns:
        PhoneNotificationSimulator: 电话通知模拟器实例
    """
    if config is None:
        config = NotificationServiceConfig()
    simulator_config = config.get_phone_simulator_config()
    return PhoneNotificationSimulator(**simulator_config)


def create_email_simulator(config: Optional[NotificationServiceConfig] = None) -> EmailNotificationSimulator:
    """
    创建邮件通知模拟器

    Args:
        config: 通知服务配置对象

    Returns:
        EmailNotificationSimulator: 邮件通知模拟器实例
    """
    if config is None:
        config = NotificationServiceConfig()
    simulator_config = config.get_email_simulator_config()
    return EmailNotificationSimulator(**simulator_config)
