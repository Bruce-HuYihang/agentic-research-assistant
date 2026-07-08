import asyncio
from baidusearch.baidusearch import search as baidu_search_raw


async def baidu_search(query: str, count: int = 10) -> list[dict]:
    """
    使用 baidusearch 库搜索百度。
    返回 [{"title": ..., "url": ..., "snippet": ...}, ...]
    """
    # baidusearch 是同步库，在线程池中运行
    raw_results = await asyncio.to_thread(baidu_search_raw, query, num_results=count)

    results = []
    for r in raw_results:
        title = r.get("title", "").strip()
        url = r.get("url", "").strip()
        snippet = r.get("abstract", "").strip()

        # 跳过无效结果（空标题、空URL、百度站内搜索）
        if not title or not url:
            continue
        if "/s?" in url or "baidu.com/s" in url:
            continue

        results.append({
            "title": title,
            "url": url,
            "snippet": snippet[:300],
        })

    return results
