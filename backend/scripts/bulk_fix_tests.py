#!/usr/bin/env python3
"""
批量修复测试文件中的服务调用方式
"""

import re
from pathlib import Path


def fix_file(filepath: Path):
    """修复单个文件"""
    content = filepath.read_text(encoding="utf-8")
    original = content

    # 匹配模式: Service.method(db, ...) -> Service(db).method(...)
    # 处理多种服务类型
    services = [
        "CheckInService",
        "DeviceService",
        "EmergencyCenterService",
        "EmergencyContactService",
        "HealthRecordService",
        "SOSService",
        "UserService",
        "NotificationService",
        "RescueService",
        "HealthService",
        "DataService",
    ]

    for svc in services:
        # 单行调用: Service.method(db, ...)
        content = re.sub(rf"\b{svc}\.(\w+)\(db,\s*", rf"{svc}(db).\1(", content)

        # 跨行调用: Service.method(\n    db, ...
        content = re.sub(rf"\b{svc}\.(\w+)\(\s*\n\s*db,", rf"{svc}(db).\1(\n", content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    tests_dir = Path(__file__).parent.parent / "tests"

    fixed = 0
    for test_file in tests_dir.glob("test_*.py"):
        if fix_file(test_file):
            print(f"✅ {test_file.name}")
            fixed += 1

    print(f"\n共修复 {fixed} 个文件")


if __name__ == "__main__":
    main()
