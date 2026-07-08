"""
FastAPI 应用入口
启动: uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Agentic Research Assistant",
    description="自主式研究助手 API — 输入问题，Agent 自动搜索、分析、生成带引用报告",
    version="0.2.0",
)

# CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Agentic Research Assistant",
        "version": "0.2.0",
        "docs": "/docs",
        "api": "/api/v1/research",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
