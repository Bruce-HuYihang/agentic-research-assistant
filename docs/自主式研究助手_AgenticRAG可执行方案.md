# 自主式研究助手（Agentic RAG + 联网搜索）— 可执行方案

> 一个能主动规划搜索路径、爬取网页、阅读 PDF/论文，并生成带引用综述报告的 AI agent。
> 融合 2025–2026 "Deep Research" 模式，可作为个人研究助手或企业情报工具。

---

## 目录

1. [核心架构](#1-核心架构)
2. [技术栈选型](#2-技术栈选型)
3. [项目目录结构](#3-项目目录结构)
4. [分阶段实现路线图](#4-分阶段实现路线图)
5. [关键模块实现](#5-关键模块实现)
6. [部署与运行](#6-部署与运行)
7. [扩展方向](#7-扩展方向)

---

## 1. 核心架构

```
┌──────────────────────────────────────────────────────────┐
│                   用户界面 (Frontend)                      │
│          React + Tailwind / Streamlit / API               │
└────────────────────┬─────────────────────────────────────┘
                     │  HTTP / WebSocket
┌────────────────────▼──────────────────────────────────────┐
│               FastAPI 后端 (Backend)                       │
│                                                           │
│  ┌──────────────────────────────────────────────────┐     │
│  │              Agent 编排引擎                        │     │
│  │    (LangGraph / 自建规划-执行-反思循环)            │     │
│  │                                                   │     │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐         │     │
│  │   │  Planner │→│  Executor│→│ Reflector│──┐      │     │
│  │   └─────────┘  └─────────┘  └─────────┘  │      │     │
│  │        ↑                                 │      │     │
│  │        └───────── 循环直到满意 ───────────┘      │     │
│  └──────────────────────────────────────────────────┘     │
│                                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐   │
│  │ Web Search│ │ Web Fetch│ │ PDF Parse│ │ Vector DB │   │
│  │  Tool     │ │  Tool    │ │  Tool    │ │  Tool     │   │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Agent 工作流

```
用户提问
    │
    ▼
┌──────────────┐
│  Planner     │  分析问题 → 拆解子问题 → 规划搜索路径
│  规划阶段    │  例：研究"量子计算在金融中的应用"
│              │   → 子问题1: 量子计算基础算法
│              │   → 子问题2: 金融场景应用案例
│              │   → 子问题3: 当前技术限制
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Executor    │  按规划依次执行工具调用
│  执行阶段    │  • Search → 获取搜索结果
│              │  • Fetch  → 爬取关键页面
│              │  • Parse  → 阅读 PDF/论文
│              │  • Vector → 存入长期记忆
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Reflector   │  评估收集到的信息是否足够
│  反思阶段    │  • 有无明显知识缺口？
│              │  • 有无相互矛盾的发现？
│              │  • 是否遗漏了某个角度？
└──────┬───────┘
       │
   不够充分 ──→ 回到 Planner 生成补充计划
       │
   足够充分
       │
       ▼
┌──────────────┐
│  Generator   │  整合所有信息 → 生成带引用综述报告
│  生成阶段    │  • Markdown 格式
│              │  • 逐句标注来源
│              │  • 突出共识与分歧
└──────────────┘
```

---

## 2. 技术栈选型

### 核心依赖

| 组件 | 选型 | 版本建议 | 理由 |
|------|------|---------|------|
| 大模型 | DeepSeek V4 / Claude 4 / GPT-5 / Gemini 2.5 | 最新 | DeepSeek 性价比极高，OpenAI 兼容，零额外适配成本 |
| Agent 框架 | **LangGraph** | ≥0.3 | 原生支持图结构 Agent，状态管理成熟 |
| 搜索 API | **百度搜索 (网页抓取)** | — | 免费，零 API Key，国内畅通 |
| 网页爬取 | **httpx + BeautifulSoup4 + jina.ai** | — | 轻量，配合 Markdown 转换 |
| PDF 解析 | **PyMuPDF** (fitz) + **LlamaParse** | — | 本地快速提取 + 高精度混合 |
| 向量数据库 | **Chroma** | ≥0.6 | 零配置，嵌入式，适合个人使用 |
| 嵌入模型 | **OpenAI embeddings** 或 **BGE-M3** | — | 前者简单，后者本地部署 |
| 后端框架 | **FastAPI** | ≥0.115 | Python 异步，原生 SSE/WS 支持 |
| 前端（可选） | **Streamlit** (快速) / **React + Tailwind** (正式) | — | 视需求选择 |

### Python 依赖清单 (`pyproject.toml`)

```toml
[project]
name = "agentic-research-assistant"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    # Agent 框架
    "langgraph>=0.3.0",
    "langchain-core>=0.3.0",
    "langchain-community>=0.3.0",
    "langchain-openai>=0.3.0",
    "langchain-anthropic>=0.3.0",
    "langchain-google-genai>=2.0.0",

    # 搜索 & 爬取
    "httpx[socks]>=0.28",
    "beautifulsoup4>=4.12",
    "markdownify>=0.14",
    "jina>=3.0",

    # PDF 解析
    "PyMuPDF>=1.25",
    "llama-parse>=0.6",

    # 向量
    "chromadb>=0.6",
    "sentence-transformers>=3.0",

    # 后端
    "fastapi[standard]>=0.115",
    "uvicorn[standard]>=0.34",
    "pydantic>=2.0",

    # 工具
    "python-dotenv>=1.0",
    "rich>=13.0",
    "loguru>=0.7",
]
```

---

## 3. 项目目录结构

```
agentic-research/
├── pyproject.toml              # 项目配置与依赖
├── .env                        # API Keys（不提交 Git）
├── .env.example                # 环境变量模板
│
├── app/
│   ├── __init__.py
│   ├── config.py               # 全局配置（模型、API Key 等）
│   │
│   ├── agent/                  # Agent 核心
│   │   ├── __init__.py
│   │   ├── graph.py            # LangGraph 图定义
│   │   ├── state.py            # Agent 状态定义
│   │   ├── nodes/              
│   │   │   ├── __init__.py
│   │   │   ├── planner.py      # 规划节点
│   │   │   ├── executor.py     # 执行节点
│   │   │   ├── reflector.py    # 反思节点
│   │   │   └── generator.py    # 生成节点
│   │   └── prompts.py          # 所有系统提示词
│   │
│   ├── tools/                  # 工具层
│   │   ├── __init__.py
│   │   ├── search.py           # 联网搜索
│   │   ├── fetch.py            # 网页爬取 & 转换
│   │   ├── pdf_parser.py       # PDF/论文解析
│   │   └── vector_store.py     # 向量存储与检索
│   │
│   ├── memory/                 # 记忆层
│   │   ├── __init__.py
│   │   ├── chroma_store.py     # Chroma 封装
│   │   └── session.py          # 会话管理
│   │
│   └── api/                    # 后端接口
│       ├── __init__.py
│       ├── routes.py           # FastAPI 路由
│       ├── schemas.py          # 请求/响应模型
│       └── websocket.py        # 实时流式通信
│
├── frontend/                   # 前端（可选）
│   ├── app.py                  # Streamlit 快速原型
│   └── streamlit_ui.py         # Streamlit 界面组件
│
├── tests/                      
│   ├── test_planner.py
│   ├── test_executor.py
│   ├── test_tools.py
│   └── test_integration.py
│
└── docs/
    └── architecture.md          # 架构说明
```

---

## 4. 分阶段实现路线图

### Phase 1 — 基础设施 & 最小可运行版本（Day 1-2）

**目标**：能跑通一个简单的研究问题，至少执行 1 轮搜索 + 回答

- [x] 搭建项目骨架，配置依赖
- [ ] 实现 `config.py`（读取 `.env`，模型初始化）
- [ ] 实现 `state.py`（Agent 状态模型）
- [ ] 实现 `search.py`（百度搜索封装，免费零配置）
- [ ] 实现 `fetch.py`（网页爬取 + Markdown 转换）
- [ ] 实现 `planner.py`（简单的搜索查询生成）
- [ ] 实现 `generator.py`（基于搜索结果生成回答）
- [ ] 构建最小 LangGraph（Planner → Executor → Generator）
- [ ] 命令行测试：`python -m app.agent.graph`

**产出**：命令行下输入问题，输出带引用的 Markdown 回答

### Phase 2 — 反思循环 & 深度研究（Day 3-4）

**目标**：Agent 能自我反思，发现不足后自动补充搜索

- [ ] 实现 `reflector.py`（评估信息完整性，识别知识缺口）
- [ ] 添加循环机制：Reflector 判断不足 → 回 Planner 补充
- [ ] 设置最大循环次数（默认 3 轮，最多 5 轮）
- [ ] 实现 `pdf_parser.py`（PyMuPDF 提取 + LlamaParse 高精度）
- [ ] 实现 `vector_store.py`（Chroma 存储已处理文档）
- [ ] 优化 Agent State：追踪已搜索过的查询、已获取的 URL，避免重复

**产出**：Agent 能自动补充搜索 2-3 轮，生成更全面的报告

### Phase 3 — 记忆层 & 持久化（Day 5）

**目标**：跨会话的知识积累，同一个话题第二次问不需要重新搜

- [ ] 完善 `chroma_store.py`（添加/检索/去重）
- [ ] 嵌入模型集成（OpenAI Embeddings 或 BGE-M3 本地）
- [ ] 搜索结果自动存入向量库
- [ ] 会话历史管理
- [ ] 实现记忆增强检索（Agent 搜索前先查向量库）

**产出**：Agent 能"记住"之前研究过的内容，长期积累知识库

### Phase 4 — FastAPI 后端 & API（Day 6-7）

**目标**：提供标准化接口，前端或其他服务可以调用

- [ ] 实现 `schemas.py`（请求/响应 Pydantic 模型）
- [ ] 实现 `routes.py`（POST `/research` 发起研究，GET `/report/{id}` 获取报告）
- [ ] 实现 `websocket.py`（实时推送搜索进度、中间结果）
- [ ] 后台任务管理（asyncio 任务池）
- [ ] 错误处理与超时机制

**产出**：`curl` 或 Postman 可直接调用研究助手 API

### Phase 5 — 前端界面（Day 8-10）

**目标**：用户友好的交互界面

**Streamlit 快速原型（半天）**
- [ ] 聊天输入框
- [ ] 实时进度展示（当前在搜什么、已找到什么）
- [ ] 报告 Markdown 渲染
- [ ] 来源链接展示

**React + Tailwind 正式版（可选，Day 9-10）**
- [ ] 项目脚手架（Vite + React + Tailwind）
- [ ] 聊天组件
- [ ] 研究进度流式展示
- [ ] 报告排版与引用高亮
- [ ] 历史记录侧边栏

**产出**：浏览器可打开的 GUI 研究助手

### Phase 6 — 生产化打磨（持续）

**目标**：稳定、可观测、可配置

- [ ] 完整单元测试 + 集成测试
- [ ] 日志系统（loguru）
- [ ] API 限流与并发控制
- [ ] Docker Compose 一键部署
- [ ] 配置化：切换模型、搜索供应商、向量库类型

---

## 5. 关键模块实现

### 5.1 Agent 状态定义 (`app/agent/state.py`)

```python
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ResearchState(BaseModel):
    """Agent 的全局状态，在 LangGraph 节点间传递"""

    # 用户原始问题
    research_question: str

    # 规划阶段
    sub_questions: list[str] = Field(default_factory=list)
    search_plan: list[dict] = Field(default_factory=list)
    # search_plan = [
    #   {"query": "量子计算 Shor 算法 原理", "priority": 1},
    #   {"query": "量子计算 金融 风险分析 2025", "priority": 2},
    # ]

    # 执行阶段
    search_results: list[dict] = Field(default_factory=list)
    # search_results = [
    #   {"query": "...", "url": "...", "content": "markdown..."},
    # ]

    # 已处理的文档/URL（去重用）
    visited_urls: set[str] = Field(default_factory=set)

    # 反思阶段
    reflection_notes: list[str] = Field(default_factory=list)
    knowledge_gaps: list[str] = Field(default_factory=list)
    is_satisfied: bool = False

    # 当前循环计数
    iteration: int = 0
    max_iterations: int = 3

    # 最终输出
    final_report: Optional[str] = None

    # 会话标识
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])

    # 跟踪工具调用时间（供前端进度展示）
    current_step: str = "initializing"
```

### 5.2 LangGraph 图定义 (`app/agent/graph.py`)

```python
from langgraph.graph import StateGraph, END
from app.agent.state import ResearchState
from app.agent.nodes.planner import planner_node
from app.agent.nodes.executor import executor_node
from app.agent.nodes.reflector import reflector_node
from app.agent.nodes.generator import generator_node


def build_research_graph() -> StateGraph:
    """构建研究 Agent 的状态图"""

    workflow = StateGraph(ResearchState)

    # 注册节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflector", reflector_node)
    workflow.add_node("generator", generator_node)

    # 设置入口
    workflow.set_entry_point("planner")

    # 连接边
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "reflector")

    # 条件判断：反思后决定继续还是生成
    workflow.add_conditional_edges(
        "reflector",
        decide_next_step,  # 路由函数
        {
            "continue": "planner",   # 知识不足 → 继续规划
            "generate": "generator", # 信息足够 → 生成报告
        },
    )

    workflow.add_edge("generator", END)

    return workflow.compile()


def decide_next_step(state: ResearchState) -> str:
    """反射节点后的路由决策"""
    if state.is_satisfied:
        return "generate"

    if state.iteration >= state.max_iterations:
        # 达到最大轮次，直接生成（可能不够完美，但避免死循环）
        return "generate"

    return "continue"
```

### 5.3 规划节点 (`app/agent/nodes/planner.py`)

```python
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ResearchState
from app.config import settings


PLANNER_PROMPT = """你是一个研究规划专家。你的任务是将用户的问题拆解为多个子问题，
并为每个子问题设计搜索查询。

当前已完成的研究背景：
{context}

当前已识别的知识缺口：
{gaps}

请生成接下来的搜索计划。考虑：
1. 问题涉及哪些核心概念
2. 需要哪些方面的证据（技术、市场、应用、限制等）
3. 是否有相互矛盾的观点需要查证
4. 优先搜索最基础、最长青的资料

输出 JSON 格式：
```json
{{
  "sub_questions": ["子问题1", "子问题2"],
  "search_queries": [
    {{"query": "搜索查询1", "priority": 1}},
    {{"query": "搜索查询2", "priority": 2}}
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
    import json, re
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # fallback: 直接尝试解析
    return json.loads(text)
```

### 5.4 执行节点 (`app/agent/nodes/executor.py`)

```python
from app.agent.state import ResearchState
from app.tools.search import baidu_search
from app.tools.fetch import fetch_page
from app.tools.pdf_parser import parse_pdf


async def executor_node(state: ResearchState) -> dict:
    """按规划执行搜索和爬取"""

    new_results = []
    visited_urls = set(state.visited_urls)

    for plan_item in state.search_plan:
        query = plan_item["query"]

        # ---- 1. 搜索 ----
        state.current_step = f"搜索: {query}"
        search_data = await baidu_search(query, count=5)

        # ---- 2. 爬取搜索结果 ----
        for item in search_data[:3]:  # 每轮搜索爬取前 3 条
            url = item["url"]

            if url in visited_urls:
                continue  # 已处理过，跳过
            visited_urls.add(url)

            state.current_step = f"读取: {item.get('title', url)[:60]}"

            content = None

            if url.endswith(".pdf") or "arxiv" in url:
                # PDF 文件 → 用解析器
                content = await parse_pdf(url)
            else:
                # HTML 页面 → 爬取并转 Markdown
                content = await fetch_page(url)

            if content:
                new_results.append({
                    "query": query,
                    "url": url,
                    "title": item.get("title", ""),
                    "content": content[:8000],  # 截断避免 token 爆炸
                })

    return {
        "search_results": [*state.search_results, *new_results],
        "visited_urls": visited_urls,
    }
```

### 5.5 反思节点 (`app/agent/nodes/reflector.py`)

```python
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ResearchState
from app.config import settings


REFLECTOR_PROMPT = """你是一个研究质量评估专家。你的任务是判断当前收集的信息是否足够
回答用户的原始问题。

评估维度：
1. **覆盖度**：是否涵盖了所有子问题？有无明显遗漏？
2. **深度**：信息是否足够深入，还是只有表面摘要？
3. **时效性**：引用的资料是否够新？（特别是技术类问题）
4. **多角度**：是否考虑了不同观点、正反两面？
5. **可信度**：来源是否可靠？有无过时信息？

回答格式（JSON）：
```json
{{
  "is_satisfied": true/false,
  "gaps": ["知识缺口1", "知识缺口2"],
  "reasoning": "简要说明判断理由",
  "missing_aspects": ["遗漏的角度"],
  "confidence": 0-10
}}
```

- is_satisfied = true：信息足够，可以生成最终报告
- is_satisfied = false：还有缺口，需要继续搜索
- confidence ≥ 7 才认为 satisfied，否则继续深挖
"""


def reflector_node(state: ResearchState) -> dict:
    """反思节点：评估信息完整性"""

    # 整理已收集的内容摘要供反思使用
    content_summary = "\n\n".join(
        f"## 来源 {i+1}: {r['title']}\nURL: {r['url']}\n内容摘要: {r['content'][:500]}..."
        for i, r in enumerate(state.search_results)
    )

    messages = [
        SystemMessage(content=REFLECTOR_PROMPT),
        HumanMessage(content=(
            f"用户问题：{state.research_question}\n\n"
            f"当前轮次：第 {state.iteration}/{state.max_iterations} 轮\n\n"
            f"已收集的材料：\n{content_summary}"
        )),
    ]

    response = settings.llm.invoke(messages)
    assessment = _parse_reflection(response.content)

    return {
        "is_satisfied": assessment.get("is_satisfied", False),
        "knowledge_gaps": assessment.get("gaps", []),
        "reflection_notes": [assessment.get("reasoning", "")],
    }


def _parse_reflection(text: str) -> dict:
    import json, re
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return {}
```

### 5.6 工具层：搜索 (`app/tools/search.py`)

```python
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


async def baidu_search(query: str, count: int = 10) -> list[dict]:
    """
    搜索百度网页搜索结果。
    免费，无需 API Key，国内畅通。
    返回 [{"title": ..., "url": ..., "snippet": ...}, ...]
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    url = f"https://www.baidu.com/s?wd={quote_plus(query)}&ie=utf-8"

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for item in soup.select(".result, .c-container")[:count]:
        link = item.select_one("a[href^='http']")
        if not link:
            continue
        href = link.get("href", "")
        title = link.get_text(strip=True)
        snippet_el = item.select_one(".c-abstract, .content-right_3Yq1, .c-span-last")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        results.append({
            "title": title,
            "url": href,
            "snippet": snippet[:300],
        })

    return results


# 备选：如果上面的解析方式跑不通，可以用 baidusearch 库
# pip install baidusearch
# from baidusearch import search as baidu_search_raw
#
# async def baidu_search(query, count=10):
#     results = baidu_search_raw(query, num_results=count)
#     return [{"title": r["title"], "url": r["url"], "snippet": r["abstract"]} for r in results]
```

### 5.7 工具层：网页爬取 (`app/tools/fetch.py`)

```python
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md


async def fetch_page(url: str) -> str | None:
    """
    爬取网页并转换为 Markdown 格式。
    返回 Markdown 文本，失败返回 None。
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
    except Exception as e:
        # 记录日志但不要让单个页面拖垮整个研究
        print(f"[WARN] 爬取失败 {url}: {e}")
        return None

    # 检测编码
    content_type = resp.headers.get("content-type", "")
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].split(";")[0].strip()
        resp.encoding = charset
    else:
        resp.encoding = "utf-8"

    # 解析 HTML
    soup = BeautifulSoup(resp.text, "html.parser")

    # 移除无用元素
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    body = soup.find("body") or soup.find("html") or soup

    # 转换为 Markdown
    markdown_text = md(
        str(body),
        heading_style="ATX",    # 用 ## 风格标题
        bullets="-",            # 用 - 做列表符号
        strip=["a", "img"],     # 删除链接和图片（保留文本）
    )

    # 清理多余空行
    lines = [line.strip() for line in markdown_text.split("\n") if line.strip()]
    cleaned = "\n".join(lines)

    # 截断长度，避免 token 爆炸
    max_chars = 10000
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n...[内容截断]..."

    return cleaned
```

### 5.8 工具层：PDF 解析 (`app/tools/pdf_parser.py`)

```python
import httpx
import fitz  # PyMuPDF
from pathlib import Path
import tempfile


async def parse_pdf(pdf_source: str) -> str | None:
    """
    解析 PDF 文件。支持 URL 和本地路径。
    返回提取的文本内容。
    """
    pdf_bytes = None

    # 判断是 URL 还是本地路径
    if pdf_source.startswith(("http://", "https://")):
        # 在线 PDF → 下载
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(pdf_source, headers=headers)
                resp.raise_for_status()
                pdf_bytes = resp.content
        except Exception as e:
            print(f"[WARN] PDF 下载失败 {pdf_source}: {e}")
            return None
    else:
        # 本地文件
        path = Path(pdf_source)
        if not path.exists():
            return None
        pdf_bytes = path.read_bytes()

    # PyMuPDF 解析
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            text_parts.append(f"--- 第 {page_num + 1} 页 ---\n{text}")

            # 防止超大 PDF 耗光内存
            if sum(len(t) for t in text_parts) > 50000:
                text_parts.append("\n\n[内容截断：超过 50,000 字符限制]...")
                break

        doc.close()
        return "\n\n".join(text_parts)

    except Exception as e:
        print(f"[WARN] PDF 解析失败: {e}")
        return None


def parse_pdf_sync(pdf_path: str | Path) -> str | None:
    """同步版本（用于不需要 async 的场景）"""
    import asyncio
    return asyncio.run(parse_pdf(str(pdf_path)))
```

### 5.9 记忆层：Chroma 向量存储 (`app/memory/chroma_store.py`)

```python
import chromadb
from chromadb.config import Settings
from typing import Optional

# 可选嵌入模型
try:
    from sentence_transformers import SentenceTransformer

    class LocalEmbedder:
        def __init__(self, model_name: str = "BAAI/bge-m3"):
            self.model = SentenceTransformer(model_name)

        def embed(self, texts: list[str]) -> list[list[float]]:
            return self.model.encode(texts, normalize_embeddings=True).tolist()

    USE_LOCAL_EMBED = True
    embedder = LocalEmbedder()

except ImportError:
    USE_LOCAL_EMBED = False
    embedder = None


class KnowledgeStore:
    """持久化研究知识库——跨会话共享"""

    def __init__(self, persist_dir: str = "./knowledge_store"):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="research_notes",
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(
        self,
        url: str,
        title: str,
        content: str,
        metadata: Optional[dict] = None,
    ):
        """将文档存入向量库"""
        doc_id = _make_id(url)

        # 去重：已存在的跳过
        existing = self.collection.get(ids=[doc_id])
        if existing["ids"]:
            return

        self.collection.add(
            documents=[content],
            metadatas=[{
                "url": url,
                "title": title,
                **(metadata or {}),
            }],
            ids=[doc_id],
        )

    def search(self, query: str, k: int = 5) -> list[dict]:
        """语义检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
        )

        documents = []
        for i in range(len(results["ids"][0])):
            documents.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else None,
            })

        return documents

    def count(self) -> int:
        return self.collection.count()


