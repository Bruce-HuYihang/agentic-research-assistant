from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ResearchState(BaseModel):
    """Agent 的全局状态，在 LangGraph 节点间传递"""

    # 用户原始问题
    research_question: str

    # 规划阶段
    sub_questions: list[str] = Field(default_factory=list)
    search_plan: list[dict] = Field(default_factory=list)

    # 执行阶段
    search_results: list[dict] = Field(default_factory=list)

    # 已处理的文档/URL（去重用）
    visited_urls: list[str] = Field(default_factory=list)

    # 反思阶段
    reflection_notes: list[str] = Field(default_factory=list)
    knowledge_gaps: list[str] = Field(default_factory=list)
    is_satisfied: bool = False

    # 当前循环计数
    iteration: int = 0
    max_iterations: int = 3

    # 最终输出
    final_report: Optional[str] = None

    # 会话标识
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])

    # 记忆增强（Phase 3）
    use_memory: bool = True
    memory_matches: list[dict] = Field(default_factory=list)

    # 跟踪工具调用时间（供前端进度展示）
    current_step: str = "initializing"
