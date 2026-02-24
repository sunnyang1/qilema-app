#!/usr/bin/env python3
"""启动脚本，手动加载环境变量"""
from dotenv import load_dotenv
import os
import sys

# 加载 .env 文件
load_dotenv()

# 启动服务
import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
