"""快速端到端测试"""
import asyncio
from app.agent.graph import run_research


async def test():
    result = await run_research("Python 的 asyncio 是什么", max_iterations=1)
    # ainvoke 返回 dict，用 key 访问
    print(f"轮次: {result.get('iteration')}")
    print(f"资料: {len(result.get('search_results', []))} 条")
    for r in result.get('search_results', [])[:3]:
        print(f"  - {r.get('title', '?'):.50s}: {r.get('url', '')}")
    print()
    report = result.get('final_report')
    if report:
        print(report[:500])
    else:
        print("(无报告)")


asyncio.run(test())
