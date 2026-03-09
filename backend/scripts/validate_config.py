#!/usr/bin/env python3
"""
配置验证脚本

在应用启动前验证必需环境变量和连接
"""

import os
import sys

import psycopg2
import redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 必需的环境变量列表
REQUIRED_ENV_VARS = ["SECRET_KEY", "DATABASE_URL", "REDIS_URL", "ENCRYPTION_KEY"]

# 可选的环境变量列表
OPTIONAL_ENV_VARS = ["CORS_ORIGINS", "LOG_LEVEL"]


def validate_required_env_vars() -> bool:
    """
    验证必需的环境变量

    Returns:
        bool: 所有必需环境变量都已设置返回 True
    """
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif var == "SECRET_KEY" and value == "your-secret-key-change-in-production":
            print(f"❌ {var}: 使用了默认值，请设置强随机密钥")
            return False

    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        return False

    print("✅ 所有必需环境变量已设置")
    return True


def validate_secret_key_strength() -> bool:
    """
    验证 SECRET_KEY 强度

    Returns:
        bool: SECRET_KEY 强度足够返回 True
    """
    secret_key = os.getenv("SECRET_KEY", "")
    if len(secret_key) < 32:
        print(f"❌ SECRET_KEY 长度不足: {len(secret_key)} < 32")
        return False

    print(f"✅ SECRET_KEY 强度验证通过 (长度: {len(secret_key)})")
    return True


def validate_encryption_key_exists() -> bool:
    """
    验证 ENCRYPTION_KEY 存在

    Returns:
        bool: ENCRYPTION_KEY 已设置返回 True
    """
    encryption_key = os.getenv("ENCRYPTION_KEY", "")
    if not encryption_key:
        print("❌ ENCRYPTION_KEY 未设置")
        return False

    if len(encryption_key) < 32:
        print(f"❌ ENCRYPTION_KEY 长度不足: {len(encryption_key)} < 32")
        return False

    print(f"✅ ENCRYPTION_KEY 验证通过 (长度: {len(encryption_key)})")
    return True


def validate_database_connection() -> bool:
    """
    验证数据库连接

    Returns:
        bool: 数据库连接成功返回 True
    """
    try:
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            print("❌ DATABASE_URL 未设置")
            return False

        # 解析数据库 URL
        if db_url.startswith("postgresql://"):
            # PostgreSQL 连接
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result and result[0] == 1:
                print("✅ 数据库连接成功")
                return True
            else:
                print("❌ 数据库查询失败")
                return False

    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False


def validate_redis_connection() -> bool:
    """
    验证 Redis 连接

    Returns:
        bool: Redis 连接成功返回 True
    """
    try:
        redis_url = os.getenv("REDIS_URL", "")
        if not redis_url:
            print("❌ REDIS_URL 未设置")
            return False

        # 解析 Redis URL
        if redis_url.startswith("redis://"):
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis 连接成功")
            return True

    except Exception as e:
        print(f"❌ Redis 连接失败: {str(e)}")
        return False


def validate_disk_space() -> bool:
    """
    验证磁盘空间

    Returns:
        bool: 磁盘空间充足返回 True
    """
    try:
        import shutil

        total, used, free = shutil.disk_usage("/")

        # 检查至少有 1GB 可用空间
        free_gb = free / (1024**3)
        if free_gb < 1:
            print(f"❌ 磁盘空间不足: {free_gb:.2f}GB < 1GB")
            return False

        print(f"✅ 磁盘空间充足: {free_gb:.2f}GB 可用")
        return True

    except Exception as e:
        print(f"❌ 磁盘空间检查失败: {str(e)}")
        return False


def main():
    """
    主函数
    """
    print("=" * 50)
    print("开始配置验证...")
    print("=" * 50)

    results = []

    # 验证环境变量
    results.append(("环境变量", validate_required_env_vars()))
    results.append(("SECRET_KEY 强度", validate_secret_key_strength()))
    results.append(("ENCRYPTION_KEY", validate_encryption_key_exists()))

    # 验证连接
    results.append(("数据库连接", validate_database_connection()))
    results.append(("Redis 连接", validate_redis_connection()))

    # 验证资源
    results.append(("磁盘空间", validate_disk_space()))

    # 汇总结果
    print("=" * 50)
    print("配置验证结果汇总:")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 所有配置验证通过！")
        return 0
    else:
        print("❌ 配置验证失败，请修复后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
