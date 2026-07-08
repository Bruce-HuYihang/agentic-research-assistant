"""执行节点：按规划搜索和爬取（Phase 3: 含记忆增强）"""

from loguru import logger
from app.agent.state import ResearchState
from app.tools.search import baidu_search
from app.tools.fetch import fetch_page
from app.memory.chroma_store import get_knowledge_store, HAS_CHROMA


async def executor_node(state: ResearchState) -> dict:
    """按规划执行搜索和爬取"""

    new_results = []
    visited_urls = set(state.visited_urls)
    memory_matches = []

    # ---- 记忆增强检索 ----
    if state.use_memory and HAS_CHROMA:
        try:
            store = get_knowledge_store()
            for plan_item in state.search_plan:
                query = plan_item["query"]
                matches = store.search(query, k=3)
                for m in matches:
                    if m["content"] and m not in memory_matches:
                        memory_matches.append(m)
            if memory_matches:
                logger.info(f"记忆库命中 {len(memory_matches)} 条历史记录")
        except Exception as e:
            logger.warning(f"记忆库检索失败: {e}")

    for plan_item in state.search_plan:
        query = plan_item["query"]

        # ---- 1. 搜索 ----
        logger.info(f"搜索: {query}")
        search_data = await baidu_search(query, count=5)

        if not search_data:
            logger.info(f"跳过: 无搜索结果: {query}")
            continue

        # ---- 2. 爬取 ----
        for item in search_data[:3]:
            url = item["url"]

            if url in visited_urls:
                continue
            visited_urls.add(url)

            title = item.get("title", url)[:60]
            logger.info(f"爬取: {title}")

            content = await fetch_page(url)

            if content:
                result_item = {
                    "query": query,
                    "url": url,
                    "title": item.get("title", ""),
                    "content": content[:8000],
                    "snippet": item.get("snippet", ""),
                }
                new_results.append(result_item)

                # ---- 存入知识库 ----
                if state.use_memory and HAS_CHROMA:
                    try:
                        store.add_document(
                            url=url,
                            title=item.get("title", ""),
                            content=content[:5000],
                            metadata={"query": query, "iteration": state.iteration},
                        )
                    except Exception as e:
                        logger.warning(f"存入知识库失败: {e}")

    return {
        "search_results": [*state.search_results, *new_results],
        "visited_urls": visited_urls,
        "memory_matches": memory_matches,
        "current_step": "执行完成",
    }
