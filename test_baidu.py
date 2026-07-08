"""测试 baidusearch 库"""
from baidusearch.baidusearch import search as baidu_search_raw


results = baidu_search_raw("Python asyncio 入门教程", num_results=5)
print(f"Got {len(results)} results")
for r in results[:5]:
    print(f"  - {r.get('title', '?')[:60]}")
    print(f"    URL: {r.get('url', '')[:80]}")
    print(f"    abstract: {r.get('abstract', '')[:100]}")
    print()
