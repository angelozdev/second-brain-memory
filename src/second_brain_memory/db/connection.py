import atexit
import os
import sqlite3
from pathlib import Path
from typing import Optional

from ..models import Memory, Session
from .schema import MIGRATION_V2, MIGRATION_V3, SCHEMA

DEFAULT_DB_PATH = Path.home() / ".second-brain-memory" / "data" / "memories.db"


class ConnectionMixin:
    conn: sqlite3.Connection

    def __init__(self, db_path: Optional[str] = None):
        path = db_path or os.environ.get("SBM_DB_PATH") or str(DEFAULT_DB_PATH)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        atexit.register(self.close)

    def _init_schema(self) -> None:
        cur = self.conn.execute("PRAGMA table_info(memories)")
        columns = [row[1] for row in cur.fetchall()]

        if not columns:
            self.conn.executescript(SCHEMA)
        elif "project" not in columns:
            self.conn.executescript(MIGRATION_V2)
            self.conn.executescript(MIGRATION_V3)
        elif "session_id" not in columns:
            self.conn.executescript(MIGRATION_V3)

    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            title=row["title"],
            type=row["type"],
            content=row["content"],
            context=row["context"],
            insight=row["insight"],
            tags=row["tags"],
            project=row["project"],
            vault_path=row["vault_path"],
            session_id=row["session_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        return Session(
            id=row["id"],
            project=row["project"],
            directory=row["directory"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            summary=row["summary"],
        )

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None  # type: ignore[assignment]
