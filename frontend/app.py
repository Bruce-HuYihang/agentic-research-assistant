"""
Streamlit 前端原型 — 自主式研究助手 GUI
启动: streamlit run frontend/app.py
"""

import streamlit as st
import httpx
import asyncio
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="自主式研究助手",
    page_icon="🦞",
    layout="wide",
)

# ---- 样式 ----
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .main-header h1 { margin: 0; font-size: 2.2rem; }
    .main-header p { color: #888; margin: 0; }
    .stStatusWidget { margin-bottom: 0.5rem; }
    .sources-list { font-size: 0.85rem; }
    .sidebar-info { font-size: 0.8rem; color: #aaa; }
</style>
""", unsafe_allow_html=True)

# ---- 标题 ----
st.markdown(
    "<div class='main-header'><h1>🦞 自主式研究助手</h1>"
    "<p>输入研究问题，Agent 自动搜索、反思、生成带引用报告</p></div>",
    unsafe_allow_html=True,
)

# ---- 侧边栏 ----
with st.sidebar:
    st.header("⚙️ 配置")

    api_url = st.text_input(
        "API 地址",
        "http://localhost:8090",
        help="FastAPI 后端地址",
    )

    col1, col2 = st.columns(2)
    with col1:
        deep_mode = st.checkbox(
            "深度研究",
            value=True,
            help="启用更多搜索轮次",
        )
    with col2:
        max_iter = st.slider("最大轮次", 1, 8, 3)

    st.divider()
    st.markdown(
        "<div class='sidebar-info'>"
        "Powered by LangGraph + DeepSeek<br>"
        f"Session: {time.strftime('%Y-%m-%d %H:%M')}"
        "</div>",
        unsafe_allow_html=True,
    )

# ---- 主界面 ----
# 初始化状态
if "report" not in st.session_state:
    st.session_state.report = None
if "sources" not in st.session_state:
    st.session_state.sources = []
if "iterations" not in st.session_state:
    st.session_state.iterations = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "running" not in st.session_state:
    st.session_state.running = False
if "error" not in st.session_state:
    st.session_state.error = None
if "history" not in st.session_state:
    st.session_state.history = []

# ---- 输入区域 ----
question = st.chat_input("输入研究问题...", disabled=st.session_state.running)

# ---- 处理用户输入 ----
if question:
    st.session_state.running = True
    st.session_state.error = None
    st.session_state.report = None
    st.session_state.sources = []
    st.session_state.iterations = 0

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(question)

    # 助手响应
    with st.chat_message("assistant"):
        status_placeholder = st.status("🧠 研究进行中...", expanded=True)
        result_placeholder = st.empty()

        try:
            # 调用 API
            status_placeholder.write("🔗 连接研究引擎...")
            async def call_api():
                async with httpx.AsyncClient(timeout=300.0) as client:
                    resp = await client.post(
                        f"{api_url}/api/v1/research",
                        json={
                            "question": question,
                            "deep": deep_mode,
                            "max_iterations": max_iter,
                        },
                    )
                    resp.raise_for_status()
                    return resp.json()

            resp_data = asyncio.run(call_api())
            session_id = resp_data["session_id"]
            st.session_state.session_id = session_id

            status_placeholder.update(
                label="📥 正在获取报告...",
                state="running",
            )

            # 获取完整报告
            async def get_report():
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{api_url}/api/v1/report/{session_id}"
                    )
                    resp.raise_for_status()
                    return resp.json()

            report_data = asyncio.run(get_report())

            st.session_state.report = report_data.get("report")
            st.session_state.sources = report_data.get("sources", [])
            st.session_state.iterations = report_data.get("iterations", 0)
            st.session_state.history.append({
                "question": question,
                "time": datetime.now().isoformat(),
                "session_id": session_id,
            })

            status_placeholder.update(
                label=f"✅ 研究完成（{st.session_state.iterations} 轮搜索）",
                state="complete",
            )

            # 显示报告
            if st.session_state.report:
                result_placeholder.markdown(st.session_state.report)

            # 显示来源
            if st.session_state.sources:
                with st.expander("📎 来源链接", expanded=True):
                    for s in st.session_state.sources:
                        title = s.get("title", "链接")
                        url = s.get("url", "")
                        st.markdown(f"- [{title}]({url})")

        except httpx.ConnectError:
            status_placeholder.update(label="❌ 连接失败", state="error")
            st.error(f"无法连接到 {api_url}，请确认 API 服务已启动")
            st.session_state.error = "连接失败"
        except httpx.TimeoutException:
            status_placeholder.update(label="⏰ 研究超时", state="error")
            st.error("研究超过 5 分钟，请简化问题或增加 API 超时时间")
            st.session_state.error = "超时"
        except Exception as e:
            status_placeholder.update(label="❌ 研究出错", state="error")
            st.error(f"错误: {str(e)}")
            st.session_state.error = str(e)

    st.session_state.running = False
    st.rerun()

# ---- 显示已有结果（回看） ----
elif st.session_state.report:
    with st.chat_message("assistant"):
        st.markdown(st.session_state.report)
        if st.session_state.sources:
            with st.expander("📎 来源链接", expanded=True):
                for s in st.session_state.sources:
                    title = s.get("title", "链接")
                    url = s.get("url", "")
                    st.markdown(f"- [{title}]({url})")
            st.caption(f"共 {st.session_state.iterations} 轮搜索 · {len(st.session_state.sources)} 个来源")

# ---- 历史记录 ----
if st.session_state.history:
    with st.sidebar:
        st.divider()
        st.header("📋 历史记录")
        for h in reversed(st.session_state.history[-10:]):
            label = h["question"][:50] + "..." if len(h["question"]) > 50 else h["question"]
            st.caption(f"🕐 {label}")
