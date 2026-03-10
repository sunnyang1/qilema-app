#!/usr/bin/env python3
"""
修复测试文件中的服务调用方式
将 Service.method(db, ...) 改为 Service(db).method(...)
"""

import re
import sys
from pathlib import Path


def fix_service_calls(content: str, service_name: str) -> str:
    """修复服务调用"""
    # 模式1: 单行调用 Service.method(db, ...)
    pattern1 = rf"{service_name}\.(\w+)\(db,\s*"
    content = re.sub(pattern1, rf"{service_name}(db).\1(", content)

    # 模式2: 跨行调用 Service.method(\n    db, ...
    pattern2 = rf"({service_name}\.(\w+)\(\s*)\n\s*db,"
    content = re.sub(pattern2, rf"{service_name}(db).\2(\n", content)

    return content


def process_file(filepath: Path) -> bool:
    """处理单个文件"""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # 修复各种服务调用
        services = [
            "AlertService",
            "DeviceService",
            "EmergencyCenterService",
            "HealthRecordService",
            "UserService",
            "CheckInService",
            "SOSService",
        ]

        for service in services:
            content = fix_service_calls(content, service)

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
    if len(sys.argv) < 2:
        print("用法: python fix_service_calls.py <test_file>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    process_file(filepath)


if __name__ == "__main__":
    main()
