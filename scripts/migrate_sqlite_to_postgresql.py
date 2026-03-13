"""
SQLite到PostgreSQL数据库迁移脚本

使用方法:
1. 安装依赖: pip install pgloader (或使用Docker)
2. 配置源数据库和目标数据库连接
3. 运行此脚本: python scripts/migrate_sqlite_to_postgresql.py

注意:
- 此脚本使用pgloader工具进行数据迁移
- pgloader需要PostgreSQL的libpq库支持
- 也可以手动导出SQLite数据再导入到PostgreSQL
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 延迟导入settings，在main函数中导入以避免启动时验证


def check_pgloader_installed():
    """检查pgloader是否已安装"""
    try:
        result = subprocess.run(
            ["pgloader", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✓ pgloader已安装: {result.stdout.strip()}")
            return True
        else:
            print("✗ pgloader未安装或无法运行")
            return False
    except FileNotFoundError:
        print("✗ pgloader未找到")
        return False


def migrate_with_pgloader(
    sqlite_db: str, postgres_url: str, verbose: bool = True
) -> bool:
    """使用pgloader从SQLite迁移到PostgreSQL

    Args:
        sqlite_db: SQLite数据库文件路径
        postgres_url: PostgreSQL连接字符串
        verbose: 是否显示详细输出

    Returns:
        bool: 迁移是否成功
    """
    print(f"\n{'='*60}")
    print(f"开始迁移: {sqlite_db} -> {postgres_url}")
    print(f"{'='*60}\n")

    # 构建pgloader命令
    # PostgreSQL URL格式: postgresql://user:password@host:port/database
    # pgloader格式: postgresql://user:password@host:port/database
    pgloader_cmd = ["pgloader", f"sqlite://{sqlite_db}", postgres_url]

    if verbose:
        pgloader_cmd.append("--verbose")

    try:
        print("执行命令:")
        print(" ".join(pgloader_cmd))
        print("\n迁移中...\n")

        result = subprocess.run(pgloader_cmd, capture_output=not verbose, text=True)

        if result.returncode == 0:
            print("\n✓ 迁移成功!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"\n✗ 迁移失败，返回码: {result.returncode}")
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
            return False

    except Exception as e:
        print(f"\n✗ 迁移过程中发生错误: {e}")
        return False


def backup_sqlite_database(sqlite_db: str) -> str:
    """备份SQLite数据库

    Args:
        sqlite_db: SQLite数据库文件路径

    Returns:
        str: 备份文件路径
    """
    import shutil
    from datetime import datetime

    backup_path = f"{sqlite_db}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n创建备份: {backup_path}")
    shutil.copy2(sqlite_db, backup_path)
    print(f"✓ 备份完成")

    return backup_path


def manual_migration_guide(sqlite_db: str, postgres_url: str):
    """输出手动迁移指南

    Args:
        sqlite_db: SQLite数据库文件路径
        postgres_url: PostgreSQL连接字符串
    """
    print(f"\n{'='*60}")
    print("手动迁移指南")
    print(f"{'='*60}\n")

    print("由于pgloader未安装，您可以尝试以下手动迁移方法:\n")

    print("方法1: 使用Docker运行pgloader")
    print("-" * 40)
    print(f"docker run --rm -v {project_root}:/data dimitri/pgloader:latest \\")
    print(f"  /data/{os.path.basename(sqlite_db)} \\")
    print(f"  {postgres_url}\n")

    print("方法2: 使用Python脚本导出/导入")
    print("-" * 40)
    print("1. 从SQLite导出数据为SQL:")
    print(f"   sqlite3 {sqlite_db} .dump > dump.sql")
    print("\n2. 修改dump.sql以适配PostgreSQL:")
    print("   - 将SQLite特定的语法替换为PostgreSQL语法")
    print("   - 修改自增列为SERIAL类型")
    print("   - 移除或调整SQLite特定的PRAGMA语句")
    print("\n3. 导入到PostgreSQL:")
    print(f"   psql {postgres_url} < dump.sql\n")

    print("方法3: 使用Alembic迁移")
    print("-" * 40)
    print("1. 安装Alembic: pip install alembic")
    print("2. 初始化Alembic: alembic init migrations")
    print("3. 配置alembic.ini中的sqlalchemy.url")
    print("4. 创建迁移脚本: alembic revision --autogenerate -m 'initial'")
    print("5. 执行迁移: alembic upgrade head\n")


def main():
    """主函数"""
    import argparse

    # 延迟导入settings，避免启动时验证失败
    from app.core.config import settings

    parser = argparse.ArgumentParser(description="SQLite到PostgreSQL数据库迁移工具")
    parser.add_argument(
        "--sqlite", default="qilema.db", help="SQLite数据库文件路径 (默认: qilema.db)"
    )
    parser.add_argument("--postgres", help="PostgreSQL连接字符串 (默认: 使用环境变量DATABASE_URL)")
    parser.add_argument("--no-backup", action="store_true", help="不创建SQLite数据库备份")
    parser.add_argument("--quiet", action="store_true", help="静默模式，不显示详细输出")

    args = parser.parse_args()

    # 获取PostgreSQL连接字符串
    postgres_url = args.postgres or os.environ.get("DATABASE_URL")

    if not postgres_url:
        print("✗ 未指定PostgreSQL连接字符串")
        print("请使用--postgres参数或设置DATABASE_URL环境变量")
        sys.exit(1)

    if not postgres_url.startswith("postgresql://"):
        print("✗ DATABASE_URL必须是PostgreSQL连接字符串")
        print(f"当前值: {postgres_url}")
        sys.exit(1)

    # 检查SQLite数据库是否存在
    if not os.path.exists(args.sqlite):
        print(f"✗ SQLite数据库文件不存在: {args.sqlite}")
        sys.exit(1)

    # 创建备份
    if not args.no_backup:
        backup_path = backup_sqlite_database(args.sqlite)
    else:
        backup_path = None

    # 检查pgloader是否安装
    if check_pgloader_installed():
        # 使用pgloader迁移
        success = migrate_with_pgloader(
            args.sqlite, postgres_url, verbose=not args.quiet
        )
    else:
        # 输出手动迁移指南
        print("\n⚠ pgloader未安装，无法自动迁移")
        manual_migration_guide(args.sqlite, postgres_url)
        success = False

    if success:
        print(f"\n{'='*60}")
        print("迁移完成!")
        print(f"{'='*60}\n")

        if backup_path:
            print(f"SQLite数据库已备份到: {backup_path}")
            print("如需回滚，请恢复备份文件\n")

        print("下一步:")
        print("1. 验证PostgreSQL中的数据是否正确")
        print("2. 更新.env文件中的DATABASE_URL")
        print("3. 重启应用\n")

        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("迁移失败")
        print(f"{'='*60}\n")

        if backup_path:
            print(f"SQLite数据库备份保存在: {backup_path}\n")

        sys.exit(1)


if __name__ == "__main__":
    main()
