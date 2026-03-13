#!/usr/bin/env python3
"""
修复测试文件中的服务实例化方式
将 Service() 改为 Service(mock_db)
"""

import os
import re
from pathlib import Path


def fix_service_fixture(content: str) -> str:
    """修复服务 fixture"""
    # 模式1: @pytest.fixture + def service(): return Service()
    pattern1 = r"(@pytest\.fixture\s+def service\([^)]*\):\s+return \w+Service)\(\)"
    content = re.sub(pattern1, r"\1(mock_db)", content)

    # 模式2: 类方法 def service(self): return Service()
    pattern2 = r"(def service\(self\):\s+return \w+Service)\(\)"
    content = re.sub(pattern2, r"\1(mock_db)", content)

    return content


def add_mock_db_import(content: str) -> str:
    """添加 mock_db fixture 如果缺失"""
    if "mock_db" in content and "def mock_db" not in content:
        # 检查是否已有 mock_db fixture
        fixture_code = '''

@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    from unittest.mock import Mock
    from sqlalchemy.orm import Session
    return Mock(spec=Session)
'''
        # 在第一个 @pytest.fixture 之前添加
        content = re.sub(
            r"(@pytest\.fixture\s+def )", fixture_code + r"\1", content, count=1
        )
    return content


def fix_test_method_calls(content: str) -> str:
    """修复测试方法中的服务调用"""
    # 将 service.method(...) 改为 service.method(mock_db, ...)
    # 但这需要更复杂的分析，暂时跳过
    return content


def process_file(filepath: Path) -> bool:
    """处理单个文件"""
    try:
        content = filepath.read_text(encoding="utf-8")

        # 检查是否包含需要修复的模式
        if "Service()" not in content:
            return False

        original = content

        # 应用修复
        content = fix_service_fixture(content)
        content = add_mock_db_import(content)

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            print(f"✅ 修复: {filepath}")
            return True

        return False
    except Exception as e:
        print(f"❌ 错误 {filepath}: {e}")
        return False


def main():
    """主函数"""
    tests_dir = Path(__file__).parent.parent / "tests"

    fixed_count = 0

    for test_file in tests_dir.glob("test_*.py"):
        if process_file(test_file):
            fixed_count += 1

    print(f"\n共修复 {fixed_count} 个文件")


if __name__ == "__main__":
    main()
