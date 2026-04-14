"""
API 路由包：主路由器在 `routes` 中集中注册（US-004）。
"""

from app.api.routes import api_router

__all__ = ["api_router"]
