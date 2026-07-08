"""应用配置——自动从 .env 文件和环境变量读取（Phase 6: 全配置化）"""
from pydantic_settings import BaseSettings
from typing import Optional
from langchain_openai import ChatOpenAI


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

    # ---- 搜索 ----
    SEARCH_PROVIDER: str = "baidu"     # baidu / bing
    SEARCH_FRESHNESS: str = "month"

    # ---- 向量库 ----
    VECTOR_STORE_PATH: str = "./knowledge_store"
    EMBEDDING_MODEL: str = "bge-m3"

    # ---- Agent ----
    MAX_SEARCH_ITERATIONS: int = 3
    MAX_TOKENS_PER_SOURCE: int = 8000

    # ---- API ----
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8090
    API_RATE_LIMIT: str = "10/minute"  # slowapi 格式

    # ---- 日志 ----
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/research.log"

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
        raise ValueError(f"Unknown LLM provider: {self.LLM_PROVIDER}")


settings = Settings()
