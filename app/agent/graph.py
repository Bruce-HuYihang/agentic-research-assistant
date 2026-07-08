"""定义 LangGraph 状态图（Phase 2: Planner → Executor → Reflector 循环）"""
import asyncio
from langgraph.graph import StateGraph, END
from app.agent.state import ResearchState
from app.agent.nodes.planner import planner_node
from app.agent.nodes.executor import executor_node
from app.agent.nodes.reflector import reflector_node
from app.agent.nodes.generator import generator_node


def decide_next_step(state: ResearchState) -> str:
    """条件路由函数：根据 reflector 的评估决定下一步"""
    if state.is_satisfied or state.iteration >= state.max_iterations:
        return "generator"
    return "planner"


def build_research_graph() -> StateGraph:
    """构建研究 Agent 的状态图（Phase 2: 含反思循环）"""

    workflow = StateGraph(ResearchState)

    # 注册节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflector", reflector_node)
    workflow.add_node("generator", generator_node)

    # 设置入口
    workflow.set_entry_point("planner")

    # 直线连接
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "reflector")

    # 条件路由：reflector → generator（完成）或 planner（继续搜索）
    workflow.add_conditional_edges(
        "reflector",
        decide_next_step,
        {
            "generator": "generator",
            "planner": "planner",
        },
    )

    workflow.add_edge("generator", END)

    return workflow.compile()


async def run_research(question: str, max_iterations: int = 3) -> ResearchState:
    """异步执行一项研究任务（Phase 2: 带反思循环）"""
    graph = build_research_graph()

    initial_state = ResearchState(
        research_question=question,
        max_iterations=max_iterations,
    )

    result = await graph.ainvoke(initial_state)
    return result


def run_research_sync(question: str, max_iterations: int = 3) -> ResearchState:
    """同步执行一项研究任务（方便命令行调用）"""
    return asyncio.run(run_research(question, max_iterations))
