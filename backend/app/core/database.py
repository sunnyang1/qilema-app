"""
数据库连接和会话管理
"""

from typing import Optional

from app.core.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool


def get_engine(
    database_url: Optional[str] = None,
    echo: Optional[bool] = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_recycle: int = 3600,
):
    """获取数据库引擎

    Args:
        database_url: 数据库连接字符串，如果为None则使用settings.DATABASE_URL
        echo: 是否输出SQL语句，如果为None则使用settings.DEBUG
        pool_size: 连接池大小（仅PostgreSQL）
        max_overflow: 连接池溢出大小（仅PostgreSQL）
        pool_recycle: 连接回收时间（秒）

    Returns:
        sqlalchemy.engine.Engine: 数据库引擎
    """
    url = database_url or settings.DATABASE_URL
    debug = echo if echo is not None else settings.DEBUG

    # 根据数据库类型设置连接参数和连接池
    if "sqlite" in url:
        # SQLite使用NullPool（不使用连接池，因为SQLite不支持并发）
        connect_args = {"check_same_thread": False}
        poolclass = NullPool
    elif "postgresql" in url:
        # PostgreSQL使用QueuePool（连接池）
        connect_args = {}
        poolclass = QueuePool
    else:
        # 其他数据库使用默认配置
        connect_args = {}
        poolclass = None

    # 构建引擎参数
    engine_kwargs = {
        "connect_args": connect_args,
        "echo": debug,
    }

    # 添加连接池配置（仅适用于支持连接池的数据库）
    if poolclass:
        engine_kwargs["poolclass"] = poolclass
        if poolclass == QueuePool:
            engine_kwargs["pool_size"] = pool_size
            engine_kwargs["max_overflow"] = max_overflow
            engine_kwargs["pool_recycle"] = pool_recycle

    return create_engine(url, **engine_kwargs)


# 创建数据库引擎
engine = get_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话(依赖注入使用)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """获取数据库会话(直接使用)"""
    return SessionLocal()


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


def check_database_health(engine_url: Optional[str] = None) -> bool:
    """检查数据库健康状态

    Args:
        engine_url: 数据库连接字符串，如果为None则使用settings.DATABASE_URL

    Returns:
        bool: 数据库是否健康
    """
    try:
        engine = get_engine(engine_url)
        with engine.connect() as conn:
            # 执行简单查询测试连接
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            return row is not None and row[0] == 1
    except Exception as e:
        print(f"数据库健康检查失败: {e}")
        return False
    finally:
        if "engine" in locals():
            engine.dispose()
