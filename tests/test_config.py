"""单元测试：配置模块"""
import os
from app.config import settings, Settings


class TestSettings:
    """测试配置"""

    def test_default_values(self):
        assert settings.LLM_PROVIDER == "deepseek"
        assert settings.LLM_MODEL == "deepseek-v4-flash"
        assert settings.SEARCH_PROVIDER == "baidu"
        assert settings.API_PORT == 8090
        assert settings.API_RATE_LIMIT == "10/minute"
        assert settings.MAX_SEARCH_ITERATIONS == 3

    def test_llm_property(self):
        """测试 llm 属性返回正确的实例"""
        llm = settings.llm
        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)

    def test_env_override(self):
        """测试环境变量覆盖（在 .env 文件中配置）"""
        assert settings.SEARCH_FRESHNESS in ("month", "week", "day", "year")
