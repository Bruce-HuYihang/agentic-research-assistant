"""会话历史管理——跨轮对话的上下文追踪"""
import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class SessionManager:
    """简单的 JSON 文件会话管理器"""

    def __init__(self, storage_dir: str = "./sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, question: str) -> str:
        """创建新会话，返回 session_id"""
        session_id = uuid.uuid4().hex[:8]
        session = {
            "session_id": session_id,
            "question": question,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "iterations": 0,
            "sources_count": 0,
            "report": None,
            "status": "created",
        }
        self._save(session_id, session)
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话记录"""
        path = self._path(session_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_session(self, session_id: str, data: dict):
        """更新会话记录"""
        session = self.get_session(session_id) or {}
        session.update(data)
        session["updated_at"] = datetime.now().isoformat()
        self._save(session_id, session)

    def list_sessions(self, limit: int = 10) -> list[dict]:
        """列出最近的会话"""
        sessions = []
        for f in sorted(
            self.storage_dir.glob("*.json"),
            key=os.path.getmtime,
            reverse=True,
        ):
            with open(f, "r", encoding="utf-8") as fh:
                sessions.append(json.load(fh))
            if len(sessions) >= limit:
                break
        return sessions

    def _path(self, session_id: str) -> Path:
        return self.storage_dir / f"{session_id}.json"

    def _save(self, session_id: str, data: dict):
        with open(self._path(session_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
