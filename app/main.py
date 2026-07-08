"""
FastAPI 应用入口
启动: uvicorn app.main:app --host 0.0.0.0 --port 8090
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.api.routes import router

# ---- 日志（loguru）----
from loguru import logger
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <cyan>{name}</cyan> | {message}",
)
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {name} | {message}",
    encoding="utf-8",
)

logger.info(f"应用启动: LOG_LEVEL={settings.LOG_LEVEL}, LLM={settings.LLM_PROVIDER}/{settings.LLM_MODEL}")

# ---- 限流 ----
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Agentic Research Assistant",
    description="自主式研究助手 API — 输入问题，Agent 自动搜索、分析、生成带引用报告",
    version="0.3.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
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
        "version": "0.3.0",
        "docs": "/docs",
        "api": "/api/v1/research",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
