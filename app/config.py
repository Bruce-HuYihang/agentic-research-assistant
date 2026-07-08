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
        raise ValueError(f"Unknown LLM provider: {self.LLM_PROVIDER}")


settings = Settings()
