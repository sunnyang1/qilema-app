"""
阿里云语音服务适配器

提供阿里云语音服务(语音通知/语音验证码)的真实实现
与PhoneNotificationSimulator保持相同接口
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.notification_simulators import PhoneNotificationSimulator

logger = logging.getLogger(__name__)


class AliyunVoiceAdapter(PhoneNotificationSimulator):
    """阿里云语音服务适配器
    
    继承PhoneNotificationSimulator保持接口兼容
    通过环境变量PHONE_USE_REAL_SERVICE控制使用真实服务还是模拟器
    
    支持两种模式：
    1. 语音通知：直接播报文本内容（TTS）
    2. 语音验证码：播放验证码数字
    """
    
    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        tts_voice: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        region_id: str = "cn-hangzhou",
        called_show_number: Optional[str] = None
    ):
        """初始化阿里云语音适配器
        
        Args:
            enabled: 是否启用
            success_rate: 成功率（仅模拟器模式使用）
            delay_ms: 模拟延迟（仅模拟器模式使用）
            max_retries: 最大重试次数
            retry_interval_ms: 重试间隔（毫秒）
            tts_voice: TTS语音类型（如：Siyue、Xiaogang等）
            access_key_id: 阿里云AccessKey ID
            access_key_secret: 阿里云AccessKey Secret
            region_id: 阿里云区域ID
            called_show_number: 被叫显示号码（必须是阿里云购买的号码）
        """
        super().__init__(enabled, success_rate, delay_ms, max_retries, retry_interval_ms, tts_voice)
        
        # 检查是否使用真实服务
        self.use_real_service = os.getenv("PHONE_USE_REAL_SERVICE", "false").lower() == "true"
        
        # 阿里云配置
        self.access_key_id = access_key_id or os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = access_key_secret or os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.region_id = region_id or os.getenv("ALIYUN_VOICE_REGION", "cn-hangzhou")
        self.called_show_number = called_show_number or os.getenv("ALIYUN_VOICE_SHOW_NUMBER")
        
        # TTS语音类型
        self.tts_voice = tts_voice or os.getenv("ALIYUN_VOICE_TTS_VOICE", "Siyue")
        
        # 通话记录（用于状态查询）
        self._call_records: Dict[str, Dict[str, Any]] = {}
        
        if self.use_real_service:
            self._init_aliyun_client()
    
    def _init_aliyun_client(self):
        """初始化阿里云SDK客户端"""
        try:
            # 尝试导入阿里云SDK（语音服务使用dyvmsapi）
            from alibabacloud_dyvmsapi20170525 import models as dyvmsapi_models
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_dyvmsapi20170525.client import Client
            
            if not self.access_key_id or not self.access_key_secret:
                raise ValueError("阿里云语音服务需要配置AccessKey ID和Secret")
            
            if not self.called_show_number:
                raise ValueError("阿里云语音服务需要配置被叫显示号码")
            
            # 配置API访问
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret
            )
            config.endpoint = f"dyvmsapi.aliyuncs.com"
            
            self._client = Client(config)
            self._dyvmsapi_models = dyvmsapi_models
            
            logger.info("阿里云语音客户端初始化成功")
            
        except ImportError:
            logger.warning("阿里云语音SDK未安装，将使用模拟器模式。运行: pip install alibabacloud_dyvmsapi20170525")
            self.use_real_service = False
        except Exception as e:
            logger.error(f"阿里云语音客户端初始化失败: {e}")
            self.use_real_service = False
    
    def _send(
        self,
        phone_number: str,
        content: str,
        call_type: str = "tts",
        template_code: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """发送电话通知
        
        Args:
            phone_number: 被叫手机号
            content: 语音内容（TTS模式）或验证码（verify模式）
            call_type: 呼叫类型（tts-语音通知，verify-语音验证码）
            template_code: 模板代码（可选）
            template_params: 模板参数（可选）
            
        Returns:
            dict: 发送结果
        """
        if not self.use_real_service:
            return super()._send(phone_number, content, **kwargs)
        
        if call_type == "verify":
            return self._send_verify_call(phone_number, content)
        else:
            return self._send_tts_call(phone_number, content, template_code, template_params)
    
    def _send_tts_call(
        self,
        phone_number: str,
        content: str,
        template_code: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送TTS语音通知
        
        Args:
            phone_number: 被叫手机号
            content: TTS文本内容
            template_code: 模板代码（如果使用模板）
            template_params: 模板参数
            
        Returns:
            dict: 发送结果
        """
        try:
            if template_code:
                # 使用模板发送
                single_call_by_tts_request = self._dyvmsapi_models.SingleCallByTtsRequest(
                    called_number=phone_number,
                    called_show_number=self.called_show_number,
                    tts_code=template_code,
                    tts_param=json.dumps(template_params) if template_params else None,
                    voice_code=self.tts_voice
                )
            else:
                # 直接使用TTS内容发送
                single_call_by_tts_request = self._dyvmsapi_models.SingleCallByTtsRequest(
                    called_number=phone_number,
                    called_show_number=self.called_show_number,
                    tts_code=content,  # 直接使用内容作为TTS文本
                    voice_code=self.tts_voice
                )
            
            response = self._client.single_call_by_tts(single_call_by_tts_request)
            
            return self._handle_voice_response(response, phone_number, "tts", content)
            
        except Exception as e:
            logger.error(f"TTS语音发送异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "service_error",
                "data": {"phone_number": phone_number}
            }
    
    def _send_verify_call(self, phone_number: str, code: str) -> Dict[str, Any]:
        """发送语音验证码
        
        Args:
            phone_number: 被叫手机号
            code: 验证码数字
            
        Returns:
            dict: 发送结果
        """
        try:
            single_call_by_voice_request = self._dyvmsapi_models.SingleCallByVoiceRequest(
                called_number=phone_number,
                called_show_number=self.called_show_number,
                voice_code=code
            )
            
            response = self._client.single_call_by_voice(single_call_by_voice_request)
            
            return self._handle_voice_response(response, phone_number, "verify", code)
            
        except Exception as e:
            logger.error(f"语音验证码发送异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "service_error",
                "data": {"phone_number": phone_number}
            }
    
    def _handle_voice_response(
        self, 
        response, 
        phone_number: str, 
        call_type: str,
        content: str
    ) -> Dict[str, Any]:
        """处理语音服务响应
        
        Args:
            response: API响应
            phone_number: 被叫号码
            call_type: 呼叫类型
            content: 内容
            
        Returns:
            dict: 处理后的结果
        """
        response_body = response.body
        
        if response_body.code == "OK":
            call_id = response_body.call_id
            
            # 记录通话
            self._call_records[call_id] = {
                "phone_number": phone_number,
                "call_type": call_type,
                "content": content,
                "call_id": call_id,
                "call_time": datetime.utcnow().isoformat(),
                "status": "calling"
            }
            
            logger.info(f"语音电话发送成功 - 手机:{phone_number}, 类型:{call_type}, 通话ID:{call_id}")
            
            return {
                "status": "success",
                "message": "电话拨打成功",
                "data": {
                    "phone_number": phone_number,
                    "call_type": call_type,
                    "call_id": call_id,
                    "request_id": response_body.request_id
                }
            }
        else:
            error_code = response_body.code
            error_message = response_body.message
            
            logger.error(f"语音电话发送失败 - 手机:{phone_number}, 错误:{error_code} - {error_message}")
            
            return {
                "status": "failed",
                "message": error_message,
                "error_code": self._map_error_code(error_code),
                "data": {
                    "phone_number": phone_number,
                    "aliyun_code": error_code,
                    "request_id": response_body.request_id
                }
            }
    
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """查询通话状态
        
        Args:
            call_id: 通话ID
            
        Returns:
            dict: 通话状态
        """
        if not self.use_real_service:
            # 模拟器模式返回模拟状态
            return {
                "status": "success",
                "message": "模拟状态查询成功",
                "data": {
                    "call_id": call_id,
                    "call_status": "SUCCESS",
                    "duration": 15,
                    "record_url": None
                }
            }
        
        try:
            # 查询真实状态
            query_call_detail_by_call_id_request = self._dyvmsapi_models.QueryCallDetailByCallIdRequest(
                call_id=call_id,
                prod_id="11000000300006",  # 语音通知产品ID
                query_date=datetime.utcnow().strftime("%Y%m%d")
            )
            
            response = self._client.query_call_detail_by_call_id(query_call_detail_by_call_id_request)
            
            if response.body.code == "OK" and response_body.call_detail_list:
                detail = response_body.call_detail_list[0]
                
                return {
                    "status": "success",
                    "message": "状态查询成功",
                    "data": {
                        "call_id": call_id,
                        "phone_number": detail.called_num,
                        "call_status": detail.state_desc,
                        "duration": detail.duration,
                        "start_time": detail.start_time,
                        "end_time": detail.end_time,
                        "record_url": detail.record_url
                    }
                }
            else:
                return {
                    "status": "failed",
                    "message": "未找到通话记录",
                    "error_code": "record_not_found"
                }
                
        except Exception as e:
            logger.error(f"查询通话状态异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "query_error"
            }
    
    def call(self, phone_number: str, content: str, **kwargs) -> Dict[str, Any]:
        """拨打电话（兼容方法）
        
        Args:
            phone_number: 被叫手机号
            content: 语音内容
            
        Returns:
            dict: 拨打结果
        """
        return self.send(phone_number=phone_number, content=content, call_type="tts", **kwargs)
    
    def send_verify_code(self, phone_number: str, code: str) -> Dict[str, Any]:
        """发送语音验证码（便捷方法）
        
        Args:
            phone_number: 被叫手机号
            code: 验证码
            
        Returns:
            dict: 发送结果
        """
        return self.send(
            phone_number=phone_number,
            content=code,
            call_type="verify"
        )
    
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
            "isv.AMOUNT_NOT_ENOUGH": "insufficient_balance",
            "isv.INVALID_NUMBER": "invalid_phone",
            "isv.BLACK_LIST": "blacklisted",
            "isv.NO_CALLED_NUMBER": "no_called_number",
            "isv.CALLED_NUMBER_LIMIT": "called_limit",
            "isv.TEMPLATE_ILLEGAL": "invalid_template"
        }
        return error_map.get(aliyun_code, "unknown_error")


def create_aliyun_voice_adapter(config: Optional[Dict[str, Any]] = None) -> AliyunVoiceAdapter:
    """创建阿里云语音适配器
    
    Args:
        config: 配置字典，可选
        
    Returns:
        AliyunVoiceAdapter: 适配器实例
    """
    if config is None:
        config = {}
    
    return AliyunVoiceAdapter(
        enabled=config.get("enabled", True),
        success_rate=config.get("success_rate", 100.0),
        delay_ms=config.get("delay_ms", 0),
        max_retries=config.get("max_retries", 3),
        retry_interval_ms=config.get("retry_interval_ms", 1000),
        tts_voice=config.get("tts_voice"),
        access_key_id=config.get("access_key_id"),
        access_key_secret=config.get("access_key_secret"),
        region_id=config.get("region_id", "cn-hangzhou"),
        called_show_number=config.get("called_show_number")
    )
