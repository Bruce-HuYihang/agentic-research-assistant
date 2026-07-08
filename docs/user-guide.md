# 🦞 自主式研究助手 — 新手使用指南

> 输入研究问题，AI 自动搜索、反思、生成带引用报告。
> 相当于你的私人研究助理，给个问题它就帮你查资料写综述。

---

## 📋 目录

1. [这是什么？](#1-这是什么)
2. [环境要求](#2-环境要求)
3. [安装步骤](#3-安装步骤)
4. [配置](#4-配置)
5. [三种使用方式](#5-三种使用方式)
   - [方式一：Web 界面（推荐）](#方式一web-界面推荐)
   - [方式二：命令行](#方式二命令行)
   - [方式三：API 调用](#方式三api-调用)
6. [常见问题](#6-常见问题)

---

## 1. 这是什么？

一个自主式研究助手，工作流程如下：

```
你输入问题
    ↓
Agent 拆解为多个子问题 → 规划搜索关键词
    ↓
    百度搜索 → 爬取网页内容
    ↓
    评估信息够不够 → 不够就再搜一轮
    ↓
    够了 → 生成带引用来源的综述报告
```

**举例：** 你输入「量子计算在金融中的应用」，它会：
- 拆解成「量子计算基础」「金融场景案例」「当前技术限制」等子问题
- 搜索百度，爬取相关页面
- 读完觉得不够，再补充搜索
- 最后整合成带引用标注的完整报告

---

## 2. 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 |
| Python | 3.11 或更高版本 |
| 磁盘空间 | 约 500MB（含模型缓存） |
| 网络 | 能访问百度搜索和 DeepSeek API |
| API Key | DeepSeek API Key（免费注册，极其便宜） |

---

## 3. 安装步骤

### 第一步：下载项目

```bash
git clone https://github.com/Bruce-HuYihang/agentic-research-assistant.git
cd agentic-research-assistant
```

如果没有 Git，直接去 https://github.com/Bruce-HuYihang/agentic-research-assistant 点绿色「Code」→「Download ZIP」也一样。

### 第二步：安装依赖

```bash
pip install -e .
```

如果想用全部功能（向量记忆、PDF 解析）：

```bash
pip install -e ".[full]"
```

### 第三步：配置 API Key

复制配置文件：

```bash
copy .env.example .env
```

用记事本打开 `.env`，修改 `DEEPSEEK_API_KEY` 为你自己的 Key：

```
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=sk-这里填你的DeepSeek API Key
```

> 💡 去 https://platform.deepseek.com 注册，充值几块钱够用几个月。

---

## 4. 配置

`.env` 文件里所有配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LLM_PROVIDER` | deepseek | 大模型供应商：deepseek / openai |
| `LLM_MODEL` | deepseek-v4-flash | 模型名称 |
| `DEEPSEEK_API_KEY` | - | **必填**，你的 API Key |
| `SEARCH_PROVIDER` | baidu | 搜索引擎（默认百度，零配置） |
| `MAX_SEARCH_ITERATIONS` | 3 | 最大搜索轮次（越大报告越详细） |
| `API_PORT` | 8090 | 后端端口 |
| `LOG_LEVEL` | INFO | 日志级别：DEBUG / INFO / WARNING |

---

## 5. 三种使用方式

### 方式一：Web 界面（推荐）

最简单，打开浏览器就能用。

**启动后端 API：**

打开第一个命令行窗口：

```bash
cd agentic-research-assistant
uvicorn app.main:app --host 0.0.0.0 --port 8090
```

看到 `Uvicorn running on http://0.0.0.0:8090` 就说明启动了。

**启动前端界面：**

打开第二个命令行窗口：

```bash
cd agentic-research-assistant
streamlit run frontend/app.py
```

浏览器会自动打开，或者手动访问 **http://localhost:8501**

**使用方法：**

1. 在左侧边栏确认 API 地址是 `http://localhost:8090`
2. 在底部输入框输入你的研究问题，回车
3. 等待 Agent 搜索、反思、生成报告（一般 1-3 分钟）
4. 看到完整报告后，可以展开「来源链接」查看引用来源

> ⏱ 第一次运行会慢一些（ChromaDB 要下载模型），后面就快了。

---

### 方式二：命令行

不喜欢网页？命令行也能用。

```bash
cd agentic-research-assistant
python -m app
```

然后输入问题：

```
研究问题：什么是量子计算？

[开始搜索...]
  搜索: 量子计算 原理
  爬取: 量子计算原理解析
  搜索: 量子计算 应用场景
  爬取: 量子计算商业应用50种方式
  ...

研究完成！
==================================================
## 研究报告
量子计算是一种...
==================================================
来源链接:
  - 来源1: http://...
```

输入 `exit` 退出。

---

### 方式三：API 调用

适合开发者集成到自己的项目。

**API 启动后**，用 Python 调用：

```python
import httpx

response = httpx.post(
    "http://localhost:8090/api/v1/research",
    json={
        "question": "什么是量子计算？",
        "deep": True,           # 深度研究模式
        "max_iterations": 3,    # 最大搜索轮次
    },
    timeout=300,
)
data = response.json()
session_id = data["session_id"]

# 获取报告
report = httpx.get(f"http://localhost:8090/api/v1/report/{session_id}")
print(report.json()["report"])
```

**API 端点一览：**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/research` | 发起研究 |
| GET | `/api/v1/report/{id}` | 获取报告 |
| GET | `/api/v1/sessions` | 查看历史记录 |
| GET | `/api/v1/report/{id}/stream` | 流式获取进度 |

API 文档（启动后访问）：**http://localhost:8090/docs**

---

## 6. 常见问题

### Q: 启动报「ModuleNotFoundError」

```bash
pip install -e .
```

重装依赖就行。

### Q: 报错「API Key 错误」

检查 `.env` 文件里的 `DEEPSEEK_API_KEY` 是否正确。Key 一般以 `sk-` 开头。

### Q: 搜索不到结果

百度搜索面向中文，搜英文问题效果差。用中文提问。

### Q: 报告质量不够好

调高 `MAX_SEARCH_ITERATIONS`（`.env` 文件中改），或者在前端勾选「深度研究」模式。

### Q: 403 错误（爬取被拒）

百度文库、知乎等部分网站有反爬机制，会正常跳过不影响整体报告。程序中已有错误处理。

### Q: 怎么关掉服务

在命令行窗口按 `Ctrl + C` 即可停止。

### Q: 想换 OpenAI 的模型

`.env` 中改：

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-你的OpenAI Key
```

---

> **版本**: v0.3.0 | **GitHub**: https://github.com/Bruce-HuYihang/agentic-research-assistant
