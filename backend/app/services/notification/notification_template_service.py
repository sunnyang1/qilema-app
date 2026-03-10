"""
通知模板服务

负责通知模板的管理和渲染
当前暂存内存中，待 NotificationTemplate 模型实现后迁移到数据库
"""

import logging
from typing import Any, Dict, List, Optional

from app.schemas.notification import NotificationTemplateCreate

logger = logging.getLogger(__name__)


class NotificationTemplate:
    """
    通知模板数据类

    临时定义，待 NotificationTemplate 模型实现后移除
    """

    def __init__(
        self,
        id: int,
        template_code: str,
        template_name: str,
        notification_type: str,
        channel: str,
        title_template: str,
        content_template: str,
        data_schema: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        is_active: bool = True,
    ):
        self.id = id
        self.template_code = template_code
        self.template_name = template_name
        self.notification_type = notification_type
        self.channel = channel
        self.title_template = title_template
        self.content_template = content_template
        self.data_schema = data_schema or {}
        self.priority = priority
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "template_code": self.template_code,
            "template_name": self.template_name,
            "notification_type": self.notification_type,
            "channel": self.channel,
            "title_template": self.title_template,
            "content_template": self.content_template,
            "data_schema": self.data_schema,
            "priority": self.priority,
            "is_active": self.is_active,
        }


class NotificationTemplateService:
    """
    通知模板服务

    负责通知模板的管理和渲染：
    - 模板的 CRUD 操作
    - 模板渲染（变量替换）

    当前模板暂存内存中，待 NotificationTemplate 模型实现后迁移到数据库

    使用示例:
        >>> service = NotificationTemplateService()
        >>> template = service.create_template(template_data)
        >>> rendered = service.render_template(template, {"name": "张三"})
    """

    def __init__(self):
        """初始化模板服务"""
        # 内存存储，待迁移到数据库
        self._templates: Dict[str, NotificationTemplate] = {}
        self._next_id = 1

    def create_template(
        self, template_data: NotificationTemplateCreate
    ) -> Dict[str, Any]:
        """
        创建通知模板

        Args:
            template_data: 模板创建数据

        Returns:
            dict: 创建的模板数据
        """
        template = NotificationTemplate(
            id=self._next_id,
            template_code=template_data.template_code,
            template_name=template_data.template_name,
            notification_type=template_data.notification_type,
            channel=template_data.channel,
            title_template=template_data.title_template,
            content_template=template_data.content_template,
            data_schema=template_data.data_schema,
            priority=template_data.priority,
            is_active=True,
        )

        self._templates[template_data.template_code] = template
        self._next_id += 1

        logger.info(f"创建通知模板: {template_data.template_code}")
        return template.to_dict()

    def get_template(self, template_code: str) -> Optional[Dict[str, Any]]:
        """
        获取通知模板

        Args:
            template_code: 模板代码

        Returns:
            dict: 模板数据，如果不存在返回 None
        """
        template = self._templates.get(template_code)
        if template:
            return template.to_dict()
        return None

    def update_template(
        self,
        template_code: str,
        update_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        更新通知模板

        Args:
            template_code: 模板代码
            update_data: 更新数据

        Returns:
            dict: 更新后的模板数据，如果不存在返回 None
        """
        template = self._templates.get(template_code)
        if not template:
            return None

        # 更新字段
        allowed_fields = [
            "template_name",
            "title_template",
            "content_template",
            "data_schema",
            "priority",
            "is_active",
        ]
        for field in allowed_fields:
            if field in update_data:
                setattr(template, field, update_data[field])

        logger.info(f"更新通知模板: {template_code}")
        return template.to_dict()

    def delete_template(self, template_code: str) -> bool:
        """
        删除通知模板

        Args:
            template_code: 模板代码

        Returns:
            bool: 是否成功删除
        """
        if template_code in self._templates:
            del self._templates[template_code]
            logger.info(f"删除通知模板: {template_code}")
            return True
        return False

    def list_templates(
        self,
        notification_type: Optional[str] = None,
        channel: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        列出通知模板

        Args:
            notification_type: 通知类型筛选（可选）
            channel: 通知渠道筛选（可选）
            is_active: 是否激活筛选（可选）

        Returns:
            list: 模板数据列表
        """
        templates = []
        for template in self._templates.values():
            # 应用筛选条件
            if notification_type and template.notification_type != notification_type:
                continue
            if channel and template.channel != channel:
                continue
            if is_active is not None and template.is_active != is_active:
                continue
            templates.append(template.to_dict())
        return templates

    def render_template(
        self,
        template_code: str,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, str]]:
        """
        渲染通知模板

        Args:
            template_code: 模板代码
            data: 模板变量数据

        Returns:
            dict: 包含 title 和 content 的渲染结果，如果模板不存在返回 None
        """
        template = self._templates.get(template_code)
        if not template:
            return None

        title = self._render_text(template.title_template, data)
        content = self._render_text(template.content_template, data)

        return {"title": title, "content": content}

    def _render_text(self, template: str, data: Dict[str, Any]) -> str:
        """
        渲染模板文本

        简单的模板渲染（实际可以使用更强大的模板引擎如 Jinja2）

        Args:
            template: 模板字符串
            data: 模板变量数据

        Returns:
            str: 渲染后的文本
        """
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def validate_template_data(
        self,
        template_code: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        验证模板数据是否符合 schema

        Args:
            template_code: 模板代码
            data: 模板变量数据

        Returns:
            dict: 验证结果 {"valid": bool, "errors": list}
        """
        template = self._templates.get(template_code)
        if not template:
            return {"valid": False, "errors": ["模板不存在"]}

        if not template.data_schema:
            return {"valid": True, "errors": []}

        errors = []
        schema = template.data_schema

        # 检查必需字段
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必需字段: {field}")

        # 检查字段类型（简单实现）
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                field_type = field_schema.get("type")
                if field_type == "string" and not isinstance(value, str):
                    errors.append(f"字段 {field} 应该是字符串类型")
                elif field_type == "integer" and not isinstance(value, int):
                    errors.append(f"字段 {field} 应该是整数类型")
                elif field_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"字段 {field} 应该是数字类型")
                elif field_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"字段 {field} 应该是布尔类型")

        return {"valid": len(errors) == 0, "errors": errors}
