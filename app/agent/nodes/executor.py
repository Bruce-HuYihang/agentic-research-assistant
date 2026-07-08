from app.agent.state import ResearchState
from app.tools.search import baidu_search
from app.tools.fetch import fetch_page


async def executor_node(state: ResearchState) -> dict:
    """按规划执行搜索和爬取"""

    new_results = []
    visited_urls = set(state.visited_urls)

    for plan_item in state.search_plan:
        query = plan_item["query"]

        # ---- 1. 搜索 ----
        print(f"  [搜索] {query}")
        state.current_step = f"搜索: {query}"
        search_data = await baidu_search(query, count=5)

        if not search_data:
            print(f"  [跳过] 无搜索结果: {query}")
            continue

        # ---- 2. 爬取搜索结果 ----
        for item in search_data[:3]:  # 每轮搜索爬取前 3 条
            url = item["url"]

            if url in visited_urls:
                continue  # 已处理过，跳过
            visited_urls.add(url)

            title = item.get("title", url)[:60]
            print(f"  [爬取] {title}")
            state.current_step = f"读取: {title}"

            content = await fetch_page(url)

            if content:
                new_results.append({
                    "query": query,
                    "url": url,
                    "title": item.get("title", ""),
                    "content": content[:8000],
                    "snippet": item.get("snippet", ""),
                })

    return {
        "search_results": [*state.search_results, *new_results],
        "visited_urls": visited_urls,
    }
