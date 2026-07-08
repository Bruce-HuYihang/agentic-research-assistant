"""反思节点：评估当前收集的信息是否足够回答研究问题"""
import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ResearchState
from app.config import settings


REFLECTOR_PROMPT = """你是一个研究质量评估专家。你的任务是根据已收集的信息判断是否足够回答用户的研究问题。

请仔细阅读以下研究问题、已收集的信息（搜索结果），然后以 JSON 格式返回评估结果。

评估维度：
1. **覆盖度**：是否涵盖了所有子问题？有无明显遗漏？
2. **深度**：信息是否足够深入，还是只有表面摘要？
3. **时效性**：引用的资料是否够新？（特别是技术类问题）
4. **多角度**：是否考虑了不同观点、正反两面？
5. **可信度**：来源是否可靠？有无过时信息？

返回格式（严格 JSON，不要附加其他文本）：
```json
{{
  "is_satisfied": false,
  "gaps": ["缺口1描述", "缺口2描述"],
  "missing_aspects": ["缺失的方面1"],
  "confidence": 5,
  "reasoning": "简要理由"
}}
```

注意：
- confidence 为 0-10 的整数，>=7 才认为信息充足
- gaps 和 missing_aspects 可以是空列表
- reasoning 提供简短分析
"""


async def reflector_node(state: ResearchState) -> dict:
    """反思节点：评估当前迭代收集的信息质量"""

    # 构造输入内容，只看最近 5 条避免超长
    search_results_text = ""
    if state.search_results:
        for i, result in enumerate(state.search_results[-5:]):
            title = result.get("title", "无标题")
            snippet = result.get("snippet", "")[:300]
            url = result.get("url", "")
            search_results_text += f"\n[{i+1}] {title}\n   URL: {url}\n   摘要: {snippet}\n"

    if not search_results_text.strip():
        return {
            "is_satisfied": False,
            "knowledge_gaps": ["没有搜索到任何结果"],
            "reflection_notes": ["搜索结果为空，无法评估"],
        }

    messages = [
        SystemMessage(content=REFLECTOR_PROMPT),
        HumanMessage(content=(
            f"研究问题：{state.research_question}\n\n"
            f"已搜索轮次：第 {state.iteration} 轮（最大 {state.max_iterations} 轮）\n\n"
            f"当前搜索结果（最近5条）：{search_results_text}"
        )),
    ]

    try:
        response = settings.llm.invoke(messages)
        assessment = _parse_reflection(response.content)

        is_satisfied = assessment.get("is_satisfied", False)
        confidence = assessment.get("confidence", 0)
        # confidence >= 7 才算 satisfied
        is_satisfied = is_satisfied and (confidence >= 7)

    except Exception as e:
        # 解析失败时保守返回不满足
        return {
            "is_satisfied": False,
            "knowledge_gaps": [f"评估结果解析失败: {e}"],
            "reflection_notes": ["LLM 返回解析异常"],
        }

    return {
        "is_satisfied": is_satisfied,
        "knowledge_gaps": assessment.get("gaps", []),
        "reflection_notes": [assessment.get("reasoning", "")],
    }


def _parse_reflection(text: str) -> dict:
    """从 LLM 响应中提取评估 JSON"""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # fallback: 直接尝试解析
    return json.loads(text)
