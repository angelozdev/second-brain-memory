class TestMigrations:
    def test_fresh_db_has_session_id_column(self, db):
        cur = db.conn.execute("PRAGMA table_info(memories)")
        columns = [row[1] for row in cur.fetchall()]
        assert "session_id" in columns

    def test_fresh_db_has_sessions_table(self, db):
        cur = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        )
        assert cur.fetchone() is not None

    def test_fresh_db_has_project_column(self, db):
        cur = db.conn.execute("PRAGMA table_info(memories)")
        columns = [row[1] for row in cur.fetchall()]
        assert "project" in columns

    def test_wal_mode_is_set(self, db):
        # In :memory: DBs, journal_mode is always "memory"
        # This test verifies the pragma doesn't error out
        cur = db.conn.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0]
        assert mode in ("wal", "memory")

    def test_foreign_keys_enabled(self, db):
        cur = db.conn.execute("PRAGMA foreign_keys")
        assert cur.fetchone()[0] == 1

    def test_sessions_table_created_before_memories(self, db):
        cur = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY rowid"
        )
        tables = [row[0] for row in cur.fetchall()]
        sessions_idx = tables.index("sessions")
        memories_idx = tables.index("memories")
        assert sessions_idx < memories_idx

    def test_session_id_fk_enforced(self, db):
        import sqlite3

        import pytest

        with pytest.raises(sqlite3.IntegrityError):
            db.save(title="Bad FK", content="x", session_id="nonexistent")
