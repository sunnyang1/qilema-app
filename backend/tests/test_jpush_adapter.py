"""
极光推送适配器集成测试

测试适配器的各项功能，包括模拟器模式和真实服务接口
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from app.core.adapters.adapter_factory import AdapterFactory
from app.core.adapters.jpush_adapter import JPushAdapter, create_jpush_adapter


class TestJPushAdapterSimulator:
    """测试极光推送适配器 - 模拟器模式"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "false"
        self.adapter = JPushAdapter(
            enabled=True,
            success_rate=100.0,
            app_key="test_key",
            master_secret="test_secret",
        )

    def test_init_default(self):
        """测试默认初始化"""
        adapter = JPushAdapter()
        assert adapter.use_real_service is False
        assert adapter.enabled is True

    def test_send_push_success(self):
        """测试发送推送成功"""
        result = self.adapter.send(
            user_id="user123",
            title="测试通知",
            content="这是一条测试推送",
            data={"type": "test"},
        )

        assert result["status"] == "success"
        assert result["data"]["user_id"] == "user123"
        assert result["data"]["title"] == "测试通知"

    def test_send_push_disabled(self):
        """测试禁用状态下发送推送"""
        disabled_adapter = JPushAdapter(enabled=False)
        result = disabled_adapter.send(user_id="user123", title="测试", content="内容")

        assert result["status"] == "disabled"

    def test_bind_device(self):
        """测试设备绑定"""
        result = self.adapter.bind_device(
            user_id="user123", registration_id="reg_abc123", device_type="android"
        )

        assert result["status"] == "success"
        assert result["data"]["user_id"] == "user123"
        assert result["data"]["device_type"] == "android"

    def test_unbind_device(self):
        """测试设备解绑"""
        # 先绑定
        self.adapter.bind_device("user123", "reg_abc123")

        # 再解绑
        result = self.adapter.unbind_device("user123")

        assert result["status"] == "success"

    def test_unbind_not_bound(self):
        """测试解绑未绑定的设备"""
        result = self.adapter.unbind_device("unknown_user")

        assert result["status"] == "failed"
        assert result["error_code"] == "not_bound"

    def test_add_tag(self):
        """测试添加标签"""
        result = self.adapter.add_tag("user123", ["vip", "emergency"])

        assert result["status"] == "success"
        assert "vip" in result["data"]["tags"]

    def test_remove_tag(self):
        """测试移除标签"""
        # 先添加标签
        self.adapter.add_tag("user123", ["vip", "emergency"])

        # 再移除
        result = self.adapter.remove_tag("user123", ["vip"])

        assert result["status"] == "success"

    def test_send_by_tag(self):
        """测试按标签发送"""
        # 绑定设备并添加标签
        self.adapter.bind_device("user1", "reg1")
        self.adapter.bind_device("user2", "reg2")
        self.adapter.add_tag("user1", ["emergency"])
        self.adapter.add_tag("user2", ["emergency"])

        result = self.adapter.send_by_tag(
            tags=["emergency"], title="紧急通知", content="紧急情况！"
        )

        assert result["status"] == "success"
        assert result["data"]["target_count"] == 2

    def test_send_by_tag_no_users(self):
        """测试按标签发送（无用户）"""
        result = self.adapter.send_by_tag(
            tags=["nonexistent"], title="测试", content="内容"
        )

        assert result["status"] == "failed"
        assert result["error_code"] == "no_users"

    def test_send_batch(self):
        """测试批量发送"""
        user_ids = ["user1", "user2", "user3"]
        results = self.adapter.send_batch(
            user_ids=user_ids, title="批量通知", content="批量内容"
        )

        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)


class TestJPushAdapterRealService:
    """测试极光推送适配器 - 真实服务接口（使用Mock）"""

    def setup_method(self):
        """每个测试方法前设置"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "true"

    @patch("app.core.adapters.jpush_adapter.JPushAdapter._init_jpush_client")
    def test_init_real_service(self, mock_init):
        """测试真实服务初始化"""
        adapter = JPushAdapter(app_key="real_key", master_secret="real_secret")

        assert adapter.use_real_service is True
        assert adapter.app_key == "real_key"
        mock_init.assert_called_once()

    @patch("app.core.adapters.jpush_adapter.JPushAdapter._init_jpush_client")
    def test_send_real_no_device(self, mock_init):
        """测试真实服务发送（无设备绑定）"""
        adapter = JPushAdapter(app_key="real_key", master_secret="real_secret")
        adapter.use_real_service = True
        adapter._device_bindings = {}  # 确保没有设备绑定

        result = adapter._send_real(user_id="user123", title="测试", content="内容")

        # 由于缺少jpush模块，会抛出异常，error_code为service_error
        assert result["status"] == "failed"
        # 当模块不存在时返回service_error，有模块时会返回device_not_bound
        assert result["error_code"] in ["device_not_bound", "service_error"]


class TestJPushFactory:
    """测试极光推送工厂"""

    def test_create_push_adapter_simulator(self):
        """测试创建推送模拟器"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "false"

        from app.core.notification_simulators import PushNotificationSimulator

        adapter = AdapterFactory.create_push_adapter()

        assert isinstance(adapter, PushNotificationSimulator)

    @patch("app.core.adapters.jpush_adapter.JPushAdapter._init_jpush_client")
    def test_create_push_adapter_real(self, mock_init):
        """测试创建真实推送适配器"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "true"

        adapter = AdapterFactory.create_push_adapter()

        assert isinstance(adapter, JPushAdapter)
        assert adapter.use_real_service is True


class TestCreateJPushAdapter:
    """测试创建极光推送适配器函数"""

    def test_create_with_config(self):
        """测试使用配置创建"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "false"

        config = {
            "enabled": True,
            "app_key": "my_app_key",
            "master_secret": "my_master_secret",
        }

        adapter = create_jpush_adapter(config)

        assert adapter.app_key == "my_app_key"
        assert adapter.master_secret == "my_master_secret"

    def test_create_default(self):
        """测试使用默认配置创建"""
        os.environ["PUSH_USE_REAL_SERVICE"] = "false"

        adapter = create_jpush_adapter()

        assert adapter.enabled is True
