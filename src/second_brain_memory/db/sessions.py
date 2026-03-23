from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Optional

from ..models import Memory, Session


class SessionMixin:
    # Provided by ConnectionMixin via MRO in MemoryDB
    if TYPE_CHECKING:
        conn: sqlite3.Connection
        def _row_to_memory(self, row: sqlite3.Row) -> Memory: ...
        def _row_to_session(self, row: sqlite3.Row) -> Session: ...

    def session_start(
        self,
        project: str,
        id: Optional[str] = None,
        directory: str = "",
    ) -> Session:
        self.conn.execute(
            """UPDATE sessions
               SET ended_at = strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')
               WHERE project = ? AND ended_at IS NULL""",
            (project,),
        )

        if id is not None:
            cur = self.conn.execute(
                """INSERT INTO sessions (id, project, directory)
                   VALUES (?, ?, ?)
                   RETURNING *""",
                (id, project, directory),
            )
        else:
            cur = self.conn.execute(
                """INSERT INTO sessions (project, directory)
                   VALUES (?, ?)
                   RETURNING *""",
                (project, directory),
            )

        row = cur.fetchone()
        self.conn.commit()
        return self._row_to_session(row)

    def session_end(self, id: str, summary: str = "") -> Optional[Session]:
        cur = self.conn.execute(
            """UPDATE sessions
               SET ended_at = strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'),
                   summary = ?
               WHERE id = ? AND ended_at IS NULL
               RETURNING *""",
            (summary, id),
        )
        row = cur.fetchone()
        self.conn.commit()
        return self._row_to_session(row) if row else None

    def session_get(self, id: str) -> Optional[Session]:
        cur = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (id,))
        row = cur.fetchone()
        return self._row_to_session(row) if row else None

    def context(
        self,
        project: str = "",
        limit: int = 5,
        memories_per_session: int = 10,
    ) -> dict:
        sql = "SELECT * FROM sessions"
        params: list = []

        if project:
            sql += " WHERE project = ?"
            params.append(project)

        sql += " ORDER BY started_at DESC, rowid DESC LIMIT ?"
        params.append(limit)

        cur = self.conn.execute(sql, params)
        session_rows = cur.fetchall()

        sessions = []
        for srow in session_rows:
            session = self._row_to_session(srow)
            cur = self.conn.execute(
                """SELECT * FROM memories
                   WHERE session_id = ? AND deleted_at IS NULL
                   ORDER BY created_at DESC LIMIT ?""",
                (session.id, memories_per_session),
            )
            memories = [self._row_to_memory(r) for r in cur.fetchall()]
            sessions.append({"session": session, "memories": memories})

        orphan_sql = """SELECT * FROM memories
                        WHERE session_id IS NULL AND deleted_at IS NULL"""
        orphan_params: list = []

        if project:
            orphan_sql += " AND project = ?"
            orphan_params.append(project)

        orphan_sql += " ORDER BY created_at DESC LIMIT ?"
        orphan_params.append(memories_per_session)

        cur = self.conn.execute(orphan_sql, orphan_params)
        orphan_memories = [self._row_to_memory(r) for r in cur.fetchall()]

        return {"sessions": sessions, "orphan_memories": orphan_memories}
