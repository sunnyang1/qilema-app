#!/usr/bin/env python3
"""
生成强随机 SECRET_KEY 脚本

使用方法:
    python backend/scripts/generate_secret_key.py

输出:
    生成的64字节随机密钥（base64编码）
"""
import os
import sys
import secrets
import base64


def generate_secret_key() -> str:
    """生成64字节的强随机密钥

    Returns:
        str: base64编码的随机密钥
    """
    # 生成64字节（512位）的随机数据
    random_bytes = secrets.token_bytes(64)

    # 使用 base64 编码，便于在配置文件中使用
    secret_key = base64.b64encode(random_bytes).decode('utf-8')

    return secret_key


def main():
    """主函数"""
    # 生成密钥
    secret_key = generate_secret_key()

    # 输出到控制台
    print("=" * 70)
    print("生成的 SECRET_KEY:")
    print("=" * 70)
    print(secret_key)
    print("=" * 70)
    print()
    print("使用方法:")
    print("1. 在 .env 文件中添加:")
    print(f"   SECRET_KEY={secret_key}")
    print()
    print("2. 或者设置环境变量:")
    print(f"   export SECRET_KEY={secret_key}")
    print("=" * 70)


if __name__ == "__main__":
    main()
