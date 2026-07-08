FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir "pydantic>=2.0" "pydantic-settings>=2.0" \
    "langgraph>=0.3.0" "langchain-core>=0.3.0" "langchain-openai>=0.3.0" \
    "baidusearch>=1.0.0" "httpx>=0.28" "beautifulsoup4>=4.12" "markdownify>=0.14" \
    "PyMuPDF>=1.25" "fastapi>=0.115" "uvicorn[standard]>=0.34" \
    "rich>=13.0" "loguru>=0.7" "slowapi>=0.1" \
    "chromadb>=0.6" "python-dotenv>=1.0"

# 复制代码
COPY app/ /app/app/
COPY .env.example /app/.env.example

# 创建必要目录
RUN mkdir -p logs sessions knowledge_store

# 端口
EXPOSE 8090

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
