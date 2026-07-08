# 🦞 Agentic Research Assistant

**自主式研究助手** — 输入问题，AI 自动规划搜索、爬取网页、反思缺口、生成带引用综述报告。

## 快速开始

`ash
# 1. 安装
git clone https://github.com/Bruce-HuYihang/agentic-research-assistant.git
cd agentic-research-assistant
pip install -e .

# 2. 配置
copy .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 3. 运行（API + 前端）
uvicorn app.main:app --host 0.0.0.0 --port 8090     # 终端1
streamlit run frontend/app.py                         # 终端2

# 或命令行直接玩
python -m app
`

然后浏览器打开 **http://localhost:8501** 即可使用。

## 使用指南

详细教程见 [docs/user-guide.md](docs/user-guide.md)

## 项目结构

`
agentic-research/
├── app/
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 全配置化
│   ├── agent/            # Agent 核心
│   │   ├── graph.py      # LangGraph 循环图
│   │   ├── state.py      # 状态模型
│   │   └── nodes/        # 节点
│   │       ├── planner.py    # 规划
│   │       ├── executor.py   # 搜索执行
│   │       ├── reflector.py  # 反思评估
│   │       └── generator.py  # 报告生成
│   ├── tools/            # 工具层
│   │   ├── search.py     # 百度搜索
│   │   ├── fetch.py      # 网页爬取
│   │   └── pdf_parser.py # PDF 解析
│   ├── memory/           # 记忆层
│   │   ├── chroma_store.py  # 向量存储
│   │   └── session.py       # 会话管理
│   └── api/              # API
│       ├── routes.py     # REST 路由
│       └── schemas.py    # 数据模型
├── frontend/app.py       # Streamlit 界面
├── tests/                # 单元测试（9个）
├── docs/user-guide.md    # 使用指南
├── Dockerfile
└── docker-compose.yml
`

## 技术栈

- **Agent 框架**: LangGraph
- **大模型**: DeepSeek V4（默认）/ OpenAI
- **搜索**: 百度搜索（零 API Key，国内畅通）
- **向量库**: ChromaDB + bge-m3
- **后端**: FastAPI + Uvicorn
- **前端**: Streamlit
- **部署**: Docker Compose
