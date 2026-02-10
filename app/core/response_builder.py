"""
API响应构建器模块

提供统一的API响应构建工具函数和类
"""

from typing import Any, List, Optional, Type, Union
from datetime import datetime
from pydantic import BaseModel


class ApiResponseBuilder:
    """
    API响应构建器
    
    提供统一的API响应构建方法，消除路由层手动构建响应字典的重复代码
    
    使用示例:
        >>> from app.core.response_builder import ApiResponseBuilder
        >>> 
        >>> # 成功响应
        >>> return ApiResponseBuilder.success(data={"id": 1})
        >>> 
        >>> # 错误响应
        >>> return ApiResponseBuilder.error(code=400, message="参数错误")
        >>> 
        >>> # 分页响应
        >>> return ApiResponseBuilder.paginated(items=[], total=100, page=1, page_size=10)
        >>> 
        >>> # 从模型转换
        >>> return ApiResponseBuilder.from_model(user, UserResponseSchema)
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        code: int = 200
    ) -> dict:
        """
        构建成功响应
        
        Args:
            data: 响应数据，可以是任意类型
            message: 成功消息
            code: 状态码，默认200
            
        Returns:
            dict: 统一格式的响应字典
            
        示例:
            >>> ApiResponseBuilder.success()
            {'code': 200, 'message': 'success', 'data': None, 'timestamp': 1706534400}
            
            >>> ApiResponseBuilder.success(data={'id': 1}, message='创建成功')
            {'code': 200, 'message': '创建成功', 'data': {'id': 1}, 'timestamp': 1706534400}
        """
        return {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": int(datetime.now().timestamp())
        }

    @staticmethod
    def error(
        code: int,
        message: str,
        detail: Optional[str] = None
    ) -> dict:
        """
        构建错误响应
        
        Args:
            code: 错误状态码
            message: 错误消息
            detail: 详细错误信息（可选）
            
        Returns:
            dict: 统一格式的错误响应字典
            
        示例:
            >>> ApiResponseBuilder.error(code=404, message='用户不存在')
            {'code': 404, 'message': '用户不存在', 'detail': None, 'timestamp': 1706534400}
        """
        return {
            "code": code,
            "message": message,
            "detail": detail,
            "timestamp": int(datetime.now().timestamp())
        }

    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "success"
    ) -> dict:
        """
        构建分页响应
        
        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码（从1开始）
            page_size: 每页大小
            message: 响应消息
            
        Returns:
            dict: 统一格式的分页响应字典
            
        示例:
            >>> ApiResponseBuilder.paginated(
            ...     items=[{'id': 1}, {'id': 2}],
            ...     total=100,
            ...     page=1,
            ...     page_size=10
            ... )
            {
                'code': 200,
                'message': 'success',
                'data': {
                    'items': [{'id': 1}, {'id': 2}],
                    'total': 100,
                    'page': 1,
                    'page_size': 10,
                    'total_pages': 10
                },
                'timestamp': 1706534400
            }
        """
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "code": 200,
            "message": message,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            },
            "timestamp": int(datetime.now().timestamp())
        }

    @staticmethod
    def from_model(
        model: Union[Any, List[Any]],
        schema_class: Type[BaseModel],
        message: str = "success",
        code: int = 200
    ) -> dict:
        """
        从ORM模型构建响应，自动转换为Pydantic Schema
        
        这是消除API路由重复转换代码的核心方法。
        自动处理单条记录和列表两种情况。
        
        Args:
            model: ORM模型实例或模型列表
            schema_class: Pydantic Schema类，用于序列化
            message: 响应消息
            code: 状态码
            
        Returns:
            dict: 统一格式的响应字典
            
        示例:
            >>> # 单条记录
            >>> user = db.query(User).first()
            >>> return ApiResponseBuilder.from_model(user, UserResponseSchema)
            
            >>> # 列表
            >>> users = db.query(User).all()
            >>> return ApiResponseBuilder.from_model(users, UserResponseSchema)
        """
        if model is None:
            return ApiResponseBuilder.success(data=None, message=message, code=code)
        
        def _model_to_dict(obj: Any) -> dict:
            """将模型对象转换为字典，支持to_dict方法或直接属性读取"""
            if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
                return obj.to_dict()
            # 从对象属性构建字典
            return {
                k: v for k, v in obj.__dict__.items() 
                if not k.startswith('_')
            }
        
        # 处理列表
        if isinstance(model, list):
            data = [_model_to_dict(item) for item in model]
            data = [schema_class.model_validate(item).model_dump() for item in data]
        else:
            # 单条记录
            model_dict = _model_to_dict(model)
            schema_instance = schema_class.model_validate(model_dict)
            data = schema_instance.model_dump()
        
        return ApiResponseBuilder.success(data=data, message=message, code=code)

    @staticmethod
    def from_paginated_models(
        models: List[Any],
        schema_class: Type[BaseModel],
        total: int,
        page: int,
        page_size: int,
        message: str = "success"
    ) -> dict:
        """
        从ORM模型列表构建分页响应，自动转换为Pydantic Schema
        
        Args:
            models: ORM模型列表
            schema_class: Pydantic Schema类
            total: 总记录数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
            
        Returns:
            dict: 统一格式的分页响应字典
            
        示例:
            >>> users = db.query(User).offset(0).limit(10).all()
            >>> total = db.query(User).count()
            >>> return ApiResponseBuilder.from_paginated_models(
            ...     users, UserResponseSchema, total, 1, 10
            ... )
        """
        # 转换模型为schema字典
        items = [
            schema_class.model_validate(model).model_dump() 
            for model in models
        ]
        
        return ApiResponseBuilder.paginated(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message=message
        )


# 为了保持向后兼容，提供模块级函数
# 这些函数只是ApiResponseBuilder静态方法的别名

def success_response(data: Any = None, message: str = "success", code: int = 200) -> dict:
    """成功响应（向后兼容）"""
    return ApiResponseBuilder.success(data=data, message=message, code=code)


def error_response(code: int, message: str, detail: Optional[str] = None) -> dict:
    """错误响应（向后兼容）"""
    return ApiResponseBuilder.error(code=code, message=message, detail=detail)


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "success"
) -> dict:
    """分页响应（向后兼容）"""
    return ApiResponseBuilder.paginated(
        items=items, total=total, page=page, page_size=page_size, message=message
    )