def _make_id(url: str) -> str:
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()
```

### 5.10 FastAPI 后端 (`app/api/routes.py`)

```python
from fastapi import APIRouter, BackgroundTasks
from app.api.schemas import ResearchRequest, ResearchResponse
from app.agent.graph import build_research_graph

router = APIRouter(prefix="/api/v1")

# Agent 实例缓存（生产环境应使用连接池或分布式状态管理）
_agent_cache: dict[str, any] = {}


@router.post("/research")
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
):
    """
    发起一项研究任务。

    - question: 研究问题
    - deep: 是否启用深度研究（更多搜索轮次）
    - max_iterations: 最大搜索轮次
    - callback: 可选的结果回调 URL
    """
    graph = build_research_graph()

    initial_state = {
        "research_question": request.question,
        "max_iterations": request.max_iterations or 5 if request.deep else 3,
    }

    # 在后台任务中执行
    # 生产环境建议使用 Celery / Arq / 消息队列
    result = await graph.ainvoke(initial_state)

    return ResearchResponse(
        question=result["research_question"],
        report=result["final_report"],
        iterations=result["iteration"],
        sources=[
            r["url"] for r in result["search_results"]
        ],
        session_id=result["session_id"],
    )


@router.get("/report/{session_id}")
async def get_report(session_id: str):
    """获取已完成的研究报告"""
    # 需要实现持久化存储
    # 此处为示例骨架
    return {"session_id": session_id, "status": "pending"}
