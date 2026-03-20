"""
应用入口模块

启动命令: uv run uvicorn main:app --reload
启动后访问 http://127.0.0.1:8000/docs 查看自动生成的 API 文档
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.backtest import router as backtest_router

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


@app.get("/")
async def root():
    """健康检查接口，用于确认服务是否正常运行"""
    return {"message": "VectorBT Playground is running"}
