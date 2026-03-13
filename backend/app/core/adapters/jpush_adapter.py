"""
极光推送服务适配器

提供极光推送(JPush)的真实实现，与PushNotificationSimulator保持相同接口
支持设备绑定、标签管理和批量推送
"""

import logging
import os
from typing import Any, Dict, List, Optional

from app.core.notification_simulators import PushNotificationSimulator

logger = logging.getLogger(__name__)


class JPushAdapter(PushNotificationSimulator):
    """极光推送服务适配器

    继承PushNotificationSimulator保持接口兼容
    通过环境变量PUSH_USE_REAL_SERVICE控制使用真实服务还是模拟器
    """

    def __init__(
        self,
        enabled: bool = True,
        success_rate: float = 100.0,
        delay_ms: int = 0,
        max_retries: int = 3,
        retry_interval_ms: int = 1000,
        push_token: Optional[str] = None,
        app_key: Optional[str] = None,
        master_secret: Optional[str] = None,
    ):
        """初始化极光推送适配器

        Args:
            enabled: 是否启用
            success_rate: 成功率（仅模拟器模式使用）
            delay_ms: 模拟延迟（仅模拟器模式使用）
            max_retries: 最大重试次数
            retry_interval_ms: 重试间隔（毫秒）
            push_token: 推送token
            app_key: 极光推送AppKey
            master_secret: 极光推送Master Secret
        """
        super().__init__(
            enabled, success_rate, delay_ms, max_retries, retry_interval_ms, push_token
        )

        # 检查是否使用真实服务
        self.use_real_service = (
            os.getenv("PUSH_USE_REAL_SERVICE", "false").lower() == "true"
        )

        # 极光推送配置
        self.app_key = app_key or os.getenv("JPUSH_APP_KEY")
        self.master_secret = master_secret or os.getenv("JPUSH_MASTER_SECRET")

        # 设备绑定记录
        self._device_bindings: Dict[str, Dict[str, Any]] = {}

        # 标签管理
        self._tags: Dict[str, List[str]] = {}  # tag -> [user_ids]

        if self.use_real_service:
            self._init_jpush_client()

    def _init_jpush_client(self):
        """初始化极光推送SDK客户端"""
        try:
            # 尝试导入极光推送SDK
            import jpush

            if not self.app_key or not self.master_secret:
                raise ValueError("极光推送需要配置AppKey和Master Secret")

            # 创建客户端
            self._client = jpush.JPush(self.app_key, self.master_secret)
            self._push = self._client.create_push()
            self._device = self._client.create_device()

            logger.info("极光推送客户端初始化成功")

        except ImportError:
            logger.warning("极光推送SDK未安装，将使用模拟器模式。运行: pip install jpush")
            self.use_real_service = False
        except Exception as e:
            logger.error(f"极光推送客户端初始化失败: {e}")
            self.use_real_service = False

    def _send(
        self,
        user_id: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """发送推送通知

        Args:
            user_id: 用户ID
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            dict: 发送结果
        """
        if not self.use_real_service:
            return super()._send(user_id, title, content, data, **kwargs)

        return self._send_real(user_id, title, content, data)

    def _send_real(
        self,
        user_id: str,
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """使用极光推送真实服务发送通知

        Args:
            user_id: 用户ID
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            dict: 发送结果
        """
        try:
            import jpush

            # 获取设备绑定信息
            device_info = self._device_bindings.get(user_id, {})
            registration_id = device_info.get("registration_id")

            if not registration_id:
                return {
                    "status": "failed",
                    "message": "用户设备未绑定",
                    "error_code": "device_not_bound",
                }

            # 构建推送对象
            push = self._client.create_push()

            # 设置目标设备
            push.audience = jpush.audience(jpush.registration_id(registration_id))

            # 设置平台
            push.platform = jpush.platform("android", "ios")

            # Android通知
            android_msg = jpush.android(alert=content, title=title, extras=data or {})

            # iOS通知
            ios_msg = jpush.ios(alert=content, extras=data or {})

            # 设置通知
            push.notification = jpush.notification(android=android_msg, ios=ios_msg)

            # 发送推送
            response = push.send()

            if response.status_code == 200:
                result = response.payload
                logger.info(f"极光推送发送成功 - 用户:{user_id}, 消息ID:{result.get('msg_id')}")

                return {
                    "status": "success",
                    "message": "推送发送成功",
                    "data": {
                        "user_id": user_id,
                        "title": title,
                        "content": content,
                        "message_id": result.get("msg_id"),
                        "send_no": result.get("sendno"),
                    },
                }
            else:
                error_msg = f"推送发送失败，HTTP状态码: {response.status_code}"
                logger.error(error_msg)
                return {
                    "status": "failed",
                    "message": error_msg,
                    "error_code": "api_error",
                }

        except Exception as e:
            logger.error(f"极光推送发送异常: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "error_code": "service_error",
            }

    def send_batch(
        self,
        user_ids: List[str],
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """批量发送推送通知

        Args:
            user_ids: 用户ID列表
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            list: 发送结果列表
        """
        if not self.use_real_service:
            return super().send_batch(user_ids, title, content, data)

        # 真实服务：使用批量推送API
        results = []
        try:
            import jpush

            # 获取所有设备的registration_id
            registration_ids = []
            for user_id in user_ids:
                device_info = self._device_bindings.get(user_id, {})
                reg_id = device_info.get("registration_id")
                if reg_id:
                    registration_ids.append(reg_id)

            if not registration_ids:
                return [
                    {
                        "status": "failed",
                        "message": "没有可推送的设备",
                        "error_code": "no_devices",
                    }
                ]

            # 创建批量推送
            push = self._client.create_push()
            push.audience = jpush.audience(jpush.registration_id(*registration_ids))
            push.platform = jpush.platform("android", "ios")

            android_msg = jpush.android(alert=content, title=title, extras=data or {})
            ios_msg = jpush.ios(alert=content, extras=data or {})

            push.notification = jpush.notification(android=android_msg, ios=ios_msg)

            response = push.send()

            if response.status_code == 200:
                result = response.payload
                # 批量推送成功，为每个用户记录成功
                for user_id in user_ids:
                    results.append(
                        {
                            "status": "success",
                            "message": "推送发送成功",
                            "data": {
                                "user_id": user_id,
                                "title": title,
                                "message_id": result.get("msg_id"),
                            },
                        }
                    )
            else:
                # 批量失败
                for user_id in user_ids:
                    results.append(
                        {
                            "status": "failed",
                            "message": f"批量推送失败: {response.status_code}",
                            "error_code": "batch_failed",
                        }
                    )

        except Exception as e:
            logger.error(f"批量推送异常: {e}")
            for user_id in user_ids:
                results.append(
                    {"status": "failed", "message": str(e), "error_code": "exception"}
                )

        return results

    def bind_device(
        self, user_id: str, registration_id: str, device_type: str = "android"
    ) -> Dict[str, Any]:
        """绑定设备

        Args:
            user_id: 用户ID
            registration_id: 设备注册ID
            device_type: 设备类型（android/ios）

        Returns:
            dict: 绑定结果
        """
        try:
            self._device_bindings[user_id] = {
                "registration_id": registration_id,
                "device_type": device_type,
                "bound_at": os.getenv("FAKE_TIME", "2024-01-01T00:00:00"),
                "is_active": True,
            }

            logger.info(f"设备绑定成功 - 用户:{user_id}, 设备:{registration_id}")

            return {
                "status": "success",
                "message": "设备绑定成功",
                "data": {
                    "user_id": user_id,
                    "registration_id": registration_id,
                    "device_type": device_type,
                },
            }
        except Exception as e:
            logger.error(f"设备绑定失败: {e}")
            return {"status": "failed", "message": str(e), "error_code": "bind_failed"}

    def unbind_device(self, user_id: str) -> Dict[str, Any]:
        """解绑设备

        Args:
            user_id: 用户ID

        Returns:
            dict: 解绑结果
        """
        if user_id in self._device_bindings:
            del self._device_bindings[user_id]
            logger.info(f"设备解绑成功 - 用户:{user_id}")
            return {"status": "success", "message": "设备解绑成功"}
        else:
            return {
                "status": "failed",
                "message": "用户未绑定设备",
                "error_code": "not_bound",
            }

    def add_tag(self, user_id: str, tags: List[str]) -> Dict[str, Any]:
        """为用户添加标签

        Args:
            user_id: 用户ID
            tags: 标签列表

        Returns:
            dict: 操作结果
        """
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = []
            if user_id not in self._tags[tag]:
                self._tags[tag].append(user_id)

        logger.info(f"标签添加成功 - 用户:{user_id}, 标签:{tags}")

        return {
            "status": "success",
            "message": "标签添加成功",
            "data": {"user_id": user_id, "tags": tags},
        }

    def remove_tag(self, user_id: str, tags: List[str]) -> Dict[str, Any]:
        """为用户移除标签

        Args:
            user_id: 用户ID
            tags: 标签列表

        Returns:
            dict: 操作结果
        """
        for tag in tags:
            if tag in self._tags and user_id in self._tags[tag]:
                self._tags[tag].remove(user_id)

        return {
            "status": "success",
            "message": "标签移除成功",
            "data": {"user_id": user_id, "tags": tags},
        }

    def send_by_tag(
        self,
        tags: List[str],
        title: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """按标签发送推送

        Args:
            tags: 标签列表
            title: 推送标题
            content: 推送内容
            data: 附加数据

        Returns:
            dict: 发送结果
        """
        # 获取标签下的所有用户
        target_users = set()
        for tag in tags:
            if tag in self._tags:
                target_users.update(self._tags[tag])

        if not target_users:
            return {
                "status": "failed",
                "message": "标签下没有用户",
                "error_code": "no_users",
            }

        # 批量发送
        results = self.send_batch(list(target_users), title, content, data)

        success_count = len([r for r in results if r["status"] == "success"])

        return {
            "status": "success",
            "message": f"标签推送完成，成功:{success_count}/{len(results)}",
            "data": {
                "tags": tags,
                "target_count": len(target_users),
                "success_count": success_count,
            },
        }


def create_jpush_adapter(config: Optional[Dict[str, Any]] = None) -> JPushAdapter:
    """创建极光推送适配器

    Args:
        config: 配置字典，可选

    Returns:
        JPushAdapter: 适配器实例
    """
    if config is None:
        config = {}

    return JPushAdapter(
        enabled=config.get("enabled", True),
        success_rate=config.get("success_rate", 100.0),
        delay_ms=config.get("delay_ms", 0),
        max_retries=config.get("max_retries", 3),
        retry_interval_ms=config.get("retry_interval_ms", 1000),
        app_key=config.get("app_key"),
        master_secret=config.get("master_secret"),
    )
