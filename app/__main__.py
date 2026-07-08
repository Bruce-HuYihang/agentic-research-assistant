"""
Agentic Research Assistant - 命令行入口
运行: python -m app
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from app.agent.graph import run_research

console = Console()


async def main():
    console.print(Panel.fit(
        "[bold cyan]自主式研究助手[/bold cyan]\n"
        "输入研究问题，Agent 自动搜索、分析、生成报告\n"
        "输入 [bold]exit[/bold] 退出",
        title="Agentic Research Assistant",
    ))

    while True:
        question = Prompt.ask("\n[bold yellow]研究问题[/bold yellow]")

        if question.lower() in ("exit", "quit", "q"):
            console.print("[dim]再见[/dim]")
            break

        if not question.strip():
            continue

        console.print("\n[dim]开始研究... 这可能需要一些时间[/dim]\n")

        try:
            result = await run_research(question)

            console.print(f"\n[bold green]研究完成[/bold green]")
            console.print(f"   搜索轮次: {result.get('iteration', '?')}")
            console.print(f"   资料数量: {len(result.get('search_results', []))}")

            report = result.get("final_report")
            if report:
                console.print("\n" + "=" * 50)
                console.print(Markdown(report))
                console.print("=" * 50)

                sources = result.get("search_results", [])
                if sources:
                    console.print("\n[bold]来源链接:[/bold]")
                    for r in sources:
                        console.print(f"  - {r.get('title', '?')}: {r.get('url', '')}")
            else:
                console.print("[red]未能生成报告[/red]")

        except Exception as e:
            console.print(f"[red]研究出错: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
