"""
应用入口模块

开发模式: uv run uvicorn main:app --reload
生产模式: cd frontend && npm run build && uv run uvicorn main:app
启动后访问 http://127.0.0.1:8000/docs 查看自动生成的 API 文档
"""

import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.backtest import router as backtest_router

# 启动时预加载 vectorbt，避免首次请求因 import + numba JIT 编译而缓慢
import vectorbt as vbt  # noqa: F401

# 创建 FastAPI 应用实例
app = FastAPI(title="VectorBT Playground")

# 允许前端开发服务器（Vite 默认 5173 端口）跨域访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册回测路由，所有 /backtest/* 的请求都会被转发到 backtest_router
app.include_router(backtest_router)

# 生产环境：挂载前端构建产物（npm run build 输出到 static/）
_STATIC = Path("static")
if _STATIC.is_dir():
    app.mount("/assets", StaticFiles(directory=_STATIC / "assets"), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """生产环境下托管前端 SPA；开发模式下返回健康检查信息"""
    if not _STATIC.is_dir():
        return {"message": "VectorBT Playground is running"}
    # 优先返回具体静态文件（如 favicon.svg、icons.svg）
    candidate = _STATIC / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    # 其余路径均交给前端路由处理
    return FileResponse(_STATIC / "index.html")