```

### 5.11 配置 (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional


class Settings(BaseSettings):
    """应用配置——自动从 .env 文件和环境变量读取"""

    # ---- 模型 ----
    LLM_PROVIDER: str = "deepseek"     # deepseek / openai / anthropic / google
    LLM_MODEL: str = "deepseek-v4-flash"

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # ---- 搜索（百度搜索，无需 API Key） ----
    SEARCH_FRESHNESS: str = "month"   # month / week / day / year

    # ---- 向量库 ----
    VECTOR_STORE_PATH: str = "./knowledge_store"
    EMBEDDING_MODEL: str = "bge-m3"    # bge-m3（本地，推荐）/ openai（需要额外 API Key）

    # ---- Agent ----
    MAX_SEARCH_ITERATIONS: int = 3
    MAX_TOKENS_PER_SOURCE: int = 8000

    # ---- API ----
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8090

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def llm(self):
        """延迟初始化 LLM 实例"""
        if self.LLM_PROVIDER == "deepseek":
            return ChatOpenAI(
                model=self.LLM_MODEL,
                temperature=0.3,
                api_key=self.DEEPSEEK_API_KEY,
                base_url=self.DEEPSEEK_BASE_URL,
            )
        elif self.LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=self.LLM_MODEL,
                temperature=0.3,
            )
        elif self.LLM_PROVIDER == "anthropic":
            return ChatAnthropic(
                model=self.LLM_MODEL or "claude-sonnet-4-20250514",
                temperature=0.3,
            )
        elif self.LLM_PROVIDER == "google":
            return ChatGoogleGenerativeAI(
                model=self.LLM_MODEL or "gemini-2.5-pro-exp-03-25",
                temperature=0.3,
            )
        raise ValueError(f"Unknown LLM provider: {self.LLM_PROVIDER}")


settings = Settings()
```

