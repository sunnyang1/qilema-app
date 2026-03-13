"""
通知发送服务

负责通知的发送逻辑，包含重试机制和降级策略
使用 CircuitBreakerService 防止服务雪崩
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.core.notification_simulators import (
    NotificationServiceConfig,
    create_email_simulator,
    create_phone_simulator,
    create_push_simulator,
    create_sms_simulator,
)
from app.schemas.notification import NotificationChannelEnum
from app.services.notification.circuit_breaker_service import CircuitBreakerService

logger = logging.getLogger(__name__)


class NotificationSenderService:
    """
    通知发送服务

    负责通知的发送逻辑：
    - 支持多种通知渠道（PUSH、SMS、PHONE、EMAIL）
    - 包含重试机制
    - 支持降级策略
    - 使用熔断器防止服务雪崩

    使用示例:
        >>> sender = NotificationSenderService()
        >>> result = sender.send_with_retry(
        ...     channel="sms",
        ...     phone_number="13800138000",
        ...     content="验证码: 123456"
        ... )
    """

    def __init__(
        self,
        config: Optional[NotificationServiceConfig] = None,
        circuit_breaker: Optional[CircuitBreakerService] = None,
    ):
        """
        初始化通知发送服务

        Args:
            config: 通知服务配置对象，如果为None则使用默认配置
            circuit_breaker: 熔断器服务，如果为None则创建新实例
        """
        self.config = config or NotificationServiceConfig()

        # 重试配置
        self.max_retries = self.config.get_max_retries()
        self.retry_delays = self.config.get_retry_delays()

        # 熔断器
        self.circuit_breaker = circuit_breaker or CircuitBreakerService(self.config)

        # 初始化通知模拟器
        self.push_simulator = create_push_simulator(self.config)
        self.sms_simulator = create_sms_simulator(self.config)
        self.phone_simulator = create_phone_simulator(self.config)
        self.email_simulator = create_email_simulator(self.config)

    def send_with_retry(
        self,
        channel: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        带重试机制的通知发送

        Args:
            channel: 通知渠道（push、sms、phone、email）
            **kwargs: 通知参数（根据渠道不同）

        Returns:
            dict: 发送结果 {"success": bool, "error": str}
        """
        channel_str = str(channel)

        for attempt in range(self.max_retries):
            # 记录重试日志
            if attempt > 0:
                delay = (
                    self.retry_delays[attempt - 1]
                    if attempt - 1 < len(self.retry_delays)
                    else 5
                )
                logger.info(
                    f"通知重试（渠道: {channel_str}，"
                    f"重试次数: {attempt}/{self.max_retries}，"
                    f"延迟: {delay}s）"
                )
                time.sleep(delay)

            try:
                result = self._try_send(channel_str, **kwargs)

                if result["success"]:
                    # 发送成功，重置熔断器
                    self.circuit_breaker.record_success(channel_str)
                    logger.info(f"通知发送成功（渠道: {channel_str}，" f"尝试次数: {attempt + 1}）")
                    return result
                else:
                    # 发送失败，记录日志
                    logger.warning(
                        f"通知发送失败（渠道: {channel_str}，"
                        f"尝试次数: {attempt + 1}/{self.max_retries}）: "
                        f"{result['error']}"
                    )
                    if attempt == self.max_retries - 1:
                        # 最后一次重试失败，记录熔断器失败
                        self.circuit_breaker.record_failure(channel_str)
                        return result
                    # 不是最后一次重试，继续重试

            except Exception as e:
                # 发送异常，记录日志
                logger.error(
                    f"通知发送异常（渠道: {channel_str}，"
                    f"尝试次数: {attempt + 1}/{self.max_retries}）: {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    # 最后一次重试失败，记录熔断器失败
                    self.circuit_breaker.record_failure(channel_str)
                    return {"success": False, "error": str(e)}
                # 不是最后一次重试，继续重试

        # 所有重试都失败
        return {"success": False, "error": f"重试 {self.max_retries} 次后仍然失败"}

    def send_with_degradation(
        self,
        initial_channel: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        使用降级策略发送通知

        如果初始渠道发送失败，按照优先级尝试其他渠道

        Args:
            initial_channel: 初始通知渠道
            **kwargs: 通知参数

        Returns:
            dict: 发送结果，包含实际使用的渠道
        """
        # 获取渠道优先级
        channel_priority = self.config.get_channel_priority()
        initial_channel_str = str(initial_channel)

        # 首先尝试初始渠道（带重试）
        if self.circuit_breaker.check(initial_channel_str):
            result = self.send_with_retry(initial_channel_str, **kwargs)
            if result["success"]:
                logger.info(f"通知发送成功（使用渠道: {initial_channel_str}）")
                return {**result, "channel_used": initial_channel_str}
            # 初始渠道失败，记录日志
            logger.warning(f"初始渠道发送失败（渠道: {initial_channel_str}）: {result['error']}")
        else:
            logger.warning(f"初始渠道熔断，跳过（渠道: {initial_channel_str}）")

        # 初始渠道失败，按照优先级尝试其他渠道（带重试）
        for channel in channel_priority:
            # 跳过已尝试的初始渠道
            if channel == initial_channel_str:
                continue

            # 记录降级日志
            logger.info(f"通知降级：尝试渠道 {channel}")

            # 检查熔断器状态
            if not self.circuit_breaker.check(channel):
                logger.warning(f"渠道熔断，跳过（渠道: {channel}）")
                continue

            # 尝试通过当前渠道发送（带重试）
            result = self.send_with_retry(channel, **kwargs)

            if result["success"]:
                logger.info(f"通知发送成功（使用渠道: {channel}）")
                return {**result, "channel_used": channel}
            else:
                # 发送失败，继续尝试下一个渠道
                logger.warning(f"通知发送失败（渠道: {channel}）: {result['error']}")
                continue

        # 所有渠道都失败了
        return {
            "success": False,
            "error": "所有通知渠道都发送失败",
            "channel_used": None,
        }

    def _try_send(self, channel: str, **kwargs) -> Dict[str, Any]:
        """
        尝试通过指定渠道发送通知

        Args:
            channel: 通知渠道
            **kwargs: 通知参数

        Returns:
            dict: 包含success和error字段的结果字典
        """
        try:
            if channel == NotificationChannelEnum.PUSH.value:
                return self._send_push(**kwargs)
            elif channel == NotificationChannelEnum.SMS.value:
                return self._send_sms(**kwargs)
            elif channel == NotificationChannelEnum.PHONE.value:
                return self._send_phone(**kwargs)
            elif channel == NotificationChannelEnum.EMAIL.value:
                return self._send_email(**kwargs)
            else:
                raise ValueError(f"不支持的通知渠道: {channel}")
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_push(
        self,
        user_id: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
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
        result = self.push_simulator.send(
            user_id=user_id,
            title=title,
            content=content,
            data=data,
        )
        return {
            "success": result.get("status") == "success",
            "error": result.get("message")
            if result.get("status") != "success"
            else None,
            "data": result.get("data"),
        }

    def _send_sms(
        self,
        phone_number: str,
        content: str,
        template_code: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None,
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
        result = self.sms_simulator.send(
            phone_number=phone_number,
            content=content,
            template_code=template_code,
            template_params=template_params,
        )
        return {
            "success": result.get("status") == "success",
            "error": result.get("message")
            if result.get("status") != "success"
            else None,
            "data": result.get("data"),
        }

    def _send_phone(
        self,
        phone_number: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        发送电话通知

        Args:
            phone_number: 手机号
            content: 语音播报内容

        Returns:
            dict: 发送结果
        """
        result = self.phone_simulator.send(
            phone_number=phone_number,
            content=content,
        )
        return {
            "success": result.get("status") == "success",
            "error": result.get("message")
            if result.get("status") != "success"
            else None,
            "data": result.get("data"),
        }

    def _send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None,
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
        result = self.email_simulator.send(
            to_email=to_email,
            subject=subject,
            content=content,
            html_content=html_content,
            attachments=attachments,
        )
        return {
            "success": result.get("status") == "success",
            "error": result.get("message")
            if result.get("status") != "success"
            else None,
            "data": result.get("data"),
        }
