import asyncio
from langgraph.graph import StateGraph, END
from app.agent.state import ResearchState
from app.agent.nodes.planner import planner_node
from app.agent.nodes.executor import executor_node
from app.agent.nodes.generator import generator_node


def build_research_graph() -> StateGraph:
    """构建研究 Agent 的状态图（Phase 1: 规划 → 执行 → 生成）"""

    workflow = StateGraph(ResearchState)

    # 注册节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("generator", generator_node)

    # 设置入口
    workflow.set_entry_point("planner")

    # 连接边：规划 → 执行 → 生成
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "generator")
    workflow.add_edge("generator", END)

    return workflow.compile()


async def run_research(question: str, max_iterations: int = 3) -> ResearchState:
    """异步执行一项研究任务"""
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
