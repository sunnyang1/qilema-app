#!/usr/bin/env python
"""
生成强随机SECRET_KEY脚本

使用方式:
    python scripts/generate_secret_key.py

生成的密钥用于环境变量SECRET_KEY配置
"""
import secrets
import sys


def generate_secret_key(length: int = 64) -> str:
    """生成强随机SECRET_KEY

    Args:
        length: 密钥长度（字节），默认64字节

    Returns:
        str: Base64编码的强随机密钥
    """
    # 使用secrets模块生成密码学安全的随机字节
    random_bytes = secrets.token_bytes(length)

    # 转换为Base64编码的字符串（易于配置）
    import base64

    secret_key = base64.urlsafe_b64encode(random_bytes).decode("utf-8")

    return secret_key


def main():
    """主函数"""
    # 生成64字节的强随机密钥
    secret_key = generate_secret_key(64)

    # 输出密钥
    print(f"生成的SECRET_KEY:")
    print(secret_key)
    print(f"\n密钥长度: {len(secret_key.encode('utf-8'))} 字节")
    print(f"\n请在.env文件中设置:")
    print(f"SECRET_KEY={secret_key}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
