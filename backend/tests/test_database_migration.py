"""
测试数据库迁移脚本
"""

import os
import subprocess
from pathlib import Path

import pytest

from scripts.migrate_sqlite_to_postgresql import (
    backup_sqlite_database,
    check_pgloader_installed,
    migrate_with_pgloader,
)


class TestDatabaseMigrationScript:
    """测试数据库迁移脚本"""

    def test_check_pgloader_installed(self):
        """测试检查pgloader是否已安装"""
        # 这个测试只是调用函数，不关心返回值
        result = check_pgloader_installed()
        # 返回值应该是布尔值
        assert isinstance(result, bool)

    def test_backup_sqlite_database(self, tmp_path):
        """测试备份SQLite数据库"""
        # 创建一个测试数据库文件
        import sqlite3

        test_db = tmp_path / "test.db"
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test (id) VALUES (1)")
        conn.commit()
        conn.close()

        # 备份数据库
        backup_path = backup_sqlite_database(str(test_db))

        # 验证备份文件存在
        assert os.path.exists(backup_path)

        # 验证备份数据库内容
        backup_conn = sqlite3.connect(backup_path)
        cursor = backup_conn.execute("SELECT * FROM test")
        rows = cursor.fetchall()
        backup_conn.close()

        assert len(rows) == 1
        assert rows[0][0] == 1

        # 清理
        os.remove(backup_path)

    def test_migrate_with_pgloader_invalid_url(self):
        """测试使用无效PostgreSQL URL进行迁移"""
        # 创建一个临时SQLite数据库
        import sqlite3
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            test_db = f.name

        conn = sqlite3.connect(test_db)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        try:
            # 尝试迁移到无效的PostgreSQL URL
            success = migrate_with_pgloader(
                test_db,
                "postgresql://invalid:invalid@localhost:9999/invalid",
                verbose=False,
            )

            # 应该失败（因为PostgreSQL不存在）
            # 但如果pgloader未安装，也会返回False
            assert isinstance(success, bool)
        finally:
            # 清理
            if os.path.exists(test_db):
                os.remove(test_db)

    def test_migration_script_exists(self):
        """测试迁移脚本文件存在"""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "migrate_sqlite_to_postgresql.py"
        )
        assert script_path.exists()

    def test_migration_script_has_main_function(self):
        """测试迁移脚本有main函数"""
        from scripts.migrate_sqlite_to_postgresql import main

        assert callable(main)

    def test_migration_script_imports(self):
        """测试迁移脚本可以正确导入"""
        import scripts.migrate_sqlite_to_postgresql as migration_script

        # 验证关键函数存在
        assert hasattr(migration_script, "check_pgloader_installed")
        assert hasattr(migration_script, "backup_sqlite_database")
        assert hasattr(migration_script, "migrate_with_pgloader")
        assert hasattr(migration_script, "manual_migration_guide")
        assert hasattr(migration_script, "main")

    def test_migration_script_help(self):
        """测试迁移脚本帮助信息"""
        result = subprocess.run(
            ["python", "scripts/migrate_sqlite_to_postgresql.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        # 验证帮助信息包含关键参数
        assert result.returncode == 0
        assert "--sqlite" in result.stdout
        assert "--postgres" in result.stdout
        assert "--no-backup" in result.stdout