### 5.12 Streamlit 快速原型 (`frontend/app.py`)

```python
"""
Streamlit 前端原型——即时可用，无需 Node.js
启动：streamlit run frontend/app.py
"""
import streamlit as st
import httpx
import json
import asyncio

st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 自主式研究助手")
st.caption("输入研究问题，Agent 自动搜索、爬取、反思、生成综述报告")

# ---- 侧边栏 ----
with st.sidebar:
    st.header("配置")
    api_url = st.text_input("API 地址", "http://localhost:8090")
    deep_mode = st.checkbox("深度研究模式", value=True,
                            help="启用更多搜索轮次，生成更详尽的报告")
    max_iter = st.slider("最大搜索轮次", 1, 10, 3)

    st.divider()
    st.caption("Powered by LangGraph + Baidu Search")

# ---- 主界面 ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# 历史展示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
if prompt := st.chat_input("输入研究问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        status_placeholder = st.status("研究中...", expanded=True)

        try:
            with status_placeholder:
                st.write("🔍 正在连接研究引擎...")

                # 调用后端 API
                with st.spinner("Agent 正在搜索、分析、反思..."):
                    resp = httpx.post(
                        f"{api_url}/api/v1/research",
                        json={
                            "question": prompt,
                            "deep": deep_mode,
                            "max_iterations": max_iter,
                        },
                        timeout=120.0,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                status_placeholder.update(label="✅ 研究完成", state="complete")

            # 展示报告
            report = data.get("report", "（无生成结果）")
            st.markdown("## 📄 研究报告")
            st.markdown(report)

            # 来源
            sources = data.get("sources", [])
            if sources:
                with st.expander("📎 来源链接"):
                    for s in sources:
                        st.write(f"- [{s}]({s})")

            st.caption(f"共搜索 {data.get('iterations', '?')} 轮")

            st.session_state.messages.append({
                "role": "assistant",
                "content": report,
            })

        except Exception as e:
            status_placeholder.update(label="❌ 研究失败", state="error")
            st.error(f"错误: {e}")
```

