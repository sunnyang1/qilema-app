"""
认证 / 授权策略常量（US-004）

重要：本模块**不参与运行时强制鉴权**。是否允许匿名访问由**各路由的 Depends(...)**
与 OAuth2 逻辑决定；下列列表用于：

- OpenAPI / 文档与代码审查对齐
- ``EnhancedLoggingMiddleware`` 写入 ``request.state.is_public_path``（仅观测，不拦截）
- 单测与将来可能的限流、审计白名单参考

若某路径出现在此列表但路由仍声明了 ``CurrentUserDep``，则以路由为准（仍要求登录）。
"""

from typing import Final, Tuple

# 前缀匹配：path == p 或 path.startswith(p + "/")
PUBLIC_PATH_PREFIXES: Final[Tuple[str, ...]] = (
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/metrics",
    "/api/versions",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/users/register",
)


def is_public_path(path: str) -> bool:
    """是否视为「公开前缀」（与 ``request.state.is_public_path`` 及文档对齐；非强制鉴权结果）。"""
    if not path:
        return False
    for prefix in PUBLIC_PATH_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False
