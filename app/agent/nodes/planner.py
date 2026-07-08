import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ResearchState
from app.config import settings


PLANNER_PROMPT = """你是一个研究规划专家。你的任务是将用户的问题拆解为多个子问题，
并为每个子问题设计搜索查询。

当前已完成的研究背景：
{context}

当前已识别的知识缺口：
{gaps}

请生成接下来的搜索计划。注意：
1. 搜索工具是**百度搜索（中文搜索引擎）**，所以**搜索查询必须用中文编写**
2. 问题涉及哪些核心概念
3. 需要哪些方面的证据（技术、市场、应用、限制等）
4. 是否有相互矛盾的观点需要查证
5. 优先搜索最基础、最长青的资料
6. 搜索词要简洁、精准，类似于用户在百度搜索时输入的关键词

输出 JSON 格式：
```json
{{
  "sub_questions": ["子问题1", "子问题2"],
  "search_queries": [
    {{"query": "中文搜索词1", "priority": 1}},
    {{"query": "中文搜索词2", "priority": 2}}
  ]
}}
```
"""


def planner_node(state: ResearchState) -> dict:
    """规划节点：拆解问题 → 生成搜索查询"""

    # 第一次运行（iteration=0）→ 完整规划
    # 后续运行（iteration>0）→ 基于知识缺口补充规划

    context = "暂无" if not state.search_results \
        else "\n".join(
            f"- {r['url']}: {r['content'][:200]}..."
            for r in state.search_results[-3:]
        )

    gaps_str = "、".join(state.knowledge_gaps) if state.knowledge_gaps else "无"

    messages = [
        SystemMessage(content=PLANNER_PROMPT.format(
            context=context,
            gaps=gaps_str,
        )),
        HumanMessage(
            content=f"用户问题：{state.research_question}\n\n"
                    f"当前轮次：第 {state.iteration + 1} 轮"
        ),
    ]

    # 调用 LLM
    response = settings.llm.invoke(messages)
    plan = _parse_plan(response.content)

    return {
        "sub_questions": plan.get("sub_questions", []),
        "search_plan": plan.get("search_queries", []),
        "iteration": state.iteration + 1,
        "current_step": f"规划阶段 - 第 {state.iteration + 1} 轮",
    }


def _parse_plan(text: str) -> dict:
    """从 LLM 响应中提取规划 JSON"""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # fallback: 直接尝试解析
    return json.loads(text)
