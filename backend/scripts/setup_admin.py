#!/usr/bin/env python
"""
管理员设置脚本

用于将指定用户设置为管理员

用法:
    python scripts/setup_admin.py <user_id>
    python scripts/setup_admin.py --list  # 列出所有用户
"""

import argparse
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User


def list_users():
    """列出所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n用户列表:")
        print("-" * 80)
        print(f"{'User ID':<36} {'Phone':<15} {'Nickname':<20} {'Is Admin'}")
        print("-" * 80)

        admin_ids = settings.ADMIN_USER_IDS
        for user in users:
            is_admin = "✓" if user.user_id in admin_ids else ""
            nickname = user.nickname or ""
            print(f"{user.user_id:<36} {user.phone:<15} {nickname:<20} {is_admin}")
        print("-" * 80)
        print(f"\n总计: {len(users)} 个用户")
        print(f"当前管理员: {len(admin_ids)} 个")

    finally:
        db.close()


def set_admin(user_id: str):
    """将指定用户设置为管理员"""
    db = SessionLocal()
    try:
        # 检查用户是否存在
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            print(f"❌ 错误: 用户 {user_id} 不存在")
            return False

        # 检查是否已经是管理员
        admin_ids = settings.ADMIN_USER_IDS
        if user_id in admin_ids:
            print(f"✅ 用户 {user_id} ({user.phone}) 已经是管理员")
            return True

        # 添加到管理员列表
        new_admin_ids = admin_ids + [user_id]
        admin_ids_str = ",".join(new_admin_ids)

        print(f"\n用户: {user_id}")
        print(f"手机: {user.phone}")
        print(f"昵称: {user.nickname or 'N/A'}")
        print(f"\n请将以下配置添加到 .env 文件:")
        print(f"\nADMIN_USER_IDS={admin_ids_str}\n")

        # 可选：自动更新 .env 文件
        env_path = os.path.join(project_root, ".env")
        if os.path.exists(env_path):
            response = input("是否自动更新 .env 文件? (y/n): ")
            if response.lower() == "y":
                update_env_file(env_path, admin_ids_str)
                print("✅ .env 文件已更新")
                print("⚠️  请重启应用以生效")

        return True

    finally:
        db.close()


def update_env_file(env_path: str, admin_ids_str: str):
    """更新 .env 文件"""
    with open(env_path, "r") as f:
        lines = f.readlines()

    # 查找并替换 ADMIN_USER_IDS
    found = False
    new_lines = []
    for line in lines:
        if line.startswith("ADMIN_USER_IDS="):
            new_lines.append(f"ADMIN_USER_IDS={admin_ids_str}\n")
            found = True
        else:
            new_lines.append(line)

    # 如果没有找到，添加到文件末尾
    if not found:
        new_lines.append(f"\n# 管理员配置\nADMIN_USER_IDS={admin_ids_str}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)


def main():
    parser = argparse.ArgumentParser(
        description="管理员设置脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python scripts/setup_admin.py --list
    python scripts/setup_admin.py user_abc123xyz
        """,
    )
    parser.add_argument(
        "user_id",
        nargs="?",
        help="要设置为管理员的用户ID",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="列出所有用户",
    )

    args = parser.parse_args()

    if args.list:
        list_users()
    elif args.user_id:
        success = set_admin(args.user_id)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
