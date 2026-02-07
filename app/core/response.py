"""
统一API响应工具

提供标准化的API响应格式
"""

from typing import Any, Dict, Optional, List, Union
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "操作成功",
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        meta: 元数据（如分页信息）
        status_code: HTTP状态码
        
    Returns:
        标准响应字典
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if meta is not None:
        response["meta"] = meta
    
    return response


def error_response(
    message: str = "操作失败",
    error_code: Optional[str] = None,
    details: Optional[Union[Dict, List, str]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详情
        status_code: HTTP状态码
        
    Returns:
        JSONResponse对象
    """
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    
    if error_code is not None:
        response["error_code"] = error_code
    
    if details is not None:
        response["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def list_response(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "获取列表成功"
) -> Dict[str, Any]:
    """
    列表响应
    
    Args:
        items: 列表数据
        total: 总数量
        page: 当前页码
        page_size: 每页数量
        message: 成功消息
        
    Returns:
        标准响应字典
    """
    return success_response(
        data=items,
        message=message,
        meta={
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


def created_response(
    data: Any,
    message: str = "创建成功"
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        data: 创建的数据
        message: 成功消息
        
    Returns:
        标准响应字典
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED
    )


def no_content_response(message: str = "删除成功") -> Dict[str, Any]:
    """
    无内容响应（删除成功等）
    
    Args:
        message: 成功消息
        
    Returns:
        标准响应字典
    """
    return success_response(
        data=None,
        message=message,
        status_code=status.HTTP_204_NO_CONTENT
    )


class APIResponse:
    """
    API响应类
    
    提供类方法创建各种标准响应
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return success_response(data, message, meta)
    
    @staticmethod
    def error(
        message: str = "操作失败",
        error_code: Optional[str] = None,
        details: Optional[Union[Dict, List, str]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> JSONResponse:
        return error_response(message, error_code, details, status_code)
    
    @staticmethod
    def list(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "获取列表成功"
    ) -> Dict[str, Any]:
        return list_response(items, total, page, page_size, message)
    
    @staticmethod
    def created(data: Any, message: str = "创建成功") -> Dict[str, Any]:
        return created_response(data, message)
    
    @staticmethod
    def no_content(message: str = "删除成功") -> Dict[str, Any]:
        return no_content_response(message)
    
    # 常用错误响应
    @staticmethod
    def not_found(message: str = "资源不存在") -> JSONResponse:
        return error_response(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def bad_request(message: str = "请求参数错误", details: Any = None) -> JSONResponse:
        return error_response(
            message=message,
            error_code="BAD_REQUEST",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> JSONResponse:
        return error_response(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message: str = "禁止访问") -> JSONResponse:
        return error_response(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def validation_error(details: Any) -> JSONResponse:
        return error_response(
            message="数据验证失败",
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def server_error(message: str = "服务器内部错误") -> JSONResponse:
        return error_response(
            message=message,
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
