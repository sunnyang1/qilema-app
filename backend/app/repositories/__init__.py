"""
Repository 层

数据访问层，隔离 Service 与 ORM 细节。
所有数据库操作通过 Repository 进行，Service 不直接使用 Session。
"""

from app.repositories.base_repository import BaseRepository

__all__ = ["BaseRepository"]
