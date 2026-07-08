"""向量存储模块（ChromaDB），Phase 3 预备骨架"""
import hashlib

# ChromaDB 是可选依赖，import 失败不影响核心功能
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
            results = self.collection.query(query_texts=[query], n_results=k)
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
    # ChromaDB 未安装，提供空桩
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
