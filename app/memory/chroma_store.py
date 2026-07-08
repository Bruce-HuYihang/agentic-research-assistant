"""向量存储模块（ChromaDB）——跨会话知识积累"""
import hashlib
from typing import Optional

# 嵌入模型（懒加载）
_sentence_available = False
_embedder = None

try:
    from sentence_transformers import SentenceTransformer
    _sentence_available = True
except ImportError:
    pass


def _get_embedder():
    """懒加载嵌入模型（避免 import 时下载模型导致 SSL 错误）"""
    global _embedder
    if _embedder is None and _sentence_available:
        try:
            _embedder = SentenceTransformer("BAAI/bge-m3")
        except Exception as e:
            print(f"[WARN] 嵌入模型加载失败（bge-m3 可能被墙）: {e}")
            return None
    return _embedder


# ChromaDB
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    class ChromaStore:
        """ChromaDB 向量存储封装——持久化研究知识"""

        def __init__(self, persist_dir: str = "./knowledge_store"):
            self.client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name="research_notes",
                metadata={"hnsw:space": "cosine"},
            )

        def add_document(self, url: str, title: str, content: str, metadata: dict = None) -> bool:
            """将文档存入向量库（自动去重）"""
            doc_id = _make_id(url)

            # 去重：已存在的跳过
            existing = self.collection.get(ids=[doc_id])
            if existing["ids"]:
                return False

            self.collection.add(
                documents=[content],
                metadatas=[{
                    "url": url,
                    "title": title,
                    **(metadata or {}),
                }],
                ids=[doc_id],
            )
            return True

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
        return hashlib.md5(url.encode()).hexdigest()

    HAS_CHROMA = True

except ImportError:
    HAS_CHROMA = False

    class ChromaStore:  # type: ignore
        """ChromaDB 不可用时的空桩"""
        def __init__(self, *args, **kwargs):
            print("[WARN] chromadb 未安装，向量存储不可用")

        def add_document(self, *args, **kwargs) -> bool:
            return False

        def search(self, *args, **kwargs) -> list:
            return []

        def count(self) -> int:
            return 0


# 全局单例
_default_store: Optional[ChromaStore] = None


def get_knowledge_store(persist_dir: str = "./knowledge_store") -> ChromaStore:
    """获取全局默认知识库实例"""
    global _default_store
    if _default_store is None:
        _default_store = ChromaStore(persist_dir=persist_dir)
    return _default_store
