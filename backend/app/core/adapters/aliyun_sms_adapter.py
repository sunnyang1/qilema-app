"""
阿里云短信服务适配器

提供阿里云短信服务的真实实现，与SMSNotificationSimulator保持相同接口
支持通过环境变量切换模拟器/真实服务
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.notification_simulators import SMSNotificationSimulator

logger = logging.getLogger(__name__)


class AliyunSMSAdapter(SMSNotificationSimulator):
    """阿里云短信服务适配器

    继承SMSNotificationSimulator保持接口兼容
    通过环境变量SMS_USE_REAL_SERVICE控制使用真实服务还是模拟器
    """

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        phone_number: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        region_id: str = "cn-hangzhou",
        sign_name: Optional[str] = None,
    ):
        """初始化阿里云短信适配器

        Args:
            enabled: 是否启用
            success_rate: 成功率（仅模拟器模式使用）
            delay_ms: 模拟延迟（仅模拟器模式使用）
            max_retries: 最大重试次数
            retry_interval_ms: 重试间隔（毫秒）
            phone_number: 默认手机号
            access_key_id: 阿里云AccessKey ID
            access_key_secret: 阿里云AccessKey Secret
            region_id: 阿里云区域ID
            sign_name: 短信签名名称
        """
        super().__init__(
            enabled,
            success_rate,
            delay_ms,
            max_retries,
            retry_interval_ms,
            phone_number,
        )

        # 检查是否使用真实服务
        self.use_real_service = (
            os.getenv("SMS_USE_REAL_SERVICE", "false").lower() == "true"
        )

        # 阿里云配置
        self.access_key_id = access_key_id or os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = access_key_secret or os.getenv(
            "ALIYUN_ACCESS_KEY_SECRET"
        )
        self.region_id = region_id or os.getenv("ALIYUN_SMS_REGION", "cn-hangzhou")
        self.sign_name = sign_name or os.getenv("ALIYUN_SMS_SIGN_NAME")

        # 短信发送记录（用于状态查询）
        self._send_records: Dict[str, Dict[str, Any]] = {}

        # 额度监控
        self._quota_info: Dict[str, Any] = {
            "total_quota": 0,
            "used_quota": 0,
            "remaining_quota": 0,
            "last_check": None,
        }

        if self.use_real_service:
            self._init_aliyun_client()

    def _init_aliyun_client(self):
        """初始化阿里云SDK客户端"""
        try:
            # 尝试导入阿里云SDK
            from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
            from alibabacloud_dysmsapi20170525.client import Client
            from alibabacloud_tea_openapi import models as open_api_models

            if not self.access_key_id or not self.access_key_secret:
                raise ValueError("阿里云短信服务需要配置AccessKey ID和Secret")

            if not self.sign_name:
                raise ValueError("阿里云短信服务需要配置签名名称")

            # 配置API访问
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
            )
            config.endpoint = "dysmsapi.aliyuncs.com"

            self._client = Client(config)
            self._dysmsapi_models = dysmsapi_models

            logger.info("阿里云短信客户端初始化成功")

        except ImportError:
            logger.warning(
                "阿里云SDK未安装，将使用模拟器模式。运行: pip install alibabacloud_dysmsapi20170525"
            )
            self.use_real_service = False
        except Exception as e:
            logger.error(f"阿里云短信客户端初始化失败: {e}")
            self.use_real_service = False

    def _send(
        self,
        phone_number: str,
        content: str,
        template_code: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """发送短信

        Args:
            phone_number: 手机号
            content: 短信内容（模拟器模式使用）
            template_code: 模板代码（真实服务必需）
            template_params: 模板参数（真实服务使用）

        Returns:
            dict: 发送结果
        """
        if not self.use_real_service:
            # 使用模拟器
            return super()._send(
                phone_number, content, template_code, template_params, **kwargs
            )

        # 使用真实服务
        return self._send_real(phone_number, template_code, template_params)

    def _send_real(
        self,
        phone_number: str,
        template_code: Optional[str],
        template_params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """使用阿里云真实服务发送短信

        Args:
            phone_number: 手机号
            template_code: 模板代码
            template_params: 模板参数

        Returns:
            dict: 发送结果
        """
        try:
            if not template_code:
                return {
                    "status": "failed",
                    "message": "真实短信服务需要使用模板代码",
                    "error_code": "template_required",
                }

            # 构建发送请求
            send_sms_request = self._dysmsapi_models.SendSmsRequest(
                phone_numbers=phone_number,
                sign_name=self.sign_name,
                template_code=template_code,
                template_param=json.dumps(template_params) if template_params else None,
            )

            # 发送短信
            response = self._client.send_sms(send_sms_request)

            # 解析响应
            response_body = response.body

            if response_body.code == "OK":
                # 发送成功
                message_id = response_body.biz_id

                # 记录发送
                self._send_records[message_id] = {
                    "phone_number": phone_number,
                    "template_code": template_code,
                    "template_params": template_params,
                    "send_time": datetime.utcnow().isoformat(),
                    "status": "sent",
                    "biz_id": message_id,
                }

                logger.info(
                    f"阿里云短信发送成功 - 手机:{phone_number}, 模板:{template_code}, 业务ID:{message_id}"
                )

                return {
                    "status": "success",
                    "message": "短信发送成功",
                    "data": {
                        "phone_number": phone_number,
                        "template_code": template_code,
                        "message_id": message_id,
                        "request_id": response_body.request_id,
                    },
                }
            else:
                # 发送失败
                error_code = response_body.code
                error_message = response_body.message

                logger.error(
                    f"阿里云短信发送失败 - 手机:{phone_number}, 错误:{error_code} - {error_message}"
                )

                return {
                    "status": "failed",
                    "message": error_message,
                    "error_code": self._map_error_code(error_code),
                    "data": {
                        "phone_number": phone_number,
                        "aliyun_code": error_code,
                        "request_id": response_body.request_id,
                    },
                }

        except Exception as e:
            logger.error(f"阿里云短信发送异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "service_error",
                "data": {"phone_number": phone_number},
            }

    def get_send_status(self, message_id: str) -> Dict[str, Any]:
        """查询短信发送状态

        Args:
            message_id: 短信业务ID

        Returns:
            dict: 发送状态
        """
        if not self.use_real_service:
            # 模拟器模式返回模拟状态
            return {
                "status": "success",
                "message": "模拟状态查询成功",
                "data": {
                    "message_id": message_id,
                    "send_status": "SUCCESS",
                    "receive_time": datetime.utcnow().isoformat(),
                },
            }

        try:
            # 查询真实状态
            query_request = self._dysmsapi_models.QuerySendDetailsRequest(
                phone_number=self._send_records.get(message_id, {}).get(
                    "phone_number", ""
                ),
                biz_id=message_id,
                send_date=datetime.utcnow().strftime("%Y-%m-%d"),
                page_size=1,
                current_page=1,
            )

            response = self._client.query_send_details(query_request)

            if response.body.code == "OK" and response.body.sms_send_detail_dtos:
                detail = response.body.sms_send_detail_dtos.sms_send_detail_dto[0]

                return {
                    "status": "success",
                    "message": "状态查询成功",
                    "data": {
                        "message_id": message_id,
                        "phone_number": detail.phone_num,
                        "send_status": detail.send_status,
                        "receive_time": detail.receive_date,
                        "content": detail.content,
                        "err_code": detail.err_code,
                    },
                }
            else:
                return {
                    "status": "failed",
                    "message": "未找到发送记录",
                    "error_code": "record_not_found",
                }

        except Exception as e:
            logger.error(f"查询短信状态异常: {e}")
            return {"status": "failed", "message": str(e), "error_code": "query_error"}

    def check_quota(self) -> Dict[str, Any]:
        """检查短信额度

        Returns:
            dict: 额度信息
        """
        if not self.use_real_service:
            return {
                "status": "success",
                "message": "模拟模式 - 额度无限",
                "data": {
                    "total_quota": 999999,
                    "used_quota": 0,
                    "remaining_quota": 999999,
                    "is_low": False,
                },
            }

        # TODO: 阿里云目前没有直接查询短信额度的API，需要通过控制台或其他方式获取
        # 这里返回缓存的额度信息
        return {
            "status": "success",
            "message": "额度查询成功",
            "data": self._quota_info,
        }

    def is_quota_low(self, threshold: int = 100) -> bool:
        """检查额度是否低于阈值

        Args:
            threshold: 低额度阈值

        Returns:
            bool: 是否低额度
        """
        quota = self.check_quota()
        remaining = quota.get("data", {}).get("remaining_quota", 0)
        return remaining < threshold

    @staticmethod
    def _map_error_code(aliyun_code: str) -> str:
        """映射阿里云错误码为内部错误码

        Args:
            aliyun_code: 阿里云错误码

        Returns:
            str: 内部错误码
        """
        error_map = {
            "isv.BUSINESS_LIMIT_CONTROL": "rate_limit_exceeded",
            "isv.DAY_LIMIT_CONTROL": "rate_limit_exceeded",
            "isv.MONTH_LIMIT_CONTROL": "rate_limit_exceeded",
            "isv.SMS_SIGNATURE_ILLEGAL": "invalid_signature",
            "isv.SMS_TEMPLATE_ILLEGAL": "invalid_template",
            "isv.MOBILE_NUMBER_ILLEGAL": "invalid_phone",
            "isv.AMOUNT_NOT_ENOUGH": "insufficient_balance",
            "isv.SMS_SERVICE_UNAVAILABLE": "service_unavailable",
        }
        return error_map.get(aliyun_code, "unknown_error")


def create_aliyun_sms_adapter(
    config: Optional[Dict[str, Any]] = None
) -> AliyunSMSAdapter:
    """创建阿里云短信适配器

    Args:
        config: 配置字典，可选

    Returns:
        AliyunSMSAdapter: 适配器实例
    """
    if config is None:
        config = {}

    return AliyunSMSAdapter(
        enabled=config.get("enabled", True),
        success_rate=config.get("success_rate", 100.0),
        delay_ms=config.get("delay_ms", 0),
        max_retries=config.get("max_retries", 3),
        retry_interval_ms=config.get("retry_interval_ms", 1000),
        access_key_id=config.get("access_key_id"),
        access_key_secret=config.get("access_key_secret"),
        region_id=config.get("region_id", "cn-hangzhou"),
        sign_name=config.get("sign_name"),
    )
