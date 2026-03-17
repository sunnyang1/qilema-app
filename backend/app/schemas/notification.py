"""
消息通知Schema验证

提供消息通知相关的数据验证和序列化
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator

# ========== 枚举定义 ==========


class NotificationTypeEnum(str, Enum):
    CHECKIN = "checkin"
    ALERT = "alert"
    SOS = "sos"
    SYSTEM = "system"
    HEALTH = "health"
    DEVICE = "device"
    REMINDER = "reminder"


class NotificationChannelEnum(str, Enum):
    PUSH = "push"
    SMS = "sms"
    PHONE = "phone"
    EMAIL = "email"
    WECHAT = "wechat"


class NotificationPriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


# ========== 通知相关 ==========


class NotificationCreate(BaseModel):
    """创建通知"""

    user_id: str = Field(..., description="用户ID")
    notification_type: NotificationTypeEnum = Field(..., description="通知类型")
    channel: NotificationChannelEnum = Field(..., description="通知渠道")
    priority: NotificationPriorityEnum = Field(
        default=NotificationPriorityEnum.NORMAL, description="优先级"
    )
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")
    recipient_type: Optional[str] = Field(None, description="接收者类型")
    recipient_id: Optional[str] = Field(None, description="接收者ID")
    related_type: Optional[str] = Field(None, description="关联对象类型")
    related_id: Optional[int] = Field(None, description="关联对象ID")


class NotificationUpdate(BaseModel):
    """更新通知"""

    status: Optional[NotificationStatusEnum] = Field(None, description="通知状态")
    read_at: Optional[datetime] = Field(None, description="阅读时间")
    error_message: Optional[str] = Field(None, description="错误信息")


class NotificationResponse(BaseModel):
    """通知响应"""

    id: int
    user_id: str
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    priority: NotificationPriorityEnum
    status: NotificationStatusEnum
    title: str
    content: Optional[str]
    data: Optional[Dict[str, Any]]
    recipient_type: Optional[str]
    recipient_id: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    related_type: Optional[str]
    related_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationQuery(BaseModel):
    """查询通知"""

    user_id: str = Field(..., description="用户ID")
    notification_type: Optional[NotificationTypeEnum] = Field(None, description="通知类型")
    channel: Optional[NotificationChannelEnum] = Field(None, description="通知渠道")
    status: Optional[NotificationStatusEnum] = Field(None, description="通知状态")
    priority: Optional[NotificationPriorityEnum] = Field(None, description="优先级")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    is_unread: Optional[bool] = Field(None, description="是否未读")
    offset: int = Field(default=0, ge=0, description="偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


class NotificationStatistics(BaseModel):
    """通知统计"""

    user_id: str
    stat_date: str
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    unread_count: int
    checkin_count: int
    alert_count: int
    sos_count: int
    system_count: int
    health_count: int
    device_count: int
    reminder_count: int


# ========== 通知模板相关 ==========


class NotificationTemplateCreate(BaseModel):
    """创建通知模板"""

    template_code: str = Field(..., min_length=1, max_length=100, description="模板编码")
    template_name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    notification_type: NotificationTypeEnum = Field(..., description="通知类型")
    channel: NotificationChannelEnum = Field(..., description="通知渠道")
    title_template: str = Field(..., min_length=1, max_length=200, description="标题模板")
    content_template: str = Field(..., description="内容模板")
    data_schema: Optional[Dict[str, Any]] = Field(None, description="数据模板结构")
    priority: NotificationPriorityEnum = Field(
        default=NotificationPriorityEnum.NORMAL, description="默认优先级"
    )


class NotificationTemplateUpdate(BaseModel):
    """更新通知模板"""

    template_name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="模板名称"
    )
    title_template: Optional[str] = Field(
        None, min_length=1, max_length=200, description="标题模板"
    )
    content_template: Optional[str] = Field(None, description="内容模板")
    data_schema: Optional[Dict[str, Any]] = Field(None, description="数据模板结构")
    priority: Optional[NotificationPriorityEnum] = Field(None, description="默认优先级")
    is_active: Optional[bool] = Field(None, description="是否启用")


class NotificationTemplateResponse(BaseModel):
    """通知模板响应"""

    id: int
    template_code: str
    template_name: str
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title_template: str
    content_template: str
    data_schema: Optional[Dict[str, Any]]
    priority: NotificationPriorityEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 通知偏好设置相关 ==========


class NotificationPreferenceCreate(BaseModel):
    """创建通知偏好设置"""

    user_id: str = Field(..., description="用户ID")
    push_enabled: bool = Field(default=True, description="启用APP推送")
    sms_enabled: bool = Field(default=False, description="启用短信通知")
    phone_enabled: bool = Field(default=False, description="启用电话通知")
    email_enabled: bool = Field(default=False, description="启用邮件通知")
    checkin_enabled: bool = Field(default=True, description="签到通知")
    alert_enabled: bool = Field(default=True, description="预警通知")
    sos_enabled: bool = Field(default=True, description="SOS通知")
    system_enabled: bool = Field(default=True, description="系统消息")
    health_enabled: bool = Field(default=True, description="健康报告")
    device_enabled: bool = Field(default=True, description="设备通知")
    reminder_enabled: bool = Field(default=True, description="提醒通知")
    mute_enabled: bool = Field(default=False, description="启用免打扰")
    mute_start_time: Optional[str] = Field(None, description="免打扰开始时间(HH:MM)")
    mute_end_time: Optional[str] = Field(None, description="免打扰结束时间(HH:MM)")

    @validator("mute_start_time", "mute_end_time")
    def validate_time_format(cls, v, values):
        """验证时间格式"""
        if v is not None:
            try:
                datetime.strptime(v, "%H:%M")
            except ValueError:
                raise ValueError("时间格式必须是HH:MM")
        return v


class NotificationPreferenceUpdate(BaseModel):
    """更新通知偏好设置"""

    push_enabled: Optional[bool] = Field(None, description="启用APP推送")
    sms_enabled: Optional[bool] = Field(None, description="启用短信通知")
    phone_enabled: Optional[bool] = Field(None, description="启用电话通知")
    email_enabled: Optional[bool] = Field(None, description="启用邮件通知")
    checkin_enabled: Optional[bool] = Field(None, description="签到通知")
    alert_enabled: Optional[bool] = Field(None, description="预警通知")
    sos_enabled: Optional[bool] = Field(None, description="SOS通知")
    system_enabled: Optional[bool] = Field(None, description="系统消息")
    health_enabled: Optional[bool] = Field(None, description="健康报告")
    device_enabled: Optional[bool] = Field(None, description="设备通知")
    reminder_enabled: Optional[bool] = Field(None, description="提醒通知")
    mute_enabled: Optional[bool] = Field(None, description="启用免打扰")
    mute_start_time: Optional[str] = Field(None, description="免打扰开始时间(HH:MM)")
    mute_end_time: Optional[str] = Field(None, description="免打扰结束时间(HH:MM)")


class NotificationPreferenceResponse(BaseModel):
    """通知偏好设置响应"""

    id: int
    user_id: str
    push_enabled: bool
    sms_enabled: bool
    phone_enabled: bool
    email_enabled: bool
    checkin_enabled: bool
    alert_enabled: bool
    sos_enabled: bool
    system_enabled: bool
    health_enabled: bool
    device_enabled: bool
    reminder_enabled: bool
    mute_enabled: bool
    mute_start_time: Optional[str]
    mute_end_time: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 通知发送请求 ==========


class SendNotificationRequest(BaseModel):
    """发送通知请求"""

    user_id: str = Field(..., description="用户ID")
    notification_type: NotificationTypeEnum = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    channel: Optional[NotificationChannelEnum] = Field(None, description="通知渠道")
    priority: NotificationPriorityEnum = Field(
        default=NotificationPriorityEnum.NORMAL, description="优先级"
    )
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")
    related_type: Optional[str] = Field(None, description="关联对象类型")
    related_id: Optional[int] = Field(None, description="关联对象ID")


class BatchSendNotificationRequest(BaseModel):
    """批量发送通知请求"""

    user_ids: List[str] = Field(..., min_items=1, description="用户ID列表")
    notification_type: NotificationTypeEnum = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")
    channel: Optional[NotificationChannelEnum] = Field(None, description="通知渠道")
    priority: NotificationPriorityEnum = Field(
        default=NotificationPriorityEnum.NORMAL, description="优先级"
    )
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class MarkAsReadRequest(BaseModel):
    """标记已读请求"""

    notification_ids: List[int] = Field(..., min_items=1, description="通知ID列表")


# ========== 通知统计查询 ==========


class NotificationStatsQuery(BaseModel):
    """通知统计查询"""

    user_id: Optional[str] = Field(None, description="用户ID(为空表示全局统计)")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYY-MM-DD)")
    period: Optional[Literal["day", "week", "month"]] = Field(None, description="统计周期")


# 别名定义,用于兼容性
NotificationPriority = NotificationPriorityEnum
