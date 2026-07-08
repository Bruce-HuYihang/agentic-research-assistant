"""单元测试：核心模块"""
import pytest
from uuid import uuid4

from app.agent.state import ResearchState


class TestResearchState:
    """测试状态模型"""

    def test_default_creation(self):
        s = ResearchState(research_question="测试问题")
        assert s.research_question == "测试问题"
        assert s.sub_questions == []
        assert s.search_plan == []
        assert s.search_results == []
        assert s.visited_urls == set()
        assert s.is_satisfied is False
        assert s.iteration == 0
        assert s.max_iterations == 3
        assert s.final_report is None
        assert s.use_memory is True
        assert s.memory_matches == []
        assert len(s.session_id) == 8

    def test_custom_values(self):
        s = ResearchState(
            research_question="量子计算",
            max_iterations=5,
            use_memory=False,
        )
        assert s.max_iterations == 5
        assert s.use_memory is False

    def test_visited_urls_as_set(self):
        s = ResearchState(research_question="test")
        s.visited_urls.add("https://example.com")
        assert "https://example.com" in s.visited_urls

    def test_search_results(self):
        s = ResearchState(research_question="test")
        s.search_results.append({"url": "https://a.com", "content": "data"})
        assert len(s.search_results) == 1
        assert s.search_results[0]["url"] == "https://a.com"


class TestSearchPlan:
    """测试搜索计划数据结构"""

    def test_plan_item_structure(self):
        """搜索计划的每一项应该有 query 和 priority"""
        plan = [
            {"query": "量子计算 金融 应用", "priority": 1},
            {"query": "Shor 算法 原理", "priority": 2},
        ]
        for item in plan:
            assert "query" in item
            assert "priority" in item

    def test_search_result_structure(self):
        """搜索结果应有 query, url, title, content, snippet"""
        result = {
            "query": "测试",
            "url": "https://example.com",
            "title": "示例",
            "content": "内容",
            "snippet": "摘要",
        }
        required = {"query", "url", "title", "content"}
        assert required.issubset(result.keys())