---

## 6. 部署与运行

### 6.1 快速启动（开发模式）

```bash
# 1. 克隆项目
git clone <your-repo> agentic-research
cd agentic-research

# 2. 安装依赖
pip install -e .

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 DeepSeek API Key 即可（百度搜索无需配置）

# 4. 启动 API 服务
uvicorn app.api.routes:router --host 0.0.0.0 --port 8090 --reload

# 5. （可选）启动 Streamlit UI
streamlit run frontend/app.py
```

### 6.2 `.env.example`

```bash
# ---- 大模型（DeepSeek 优先，也可用 OpenAI/Anthropic/Google） ----
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-v4-flash

DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...

# ---- 搜索（百度搜索，零配置，国内畅通） ----
SEARCH_FRESHNESS=month

# ---- 向量库 ----
VECTOR_STORE_PATH=./knowledge_store
EMBEDDING_MODEL=openai  # 或 bge-m3（需要 sentence-transformers）
```

### 6.3 Docker Compose（生产部署）

```yaml
# docker-compose.yml
version: "3.9"

services:
  research-api:
    build: .
    ports:
      - "8090:8090"
    env_file: .env
    volumes:
      - ./knowledge_store:/app/knowledge_store
    restart: unless-stopped

  # 可选：Streamlit UI
  research-ui:
    image: python:3.11-slim
    command: streamlit run frontend/app.py
    ports:
      - "8501:8501"
    depends_on:
      - research-api
    environment:
      - API_URL=http://research-api:8090
    volumes:
      - ./frontend:/app/frontend
```

