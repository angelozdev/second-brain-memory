import sqlite3
from typing import TYPE_CHECKING


class StatsMixin:
    # Provided by ConnectionMixin via MRO in MemoryDB
    if TYPE_CHECKING:
        conn: sqlite3.Connection

    def stats(self, project: str = "") -> dict:
        where = "WHERE 1=1"
        params: list = []
        if project:
            where += " AND project = ?"
            params.append(project)

        cur = self.conn.execute(
            f"""SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deleted
               FROM memories {where}""",
            params,
        )
        row = cur.fetchone()
        total = row["total"]
        deleted = row["deleted"]

        cur = self.conn.execute(
            f"""SELECT type, COUNT(*) as count
               FROM memories {where} AND deleted_at IS NULL
               GROUP BY type ORDER BY count DESC""",
            params,
        )
        by_type = {r["type"]: r["count"] for r in cur.fetchall()}

        return {
            "total": total,
            "active": total - deleted,
            "deleted": deleted,
            "by_type": by_type,
        }
