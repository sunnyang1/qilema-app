"""
服务外观协议（typing.Protocol）

用于类型检查与测试替身；**具体服务类无需继承**这些 Protocol，
只要实现相同方法与属性，即满足结构化子类型（PEP 544）。

新服务可在此处或按域拆文件增量添加 Protocol。
"""

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.user import User


@runtime_checkable
class UserServiceProtocol(Protocol):
    """用户服务在路由中最常依赖的能力子集。"""

    db: Session

    def get_by_id(self, user_id: str) -> Optional["User"]:
        ...