### 6.4 所需 API Key 获取

| 服务 | 用途 | 注册地址 | 费用 |
|------|------|---------|------|
| 百度搜索 | 联网搜索（推荐） | pip install baidusearch | 免费，零 API Key |
| DeepSeek | LLM（首选） | https://platform.deepseek.com | 极其便宜 |
| LlamaParse | PDF 高精度解析 | https://cloud.llamaindex.ai | 免费 1000 页/天 |

---

## 7. 扩展方向

### 已规划

| 特性 | 优先级 | 说明 |
|------|--------|------|
| 多语言支持 | 中 | Agent 能理解中英文混合问题 |
| 自定义知识库注入 | 中 | 上传私有 PDF/文档供 Agent 参考 |
| 报告导出 | 低 | PDF / LaTeX / Notion 导出 |
| 定时监控 | 低 | 对特定关键词持续追踪新资料 |
| 多搜索源切换 | 低 | 可插拔设计，后期加搜狗/360等 |

### 大胆一些

- **多 Agent 辩论**：两个 Agent 对同一问题分别研究，然后辩论找出分歧，生成更平衡的报告
- **可视化知识图谱**：将研究结果绘制为概念关系图，而非纯文本报告
- **论文推荐引擎**：根据当前研究内容，主动推荐相关的未读论文
- **自动化文献综述**：输入一个研究方向，自动搜刮 arXiv + Semantic Scholar，输出结构化综述

---

> **方案版本**: v1.0  
> **适用场景**: 个人研究辅助 / 企业竞争情报 / 学术文献综述  
> **预估工期**: 10 天（单人，业余时间），4-5 天（全职）
