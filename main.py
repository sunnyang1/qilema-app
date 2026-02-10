"""
起了吗 App - 后端服务入口

此文件为后端服务的包装入口，实际代码位于 backend/ 目录
"""

import sys
import os

# 将 backend 目录添加到路径
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# 从 backend 导入应用
from main import app

# 导出 FastAPI 应用
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"]
    )
