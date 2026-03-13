#!/usr/bin/env python3
"""
重构测试文件 - 适配新的服务实例方法模式

修复内容:
1. fixture: def service() -> def service(mock_db)
2. 方法调用: service.method(mock_db, ...) -> service.method(...)
"""

import re
from pathlib import Path


def fix_service_fixture(content: str) -> str:
    """修复服务 fixture 定义"""
    # 模式: @pytest.fixture\ndef service():\n    return Service()
    pattern = r"(@pytest\.fixture\s+def service)\(([^)]*)\)(:\s+return \w+Service)\(\)"
    replacement = r"\1(mock_db)\3(mock_db)"
    content = re.sub(pattern, replacement, content)
    return content


def remove_mock_db_from_calls(content: str) -> str:
    """移除方法调用中的 mock_db 参数"""
    # 模式: service.method(mock_db, ...) -> service.method(...)
    # 需要处理多种情况

    # 先找到所有服务方法调用
    methods = [
        "get_emergency_contacts",
        "get_emergency_contact",
        "create_emergency_contact",
        "update_emergency_contact",
        "delete_emergency_contact",
        "set_primary_contact",
        "get_primary_contact",
        "create",
        "update",
        "delete",
        "get",
        "list",
    ]

    for method in methods:
        # 匹配 service.method(mock_db, ...)
        pattern = rf"(service\.{method})\(mock_db,\s*"
        content = re.sub(pattern, r"\1(", content)

        # 匹配 service.method(mock_db)
        pattern = rf"(service\.{method})\(mock_db\)"
        content = re.sub(pattern, r"\1()", content)

    return content


def fix_test_signatures(content: str) -> str:
    """修复测试方法签名，移除不需要的 mock_db 参数"""
    # 如果测试方法签名中有 mock_db 但从未使用（除了传给 service），则移除
    # 这是一个复杂操作，暂时保留
    return content


def process_file(filepath: Path) -> tuple[bool, str]:
    """处理单个文件，返回 (是否修改, 新内容)"""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # 应用修复
        content = fix_service_fixture(content)
        content = remove_mock_db_from_calls(content)

        if content != original:
            return True, content
        return False, content
    except Exception as e:
        print(f"❌ 错误 {filepath}: {e}")
        return False, ""


def main():
    """主函数"""
    tests_dir = Path(__file__).parent.parent / "tests"

    files_to_check = [
        "test_emergency_contact_service.py",
        "test_emergency_contact_cache.py",
        "test_emergency_center_service.py",
        "test_health_record_service.py",
        "test_device_service.py",
    ]

    for filename in files_to_check:
        filepath = tests_dir / filename
        if not filepath.exists():
            print(f"⚠️ 跳过: {filename} (不存在)")
            continue

        modified, new_content = process_file(filepath)
        if modified:
            # 不直接写入，而是显示差异
            print(f"\n{'='*60}")
            print(f"📁 {filename}")
            print(f"{'='*60}")

            # 显示关键变化
            original = filepath.read_text(encoding="utf-8")
            original_lines = original.split("\n")
            new_lines = new_content.split("\n")

            for i, (old, new) in enumerate(zip(original_lines, new_lines)):
                if old != new:
                    print(f"  行 {i+1}:")
                    print(f"    - {old}")
                    print(f"    + {new}")

            # 写入文件
            filepath.write_text(new_content, encoding="utf-8")
            print(f"✅ 已修复: {filename}")


if __name__ == "__main__":
    main()
