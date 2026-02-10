"""
测试配置 - pytest配置文件
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Pytest配置
def pytest_configure(config):
    """Pytest配置钩子"""
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试"
    )
    config.addinivalue_line(
        "markers", "stress: 压力测试"
    )
    config.addinivalue_line(
        "markers", "full: 全量测试"
    )


# 数据库配置
@pytest.fixture(scope="session")
def test_database_url():
    """测试数据库URL"""
    return "sqlite:///test.db"


@pytest.fixture
def db():
    """创建测试数据库会话"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # 使用内存数据库进行测试
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理数据库
        Base.metadata.drop_all(bind=engine)


# 测试配置
TEST_CONFIG = {
    # 超时配置(秒)
    "timeout": {
        "unit_test": 5,
        "integration_test": 10,
        "api_test": 3,
        "stress_test": 600,
    },

    # 并发配置
    "concurrency": {
        "max_workers": 20,
        "batch_size": 100,
    },

    # 数据量配置
    "data_volume": {
        "small": 10,
        "medium": 100,
        "large": 1000,
        "extra_large": 10000,
    },

    # 性能阈值
    "performance_threshold": {
        "api_response_time": 1.0,  # 秒
        "query_time": 1.0,  # 秒
        "batch_operation_time": 30.0,  # 秒
        "concurrent_operation_time": 10.0,  # 秒
    },

    # 成功率阈值
    "success_rate": {
        "critical": 1.0,  # 100%
        "high": 0.95,  # 95%
        "medium": 0.90,  # 90%
        "low": 0.80,  # 80%
    },

    # 内存配置(MB)
    "memory_limit": {
        "max_increase": 100,  # 最大内存增长
        "max_total": 500,  # 最大总内存
    },
}
