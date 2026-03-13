"""
通知模板服务单元测试
"""

import pytest
from app.schemas.notification import NotificationTemplateCreate
from app.services.notification import NotificationTemplateService


class TestNotificationTemplateService:
    """通知模板服务测试类"""

    def test_create_template(self):
        """测试创建模板"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="test_welcome",
            template_name="欢迎模板",
            notification_type="system",
            channel="push",
            title_template="欢迎 {{username}}",
            content_template="你好 {{username}}，欢迎加入！",
            data_schema={"username": {"type": "string"}},
            priority="normal",
        )

        result = service.create_template(template_data)

        assert result["template_code"] == "test_welcome"
        assert result["template_name"] == "欢迎模板"
        assert result["is_active"] is True

    def test_get_template_existing(self):
        """测试获取存在的模板"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="test_code",
            template_name="测试模板",
            notification_type="system",
            channel="push",
            title_template="标题",
            content_template="内容",
        )
        service.create_template(template_data)

        result = service.get_template("test_code")

        assert result is not None
        assert result["template_code"] == "test_code"

    def test_get_template_non_existing(self):
        """测试获取不存在的模板"""
        service = NotificationTemplateService()

        result = service.get_template("non_existing")

        assert result is None

    def test_update_template(self):
        """测试更新模板"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="test_update",
            template_name="原名称",
            notification_type="system",
            channel="push",
            title_template="原标题",
            content_template="原内容",
        )
        service.create_template(template_data)

        result = service.update_template(
            "test_update", {"template_name": "新名称", "title_template": "新标题"}
        )

        assert result is not None
        assert result["template_name"] == "新名称"
        assert result["title_template"] == "新标题"
        assert result["content_template"] == "原内容"  # 未更新的字段保持不变

    def test_update_template_non_existing(self):
        """测试更新不存在的模板"""
        service = NotificationTemplateService()

        result = service.update_template("non_existing", {"template_name": "新名称"})

        assert result is None

    def test_delete_template(self):
        """测试删除模板"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="test_delete",
            template_name="删除测试",
            notification_type="system",
            channel="push",
            title_template="标题",
            content_template="内容",
        )
        service.create_template(template_data)

        result = service.delete_template("test_delete")

        assert result is True
        assert service.get_template("test_delete") is None

    def test_delete_template_non_existing(self):
        """测试删除不存在的模板"""
        service = NotificationTemplateService()

        result = service.delete_template("non_existing")

        assert result is False

    def test_list_templates_all(self):
        """测试列出所有模板"""
        service = NotificationTemplateService()

        # 创建多个模板
        for i in range(3):
            template_data = NotificationTemplateCreate(
                template_code=f"test_{i}",
                template_name=f"模板{i}",
                notification_type="system",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
            service.create_template(template_data)

        results = service.list_templates()

        assert len(results) >= 3

    def test_list_templates_by_type(self):
        """测试按类型筛选模板"""
        service = NotificationTemplateService()

        # 创建不同类型模板
        service.create_template(
            NotificationTemplateCreate(
                template_code="type_checkin",
                template_name="签到模板",
                notification_type="checkin",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
        )
        service.create_template(
            NotificationTemplateCreate(
                template_code="type_alert",
                template_name="预警模板",
                notification_type="alert",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
        )

        checkin_templates = service.list_templates(notification_type="checkin")

        assert len(checkin_templates) == 1
        assert checkin_templates[0]["template_code"] == "type_checkin"

    def test_list_templates_by_channel(self):
        """测试按渠道筛选模板"""
        service = NotificationTemplateService()

        service.create_template(
            NotificationTemplateCreate(
                template_code="channel_sms",
                template_name="短信模板",
                notification_type="system",
                channel="sms",
                title_template="标题",
                content_template="内容",
            )
        )
        service.create_template(
            NotificationTemplateCreate(
                template_code="channel_push",
                template_name="推送模板",
                notification_type="system",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
        )

        sms_templates = service.list_templates(channel="sms")

        assert len(sms_templates) == 1
        assert sms_templates[0]["template_code"] == "channel_sms"

    def test_list_templates_by_is_active(self):
        """测试按是否激活筛选模板"""
        service = NotificationTemplateService()

        service.create_template(
            NotificationTemplateCreate(
                template_code="active_template",
                template_name="激活模板",
                notification_type="system",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
        )

        # 创建并停用模板
        service.create_template(
            NotificationTemplateCreate(
                template_code="inactive_template",
                template_name="停用模板",
                notification_type="system",
                channel="push",
                title_template="标题",
                content_template="内容",
            )
        )
        service.update_template("inactive_template", {"is_active": False})

        active_templates = service.list_templates(is_active=True)
        inactive_templates = service.list_templates(is_active=False)

        assert any(t["template_code"] == "active_template" for t in active_templates)
        assert any(
            t["template_code"] == "inactive_template" for t in inactive_templates
        )

    def test_render_template(self):
        """测试渲染模板"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="render_test",
            template_name="渲染测试",
            notification_type="system",
            channel="push",
            title_template="欢迎 {{username}}",
            content_template="你好 {{username}}，你的验证码是 {{code}}",
        )
        service.create_template(template_data)

        result = service.render_template(
            "render_test", {"username": "张三", "code": "123456"}
        )

        assert result is not None
        assert result["title"] == "欢迎 张三"
        assert result["content"] == "你好 张三，你的验证码是 123456"

    def test_render_template_non_existing(self):
        """测试渲染不存在的模板"""
        service = NotificationTemplateService()

        result = service.render_template("non_existing", {"username": "test"})

        assert result is None

    def test_render_template_missing_variable(self):
        """测试渲染模板时变量缺失"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="missing_var",
            template_name="变量缺失测试",
            notification_type="system",
            channel="push",
            title_template="欢迎 {{username}}",
            content_template="内容",
        )
        service.create_template(template_data)

        # 不提供变量
        result = service.render_template("missing_var", {})

        # 未替换的占位符应该保留
        assert "{{username}}" in result["title"]

    def test_validate_template_data_valid(self):
        """测试验证有效的模板数据"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="validate_test",
            template_name="验证测试",
            notification_type="system",
            channel="push",
            title_template="标题",
            content_template="内容",
            data_schema={
                "required": ["username"],
                "properties": {
                    "username": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        )
        service.create_template(template_data)

        result = service.validate_template_data(
            "validate_test", {"username": "张三", "age": 25}
        )

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_template_data_missing_required(self):
        """测试验证缺少必需字段"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="required_test",
            template_name="必需字段测试",
            notification_type="system",
            channel="push",
            title_template="标题",
            content_template="内容",
            data_schema={"required": ["username"], "properties": {}},
        )
        service.create_template(template_data)

        result = service.validate_template_data("required_test", {})

        assert result["valid"] is False
        assert any("username" in e for e in result["errors"])

    def test_validate_template_data_invalid_type(self):
        """测试验证类型错误"""
        service = NotificationTemplateService()
        template_data = NotificationTemplateCreate(
            template_code="type_test",
            template_name="类型测试",
            notification_type="system",
            channel="push",
            title_template="标题",
            content_template="内容",
            data_schema={"properties": {"age": {"type": "integer"}}},
        )
        service.create_template(template_data)

        result = service.validate_template_data("type_test", {"age": "not_a_number"})

        assert result["valid"] is False
        assert any("age" in e for e in result["errors"])

    def test_validate_template_data_non_existing(self):
        """测试验证不存在的模板"""
        service = NotificationTemplateService()

        result = service.validate_template_data("non_existing", {"username": "test"})

        assert result["valid"] is False
        assert any("不存在" in e for e in result["errors"])

    def test_render_text(self):
        """测试 _render_text 方法"""
        service = NotificationTemplateService()

        result = service._render_text(
            "Hello {{name}}, your code is {{code}}", {"name": "World", "code": "123"}
        )

        assert result == "Hello World, your code is 123"
