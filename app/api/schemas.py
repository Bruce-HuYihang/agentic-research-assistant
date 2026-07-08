"""FastAPI 请求/响应模型"""

from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    """发起研究请求"""
    question: str = Field(..., min_length=1, description="研究问题")
    deep: bool = Field(False, description="是否启用深度研究（更多搜索轮次）")
    max_iterations: Optional[int] = Field(None, ge=1, le=10, description="最大搜索轮次（覆盖 deep 参数）")


class ResearchResponse(BaseModel):
    """研究任务响应"""
    session_id: str
    question: str
    status: str = "completed"  # completed | running | error


class ReportResponse(BaseModel):
    """研究报告详情"""
    session_id: str
    question: str
    report: Optional[str] = None
    iterations: int = 0
    sources_count: int = 0
    sources: list[dict] = Field(default_factory=list)
    status: str = "pending"
    error: Optional[str] = None


class SessionSummary(BaseModel):
    """会话摘要"""
    session_id: str
    question: str
    created_at: str
    status: str
    iterations: int = 0
    sources_count: int = 0


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    session_id: Optional[str] = None
