from app.agent.state import ResearchState


async def generator_node(state: ResearchState) -> dict:
    """生成最终研究报告"""

    # 聚合所有搜索结果
    sources_text = ""
    for i, r in enumerate(state.search_results):
        sources_text += f"\n## 来源 {i+1}: {r['title']}\n"
        sources_text += f"URL: {r['url']}\n"
        sources_text += f"内容:\n{r['content'][:1500]}\n"

    # 历史记忆上下文（Phase 3）
    memory_text = ""
    if state.memory_matches:
        memory_text = "\n\n### 历史知识库匹配结果\n"
        for i, m in enumerate(state.memory_matches):
            meta = m.get("metadata", {})
            memory_text += f"\n## 记忆 {i+1}: {meta.get('title', '无标题')}\n"
            memory_text += f"URL: {meta.get('url', '')}\n"
            memory_text += f"内容摘要:\n{m.get('content', '')[:1000]}\n"

    prompt = f"""你是一个研究分析专家。基于以下收集到的资料，为用户的问题撰写一篇完整的研究报告。

用户问题: {state.research_question}

共搜索了 {state.iteration} 轮，收集了 {len(state.search_results)} 份资料。

收集到的资料:
{sources_text}

{memory_text}

要求：
1. 报告结构完整：结论先行，然后展开分析
2. 引用来源：在相关论述后标注 [来源1][来源2]
3. 指出不同来源之间的共识和分歧
4. 如果有知识盲区，如实说明
5. 用中文撰写"""

    from app.config import settings
    from langchain_core.messages import SystemMessage, HumanMessage

    messages = [
        SystemMessage(content="你是一个专业的研究分析专家，擅长整合多源信息撰写综述报告。"),
        HumanMessage(content=prompt),
    ]

    response = settings.llm.invoke(messages)
    report = response.content

    return {
        "final_report": report,
        "current_step": "报告已生成",
    }
