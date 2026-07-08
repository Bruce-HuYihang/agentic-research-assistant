"""集成测试：端到端流程测试（需要 API Key 和网络）"""
import pytest
from app.agent.graph import build_research_graph, run_research
from app.agent.state import ResearchState


class TestGraph:
    """测试 LangGraph 状态图"""

    def test_build_graph(self):
        """测试图能正常构建"""
        graph = build_research_graph()
        assert graph is not None
        assert hasattr(graph, "ainvoke")

    @pytest.mark.asyncio
    async def test_graph_compile(self):
        """测试图的编译（不含实际执行）"""
        graph = build_research_graph()
        # 验证图结构
        nodes = graph.get_graph().nodes
        assert "planner" in nodes
        assert "executor" in nodes
        assert "reflector" in nodes
        assert "generator" in nodes


class TestSessionManager:
    """测试会话管理"""

    def test_session_crud(self):
        from app.memory.session import SessionManager
        import tempfile, os

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SessionManager(storage_dir=tmpdir)
            sid = sm.create_session("测试问题")
            assert sid is not None

            session = sm.get_session(sid)
            assert session is not None
            assert session["question"] == "测试问题"
            assert session["status"] == "created"

            sm.update_session(sid, {"status": "completed", "iterations": 3})
            updated = sm.get_session(sid)
            assert updated["status"] == "completed"
            assert updated["iterations"] == 3

            sessions = sm.list_sessions(limit=5)
            assert len(sessions) == 1
