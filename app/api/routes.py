"""FastAPI 路由（Phase 4 + 6: 标准 API + 限流 + 日志）"""
import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi.util import get_remote_address

from app.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    ReportResponse,
    SessionSummary,
)
from app.agent.graph import build_research_graph
from app.agent.state import ResearchState
from app.memory.session import SessionManager
from app.config import settings

from loguru import logger

router = APIRouter(prefix="/api/v1")
session_manager = SessionManager()

# 内存缓存：正在运行/已完成的研究任务
_research_cache: dict[str, dict] = {}


@router.post("/research", response_model=ResearchResponse)
async def start_research(request: Request, research_request: ResearchRequest):
    """发起一项研究任务（同步执行，支持超时）"""
    max_iterations = research_request.max_iterations or (5 if research_request.deep else 3)
    session_id = uuid4().hex[:8]

    logger.info(f"研究开始 [会话={session_id}] 问题='{research_request.question[:80]}' 轮次={max_iterations}")

    session_manager.create_session(research_request.question)
    session_manager.update_session(session_id, {"status": "running"})

    try:
        graph = build_research_graph()
        initial_state = ResearchState(
            research_question=research_request.question,
            max_iterations=max_iterations,
        )
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state),
            timeout=300.0,
        )

        report = result.final_report or ""
        sources = [
            {"title": r.get("title", ""), "url": r.get("url", "")}
            for r in (result.search_results or [])
        ]
        _research_cache[session_id] = {
            "question": research_request.question,
            "report": report,
            "iterations": result.iteration,
            "sources_count": len(result.search_results or []),
            "sources": sources,
            "status": "completed",
        }

        session_manager.update_session(session_id, {
            "question": research_request.question,
            "iterations": result.iteration,
            "sources_count": len(result.search_results or []),
            "report": report,
            "status": "completed",
        })

        logger.info(f"研究完成 [会话={session_id}] {result.iteration}轮 {len(result.search_results or [])}个来源")

        return ResearchResponse(
            session_id=session_id,
            question=research_request.question,
            status="completed",
        )

    except asyncio.TimeoutError:
        logger.warning(f"研究超时 [会话={session_id}]")
        _research_cache[session_id] = {"question": research_request.question, "status": "error", "error": "研究超时（>5分钟）"}
        session_manager.update_session(session_id, {"status": "error"})
        raise HTTPException(status_code=504, detail="研究超时")

    except Exception as e:
        logger.exception(f"研究出错 [会话={session_id}]: {e}")
        _research_cache[session_id] = {"question": research_request.question, "status": "error", "error": str(e)}
        session_manager.update_session(session_id, {"status": "error"})
        raise HTTPException(status_code=500, detail=f"研究执行失败: {str(e)}")


@router.get("/report/{session_id}", response_model=ReportResponse)
async def get_report(request: Request, session_id: str):
    """获取研究报告"""
    cached = _research_cache.get(session_id)
    if cached:
        return ReportResponse(
            session_id=session_id,
            question=cached.get("question", ""),
            report=cached.get("report"),
            iterations=cached.get("iterations", 0),
            sources_count=cached.get("sources_count", 0),
            sources=cached.get("sources", []),
            status=cached.get("status", "completed"),
            error=cached.get("error"),
        )

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")

    return ReportResponse(
        session_id=session_id,
        question=session.get("question", ""),
        report=session.get("report"),
        iterations=session.get("iterations", 0),
        sources_count=session.get("sources_count", 0),
        sources=[],
        status=session.get("status", "unknown"),
    )


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(request: Request, limit: int = 20):
    """列出最近的研究会话"""
    sessions = session_manager.list_sessions(limit=limit)
    return [
        SessionSummary(
            session_id=s.get("session_id", ""),
            question=s.get("question", ""),
            created_at=s.get("created_at", ""),
            status=s.get("status", "unknown"),
            iterations=s.get("iterations", 0),
            sources_count=s.get("sources_count", 0),
        )
        for s in sessions
    ]


@router.get("/report/{session_id}/stream")
async def stream_report(request: Request, session_id: str):
    """SSE 流式获取研究报告进度"""
    async def event_stream():
        poll_interval = 1.0
        max_wait = 300.0
        elapsed = 0.0

        while elapsed < max_wait:
            cached = _research_cache.get(session_id)
            if cached:
                status = cached.get("status", "completed")
                if status == "completed":
                    yield f"data: {json.dumps({'status': 'completed', 'session_id': session_id, 'report': cached.get('report', ''), 'iterations': cached.get('iterations', 0), 'sources_count': cached.get('sources_count', 0), 'sources': cached.get('sources', [])})}\n\n"
                    return
                elif status == "error":
                    yield f"data: {json.dumps({'status': 'error', 'error': cached.get('error', '')})}\n\n"
                    return

            yield f"data: {json.dumps({'status': 'running', 'session_id': session_id})}\n\n"
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        yield f"data: {json.dumps({'status': 'timeout', 'error': '等待超时'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
