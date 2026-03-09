"""
用户设置Schema验证

提供用户设置相关的数据验证和序列化
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.core.schemas import BaseSchema
from pydantic import BaseModel, Field, validator

# ========== 登录记录相关 ==========


class LoginRecordResponse(BaseModel):
    """登录记录响应"""

    id: int
    user_id: str
    ip_address: Optional[str]
    device_type: Optional[str]
    device_model: Optional[str]
    os_version: Optional[str]
    app_version: Optional[str]
    location: Optional[str]
    latitude: Optional[int]
    longitude: Optional[int]
    login_status: str
    failure_reason: Optional[str]
    created_at: datetime
    logged_out_at: Optional[datetime]

    class Config:
        orm_mode = True


class LoginRecordQuery(BaseModel):
    """查询登录记录"""

    user_id: str = Field(..., description="用户ID")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    login_status: Optional[str] = Field(None, description="登录状态")
    offset: int = Field(default=0, ge=0, description="偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


# ========== 用户反馈相关 ==========


class FeedbackTypeEnum(str, Enum):
    """反馈类型枚举"""

    BUG = "bug"
    SUGGESTION = "suggestion"
    COMPLAINT = "complaint"
    OTHER = "other"


class FeedbackStatusEnum(str, Enum):
    """反馈状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class FeedbackPriorityEnum(str, Enum):
    """反馈优先级枚举"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class UserFeedbackCreate(BaseModel):
    """创建用户反馈"""

    feedback_type: FeedbackTypeEnum = Field(..., description="反馈类型")
    category: Optional[str] = Field(None, description="反馈分类")
    title: str = Field(..., min_length=1, max_length=200, description="反馈标题")
    content: str = Field(..., min_length=1, description="反馈内容")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="附件列表")
    device_type: Optional[str] = Field(None, description="设备类型")
    app_version: Optional[str] = Field(None, description="App版本")


class UserFeedbackUpdate(BaseModel):
    """更新用户反馈"""

    status: Optional[FeedbackStatusEnum] = Field(None, description="处理状态")
    response: Optional[str] = Field(None, description="处理回复")


class UserFeedbackResponse(BaseModel):
    """用户反馈响应"""

    id: int
    user_id: Optional[str]
    feedback_type: FeedbackTypeEnum
    category: Optional[str]
    title: str
    content: str
    attachments: Optional[Dict[str, Any]]
    status: FeedbackStatusEnum
    priority: FeedbackPriorityEnum
    handler_id: Optional[str]
    handler_name: Optional[str]
    response: Optional[str]
    response_at: Optional[datetime]
    device_type: Optional[str]
    app_version: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FeedbackQuery(BaseModel):
    """查询用户反馈"""

    user_id: Optional[str] = Field(None, description="用户ID")
    feedback_type: Optional[FeedbackTypeEnum] = Field(None, description="反馈类型")
    status: Optional[FeedbackStatusEnum] = Field(None, description="处理状态")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    offset: int = Field(default=0, ge=0, description="偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


# ========== 帮助文档相关 ==========


class HelpArticleCreate(BaseModel):
    """创建帮助文档"""

    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: str = Field(..., description="文档内容")
    summary: Optional[str] = Field(None, max_length=500, description="文档摘要")
    category: str = Field(..., description="分类")
    subcategory: Optional[str] = Field(None, description="子分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    sort_order: int = Field(default=0, description="排序序号")
    is_featured: bool = Field(default=False, description="是否推荐")


class HelpArticleUpdate(BaseModel):
    """更新帮助文档"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    summary: Optional[str] = Field(None, max_length=500, description="文档摘要")
    category: Optional[str] = Field(None, description="分类")
    subcategory: Optional[str] = Field(None, description="子分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_featured: Optional[bool] = Field(None, description="是否推荐")
    is_published: Optional[bool] = Field(None, description="是否发布")


class HelpArticleResponse(BaseModel):
    """帮助文档响应"""

    id: int
    title: str
    content: str
    summary: Optional[str]
    category: str
    subcategory: Optional[str]
    tags: Optional[Dict[str, Any]]
    sort_order: int
    is_featured: bool
    is_published: bool
    view_count: int
    helpful_count: int
    not_helpful_count: int
    author_id: Optional[str]
    author_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        orm_mode = True


class HelpArticleQuery(BaseModel):
    """查询帮助文档"""

    category: Optional[str] = Field(None, description="分类")
    is_published: Optional[bool] = Field(None, description="是否发布")
    is_featured: Optional[bool] = Field(None, description="是否推荐")
    offset: int = Field(default=0, ge=0, description="偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


# ========== 常见问题相关 ==========


class FAQCreate(BaseModel):
    """创建常见问题"""

    question: str = Field(..., min_length=1, max_length=500, description="问题")
    answer: str = Field(..., description="答案")
    category: Optional[str] = Field(None, description="分类")
    sort_order: int = Field(default=0, description="排序序号")


class FAQUpdate(BaseModel):
    """更新常见问题"""

    question: Optional[str] = Field(
        None, min_length=1, max_length=500, description="问题"
    )
    answer: Optional[str] = Field(None, description="答案")
    category: Optional[str] = Field(None, description="分类")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_published: Optional[bool] = Field(None, description="是否发布")


class FAQResponse(BaseModel):
    """常见问题响应"""

    id: int
    question: str
    answer: str
    category: Optional[str]
    sort_order: int
    is_published: bool
    view_count: int
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FAQQuery(BaseModel):
    """查询常见问题"""

    category: Optional[str] = Field(None, description="分类")
    is_published: Optional[bool] = Field(None, description="是否发布")
    offset: int = Field(default=0, ge=0, description="偏移量")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")


# ========== 用户设置相关 ==========


class LanguageEnum(str, Enum):
    """语言枚举"""

    ZH_CN = "zh-CN"
    EN_US = "en-US"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"


class ThemeEnum(str, Enum):
    """主题枚举"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class FontSizeEnum(str, Enum):
    """字体大小枚举"""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class UserSettingCreate(BaseModel):
    """创建用户设置"""

    user_id: str = Field(..., description="用户ID")
    language: LanguageEnum = Field(default=LanguageEnum.ZH_CN, description="语言")
    region: str = Field(default="CN", description="地区")
    share_profile: bool = Field(default=True, description="是否分享个人资料")
    share_location: bool = Field(default=True, description="是否分享位置")
    allow_analytics: bool = Field(default=True, description="是否允许数据分析")
    theme: ThemeEnum = Field(default=ThemeEnum.LIGHT, description="主题")
    font_size: FontSizeEnum = Field(default=FontSizeEnum.MEDIUM, description="字体大小")
    extra_settings: Optional[Dict[str, Any]] = Field(None, description="其他设置")


class UserSettingUpdate(BaseModel):
    """更新用户设置"""

    language: Optional[LanguageEnum] = Field(None, description="语言")
    region: Optional[str] = Field(None, description="地区")
    share_profile: Optional[bool] = Field(None, description="是否分享个人资料")
    share_location: Optional[bool] = Field(None, description="是否分享位置")
    allow_analytics: Optional[bool] = Field(None, description="是否允许数据分析")
    theme: Optional[ThemeEnum] = Field(None, description="主题")
    font_size: Optional[FontSizeEnum] = Field(None, description="字体大小")
    extra_settings: Optional[Dict[str, Any]] = Field(None, description="其他设置")


class UserSettingResponse(BaseModel):
    """用户设置响应"""

    id: int
    user_id: str
    language: str
    region: str
    share_profile: bool
    share_location: bool
    allow_analytics: bool
    theme: str
    font_size: str
    extra_settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ========== 账户安全相关 ==========


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

    @validator("new_password")
    def validate_password_complexity(cls, v):
        """验证密码复杂度"""
        # 简单的密码复杂度验证
        if len(v) < 6:
            raise ValueError("密码长度至少6位")
        return v


class UpdatePhoneRequest(BaseModel):
    """更新手机号请求"""

    new_phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="新手机号")
    verification_code: str = Field(..., description="验证码")


class ExportDataRequest(BaseModel):
    """导出数据请求"""

    data_types: List[str] = Field(..., description="数据类型列表")
    format: str = Field(default="json", description="导出格式: json/csv")


class DeleteAccountRequest(BaseModel):
    """删除账户请求"""

    password: str = Field(..., description="密码确认")
    reason: Optional[str] = Field(None, description="删除原因")


class HelpfulRatingRequest(BaseModel):
    """有用评价请求"""

    is_helpful: bool = Field(..., description="是否有用")
