from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Optional

from ..models import VALID_TYPES, Memory


class MemoriesMixin:
    # Provided by ConnectionMixin via MRO in MemoryDB
    if TYPE_CHECKING:
        conn: sqlite3.Connection
        def _row_to_memory(self, row: sqlite3.Row) -> Memory: ...

    def save(
        self,
        title: str,
        content: str,
        type: str = "observation",
        context: str = "",
        insight: str = "",
        tags: str = "",
        project: str = "",
        vault_path: str = "",
        session_id: Optional[str] = None,
    ) -> Memory:
        if type not in VALID_TYPES:
            raise ValueError(f"Tipo invalido: {type}. Validos: {VALID_TYPES}")
        cur = self.conn.execute(
            """INSERT INTO memories (title, type, content, context, insight, tags, project, vault_path, session_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               RETURNING *""",
            (
                title,
                type,
                content,
                context,
                insight,
                tags,
                project,
                vault_path,
                session_id,
            ),
        )
        row = cur.fetchone()
        self.conn.commit()
        return self._row_to_memory(row)

    def get(self, memory_id: str) -> Optional[Memory]:
        cur = self.conn.execute(
            "SELECT * FROM memories WHERE id = ? AND deleted_at IS NULL", (memory_id,)
        )
        row = cur.fetchone()
        return self._row_to_memory(row) if row else None

    def update(self, memory_id: str, **kwargs: str | None) -> Optional[Memory]:
        memory = self.get(memory_id)
        if not memory:
            return None

        if "type" in kwargs and kwargs["type"] not in VALID_TYPES:
            raise ValueError(f"Tipo invalido: {kwargs['type']}. Validos: {VALID_TYPES}")

        allowed = {
            "title",
            "type",
            "content",
            "context",
            "insight",
            "tags",
            "project",
            "vault_path",
            "session_id",
        }
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return memory

        # Safe: keys are filtered against hardcoded `allowed` set above
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        values.append(memory_id)

        cur = self.conn.execute(
            f"""UPDATE memories
                SET {set_clause}, updated_at = strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')
                WHERE id = ? AND deleted_at IS NULL
                RETURNING *""",
            values,
        )
        row = cur.fetchone()
        self.conn.commit()
        return self._row_to_memory(row) if row else None

    def delete(self, memory_id: str, hard: bool = False) -> bool:
        if hard:
            cur = self.conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        else:
            cur = self.conn.execute(
                """UPDATE memories
                   SET deleted_at = strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')
                   WHERE id = ? AND deleted_at IS NULL""",
                (memory_id,),
            )
        self.conn.commit()
        return cur.rowcount > 0

    def search(
        self,
        query: str,
        type: str = "",
        tags: str = "",
        project: str = "",
        limit: int = 10,
    ) -> list[Memory]:
        sql = """
            SELECT m.* FROM memories m
            JOIN memories_fts fts ON m.rowid = fts.rowid
            WHERE memories_fts MATCH ?
              AND m.deleted_at IS NULL
        """
        params: list = [query]

        if project:
            sql += " AND m.project = ?"
            params.append(project)
        if type:
            sql += " AND m.type = ?"
            params.append(type)
        if tags:
            for tag in tags.split(","):
                tag = tag.strip()
                sql += " AND (',' || m.tags || ',') LIKE ?"
                params.append(f"%,{tag},%")

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        cur = self.conn.execute(sql, params)
        return [self._row_to_memory(row) for row in cur.fetchall()]

    def timeline(
        self,
        type: str = "",
        tags: str = "",
        project: str = "",
        limit: int = 20,
        offset: int = 0,
        since: str = "",
    ) -> list[Memory]:
        sql = "SELECT * FROM memories WHERE deleted_at IS NULL"
        params: list = []

        if project:
            sql += " AND project = ?"
            params.append(project)
        if type:
            sql += " AND type = ?"
            params.append(type)
        if tags:
            for tag in tags.split(","):
                tag = tag.strip()
                sql += " AND (',' || tags || ',') LIKE ?"
                params.append(f"%,{tag},%")
        if since:
            sql += " AND created_at >= ?"
            params.append(since)

        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur = self.conn.execute(sql, params)
        return [self._row_to_memory(row) for row in cur.fetchall()]
