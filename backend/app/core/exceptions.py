"""
统一异常处理模块

定义应用中的所有业务异常类，提供统一的错误处理机制
"""

from typing import Any, Optional

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """应用基础异常类

    所有自定义异常的基类，提供统一的异常处理接口

    Attributes:
        code: 错误码
        message: 错误消息
        detail: 详细错误信息
    """

    def __init__(
        self,
        code: int = 500,
        message: str = "Internal server error",
        detail: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        """初始化基础异常

        Args:
            code: 自定义错误码（如1001, 1002等）
            message: 错误消息
            detail: 详细错误信息
            status_code: HTTP状态码
        """
        self.code = code
        self.message = message
        super().__init__(status_code=status_code, detail=detail or message)


# ========== 400 客户端错误 ==========


class ValidationException(BaseAppException):
    """验证异常

    当请求参数验证失败时抛出
    """

    def __init__(self, message: str = "请求参数验证失败", detail: Optional[str] = None):
        super().__init__(
            code=400,
            message=message,
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MissingFieldException(ValidationException):
    """缺失字段异常

    当必填字段缺失时抛出
    """

    def __init__(self, field_name: str):
        message = f"必填字段缺失: {field_name}"
        super().__init__(message=message)


class InvalidValueException(ValidationException):
    """无效值异常

    当字段值无效时抛出
    """

    def __init__(self, field_name: str, value: Any = None):
        message = f"字段值无效: {field_name}"
        if value is not None:
            message += f" (值: {value})"
        super().__init__(message=message)


class InvalidFormatException(ValidationException):
    """格式异常

    当数据格式不正确时抛出
    """

    def __init__(self, field_name: str, expected_format: str):
        message = f"字段格式错误: {field_name}，期望格式: {expected_format}"
        super().__init__(message=message)


# ========== 401 认证错误 ==========


class UnauthorizedException(BaseAppException):
    """未授权异常

    当用户未认证时抛出
    """

    def __init__(self, message: str = "未授权访问", detail: Optional[str] = None):
        super().__init__(
            code=401,
            message=message,
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidCredentialsException(UnauthorizedException):
    """无效凭证异常

    当用户名或密码错误时抛出
    """

    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__(message=message)


class TokenExpiredException(UnauthorizedException):
    """Token过期异常

    当JWT Token过期时抛出
    """

    def __init__(self, message: str = "Token已过期，请重新登录"):
        super().__init__(message=message)


class InvalidTokenException(UnauthorizedException):
    """无效Token异常

    当JWT Token无效时抛出
    """

    def __init__(self, message: str = "无效的Token"):
        super().__init__(message=message)


# ========== 403 禁止访问 ==========


class ForbiddenException(BaseAppException):
    """禁止访问异常

    当用户权限不足时抛出
    """

    def __init__(self, message: str = "权限不足，无法访问", detail: Optional[str] = None):
        super().__init__(
            code=403,
            message=message,
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


# ========== 404 资源未找到 ==========


class NotFoundException(BaseAppException):
    """资源未找到异常

    当请求的资源不存在时抛出
    """

    def __init__(self, resource_name: str = "资源", detail: Optional[str] = None):
        message = f"{resource_name}不存在"
        BaseAppException.__init__(
            self,
            code=404,
            message=message,
            detail=detail or message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserNotFoundException(BaseAppException):
    """用户未找到异常

    当用户不存在时抛出
    """

    def __init__(self, user_id: str = None):
        if user_id:
            message = f"用户不存在: {user_id}"
        else:
            message = "用户不存在"
        BaseAppException.__init__(
            self, code=404, message=message, status_code=status.HTTP_404_NOT_FOUND
        )


class DeviceNotFoundException(BaseAppException):
    """设备未找到异常

    当设备不存在时抛出
    """

    def __init__(self, device_id: str = None):
        if device_id:
            message = f"设备不存在: {device_id}"
        else:
            message = "设备不存在"
        BaseAppException.__init__(
            self, code=404, message=message, status_code=status.HTTP_404_NOT_FOUND
        )


class ThresholdNotFoundException(BaseAppException):
    """阈值配置未找到异常

    当阈值配置不存在时抛出
    """

    def __init__(self):
        BaseAppException.__init__(
            self,
            code=404,
            message="阈值配置不存在",
            status_code=status.HTTP_404_NOT_FOUND,
        )


# ========== 429 请求过多 ==========


class TooManyRequestsException(BaseAppException):
    """请求过多异常

    当请求频率超过限制时抛出
    """

    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(
            code=429, message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


# ========== 500 服务器错误 ==========


class InternalServerException(BaseAppException):
    """服务器内部错误异常

    当服务器发生未知错误时抛出
    """

    def __init__(self, message: str = "服务器内部错误", detail: Optional[str] = None):
        super().__init__(
            code=500,
            message=message,
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DatabaseException(InternalServerException):
    """数据库异常

    当数据库操作失败时抛出
    """

    def __init__(self, message: str = "数据库操作失败", detail: Optional[str] = None):
        super().__init__(message=message, detail=detail)


class CacheException(InternalServerException):
    """缓存异常

    当缓存操作失败时抛出
    """

    def __init__(self, message: str = "缓存操作失败", detail: Optional[str] = None):
        super().__init__(message=message, detail=detail)


class ExternalServiceException(InternalServerException):
    """外部服务异常

    当调用外部服务失败时抛出
    """

    def __init__(self, service_name: str, detail: Optional[str] = None):
        message = f"外部服务调用失败: {service_name}"
        super().__init__(message=message, detail=detail)


# ========== 自定义业务错误码 ==========


# 1001-1099: 用户相关错误
class UserAlreadyExistsException(BaseAppException):
    """用户已存在异常（错误码1001）"""

    def __init__(self, phone: str = None):
        message = "该手机号已注册"
        if phone:
            message = f"该手机号已注册: {phone}"
        BaseAppException.__init__(
            self, code=1001, message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


# 1002-1099: 签到相关错误
class AlreadyCheckedInException(BaseAppException):
    """已签到异常（错误码1003）"""

    def __init__(self, message: str = "今天已经签到过了"):
        BaseAppException.__init__(
            self, code=1003, message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


# 1100-1199: 设备相关错误
class DeviceAlreadyBoundException(BaseAppException):
    """设备已绑定异常（错误码1101）"""

    def __init__(self, device_id: str = None):
        message = "该设备已被绑定"
        if device_id:
            message = f"该设备已被绑定: {device_id}"
        BaseAppException.__init__(
            self, code=1101, message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


# 1200-1299: 紧急联系人相关错误
class EmergencyContactNotFoundException(BaseAppException):
    """紧急联系人未找到异常（错误码1201）"""

    def __init__(self):
        BaseAppException.__init__(
            self,
            code=1201,
            message="紧急联系人不存在",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class MinimumContactRequiredException(BaseAppException):
    """最少联系人异常（错误码1202）"""

    def __init__(self, min_count: int = 1):
        message = f"至少需要{min_count}个紧急联系人"
        BaseAppException.__init__(
            self, code=1202, message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


# 1300-1399: SOS相关错误
class SOSAlreadyTriggeredException(BaseAppException):
    """SOS已触发异常（错误码1301）"""

    def __init__(self):
        BaseAppException.__init__(
            self,
            code=1301,
            message="SOS已触发，请勿重复操作",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# 1400-1499: 预警相关错误
class AlertCooldownException(BaseAppException):
    """预警冷却异常（错误码1401）"""

    def __init__(self):
        BaseAppException.__init__(
            self,
            code=1401,
            message="预警冷却中，请稍后再试",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# ========== 异常工具函数 ==========


def handle_database_error(error: Exception) -> DatabaseException:
    """处理数据库错误

    Args:
        error: 原始数据库错误

    Returns:
        DatabaseException: 格式化后的数据库异常
    """
    error_message = str(error)
    # 根据错误类型提供更友好的消息
    if "duplicate" in error_message.lower() or "unique" in error_message.lower():
        return DatabaseException(message="数据已存在", detail=error_message)
    elif "foreign key" in error_message.lower():
        return DatabaseException(message="关联数据不存在", detail=error_message)
    elif "constraint" in error_message.lower():
        return DatabaseException(message="数据约束冲突", detail=error_message)
    else:
        return DatabaseException(message="数据库操作失败", detail=error_message)
