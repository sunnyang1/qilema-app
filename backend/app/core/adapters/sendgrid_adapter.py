"""
SendGrid邮件服务适配器

提供SendGrid邮件服务的真实实现，与EmailNotificationSimulator保持相同接口
支持HTML邮件、模板和附件
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.notification_simulators import EmailNotificationSimulator

logger = logging.getLogger(__name__)


class SendGridAdapter(EmailNotificationSimulator):
    """SendGrid邮件服务适配器

    继承EmailNotificationSimulator保持接口兼容
    通过环境变量EMAIL_USE_REAL_SERVICE控制使用真实服务还是模拟器
    """

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        smtp_server: Optional[str] = None,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        """初始化SendGrid适配器

        Args:
            enabled: 是否启用
            success_rate: 成功率（仅模拟器模式使用）
            delay_ms: 模拟延迟（仅模拟器模式使用）
            max_retries: 最大重试次数
            retry_interval_ms: 重试间隔（毫秒）
            smtp_server: SMTP服务器（保留兼容）
            api_key: SendGrid API Key
            from_email: 发件人邮箱
            from_name: 发件人名称
        """
        super().__init__(
            enabled, success_rate, delay_ms, max_retries, retry_interval_ms, smtp_server
        )

        # 检查是否使用真实服务
        self.use_real_service = (
            os.getenv("EMAIL_USE_REAL_SERVICE", "false").lower() == "true"
        )

        # SendGrid配置
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = from_email or os.getenv(
            "SENDGRID_FROM_EMAIL", "noreply@qilema.com"
        )
        self.from_name = from_name or os.getenv("SENDGRID_FROM_NAME", "起了吗App")

        # 发送记录（用于统计和查询）
        self._send_records: List[Dict[str, Any]] = []

        if self.use_real_service:
            self._init_sendgrid_client()

    def _init_sendgrid_client(self):
        """初始化SendGrid客户端"""
        try:
            # 尝试导入SendGrid SDK
            from sendgrid import SendGridAPIClient

            if not self.api_key:
                raise ValueError("SendGrid邮件服务需要配置API Key")

            # 创建客户端
            self._client = SendGridAPIClient(api_key=self.api_key)

            logger.info("SendGrid客户端初始化成功")

        except ImportError:
            logger.warning("SendGrid SDK未安装，将使用模拟器模式。运行: pip install sendgrid")
            self.use_real_service = False
        except Exception as e:
            logger.error(f"SendGrid客户端初始化失败: {e}")
            self.use_real_service = False

    def _send(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 纯文本内容
            html_content: HTML内容
            attachments: 附件路径列表
            template_id: 模板ID（可选）
            template_data: 模板数据（可选）

        Returns:
            dict: 发送结果
        """
        if not self.use_real_service:
            return super()._send(
                to_email, subject, content, html_content, attachments, **kwargs
            )

        return self._send_real(
            to_email,
            subject,
            content,
            html_content,
            attachments,
            template_id,
            template_data,
        )

    def _send_real(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """使用SendGrid真实服务发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 纯文本内容
            html_content: HTML内容
            attachments: 附件路径列表
            template_id: 模板ID
            template_data: 模板数据

        Returns:
            dict: 发送结果
        """
        try:
            import base64

            from sendgrid.helpers.mail import (
                Attachment,
                Content,
                Disposition,
                Email,
                FileContent,
                FileName,
                FileType,
                Mail,
                To,
            )

            # 发件人
            from_email_obj = Email(email=self.from_email, name=self.from_name)

            # 收件人
            to_email_obj = To(to_email)

            # 构建邮件
            if template_id:
                # 使用动态模板
                message = Mail(from_email=from_email_obj, to_emails=to_email_obj)
                message.template_id = template_id
                message.dynamic_template_data = template_data or {}
            else:
                # 普通邮件
                if html_content:
                    message = Mail(
                        from_email=from_email_obj,
                        to_emails=to_email_obj,
                        subject=subject,
                        html_content=html_content,
                    )
                else:
                    message = Mail(
                        from_email=from_email_obj,
                        to_emails=to_email_obj,
                        subject=subject,
                        plain_text_content=content,
                    )

            # 处理附件
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as f:
                            file_data = f.read()

                        encoded_file = base64.b64encode(file_data).decode()
                        file_name = os.path.basename(file_path)

                        attachment = Attachment(
                            FileContent(encoded_file),
                            FileName(file_name),
                            FileType(self._get_mime_type(file_path)),
                            Disposition("attachment"),
                        )
                        message.add_attachment(attachment)
                    except Exception as e:
                        logger.warning(f"添加附件失败 {file_path}: {e}")

            # 发送邮件
            response = self._client.send(message)

            if response.status_code in [200, 202]:
                # 发送成功
                message_id = response.headers.get("X-Message-Id", "unknown")

                # 记录发送
                self._send_records.append(
                    {
                        "to_email": to_email,
                        "subject": subject,
                        "message_id": message_id,
                        "send_time": datetime.utcnow().isoformat(),
                        "status": "sent",
                    }
                )

                logger.info(
                    f"SendGrid邮件发送成功 - 收件人:{to_email}, 主题:{subject}, 消息ID:{message_id}"
                )

                return {
                    "status": "success",
                    "message": "邮件发送成功",
                    "data": {
                        "to_email": to_email,
                        "subject": subject,
                        "message_id": message_id,
                        "has_html": html_content is not None,
                        "attachment_count": len(attachments or []),
                    },
                }
            else:
                error_msg = f"邮件发送失败，HTTP状态码: {response.status_code}"
                logger.error(error_msg)
                return {
                    "status": "failed",
                    "message": error_msg,
                    "error_code": f"http_{response.status_code}",
                }

        except Exception as e:
            logger.error(f"SendGrid邮件发送异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "service_error",
            }

    def get_send_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取发送统计

        Args:
            days: 统计天数

        Returns:
            dict: 统计数据
        """
        if not self.use_real_service:
            # 模拟器模式返回模拟统计
            return {
                "status": "success",
                "message": "模拟统计",
                "data": {
                    "total_sent": 100,
                    "total_delivered": 98,
                    "total_bounced": 1,
                    "total_dropped": 1,
                    "period_days": days,
                },
            }

        try:
            # 查询SendGrid统计
            params = {"aggregated_by": "day", "limit": days}
            response = self._client.stats.get(query_params=params)

            if response.status_code == 200:
                stats = response.body
                return {"status": "success", "message": "统计获取成功", "data": stats}
            else:
                return {
                    "status": "failed",
                    "message": "获取统计失败",
                    "error_code": f"http_{response.status_code}",
                }

        except Exception as e:
            logger.error(f"获取SendGrid统计异常: {e}")
            return {"status": "failed", "message": str(e), "error_code": "query_error"}

    def verify_webhook_signature(
        self, signature: str, timestamp: str, payload: str
    ) -> bool:
        """验证Webhook签名（用于处理退信等事件）

        Args:
            signature: 签名
            timestamp: 时间戳
            payload: 请求体

        Returns:
            bool: 签名是否有效
        """
        try:
            import hashlib
            import hmac

            # 构建签名内容
            signed_content = timestamp + payload

            # 计算签名
            computed_signature = hmac.new(
                key=self.api_key.encode(),
                msg=signed_content.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(computed_signature, signature)

        except Exception as e:
            logger.error(f"Webhook签名验证失败: {e}")
            return False

    def handle_bounce(self, bounce_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理退信

        Args:
            bounce_data: 退信数据

        Returns:
            dict: 处理结果
        """
        email = bounce_data.get("email")
        reason = bounce_data.get("reason", "unknown")
        status = bounce_data.get("status", "bounce")

        logger.info(f"处理退信 - 邮箱:{email}, 原因:{reason}, 状态:{status}")

        # 这里可以添加退信处理逻辑，例如：
        # - 将邮箱加入黑名单
        # - 更新用户邮箱状态
        # - 发送告警通知

        return {
            "status": "success",
            "message": "退信已处理",
            "data": {"email": email, "reason": reason, "status": status},
        }

    @staticmethod
    def _get_mime_type(file_path: str) -> str:
        """根据文件路径获取MIME类型

        Args:
            file_path: 文件路径

        Returns:
            str: MIME类型
        """
        import mimetypes

        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"


def create_sendgrid_adapter(config: Optional[Dict[str, Any]] = None) -> SendGridAdapter:
    """创建SendGrid适配器

    Args:
        config: 配置字典，可选

    Returns:
        SendGridAdapter: 适配器实例
    """
    if config is None:
        config = {}

    return SendGridAdapter(
        enabled=config.get("enabled", True),
        success_rate=config.get("success_rate", 100.0),
        delay_ms=config.get("delay_ms", 0),
        max_retries=config.get("max_retries", 3),
        retry_interval_ms=config.get("retry_interval_ms", 1000),
        api_key=config.get("api_key"),
        from_email=config.get("from_email"),
        from_name=config.get("from_name"),
    )
