import pytest


class TestSave:
    def test_save_returns_memory(self, db):
        m = db.save(title="Test", content="Hello world")
        assert m.id
        assert len(m.id) == 16
        assert m.title == "Test"
        assert m.content == "Hello world"
        assert m.type == "observation"
        assert m.created_at
        assert m.deleted_at is None

    def test_save_with_all_fields(self, db):
        m = db.save(
            title="Decision",
            content="Use SQLite",
            type="decision",
            context="Need local persistence",
            insight="SQLite is enough",
            tags="architecture,database",
            project="my-app",
            vault_path="01 - Notes/Concepts/SQLite.md",
        )
        assert m.type == "decision"
        assert m.context == "Need local persistence"
        assert m.tags == "architecture,database"
        assert m.project == "my-app"
        assert m.vault_path == "01 - Notes/Concepts/SQLite.md"

    def test_save_invalid_type_raises(self, db):
        with pytest.raises(ValueError, match="Tipo invalido"):
            db.save(title="Bad", content="x", type="invalid_type")

    def test_save_with_session_id(self, db):
        db.session_start(project="test", id="sess-1")
        m = db.save(title="In session", content="x", session_id="sess-1")
        assert m.session_id == "sess-1"

    def test_save_without_session_id(self, db):
        m = db.save(title="No session", content="x")
        assert m.session_id is None


class TestGet:
    def test_get_existing(self, db):
        saved = db.save(title="Test", content="Hello")
        found = db.get(saved.id)
        assert found is not None
        assert found.id == saved.id

    def test_get_nonexistent(self, db):
        assert db.get("nonexistent") is None

    def test_get_deleted_returns_none(self, db):
        saved = db.save(title="Test", content="Hello")
        db.delete(saved.id)
        assert db.get(saved.id) is None


class TestUpdate:
    def test_update_title(self, db):
        saved = db.save(title="Old", content="Hello")
        updated = db.update(saved.id, title="New")
        assert updated is not None
        assert updated.title == "New"
        assert updated.content == "Hello"

    def test_update_multiple_fields(self, db):
        saved = db.save(title="Test", content="Hello")
        updated = db.update(saved.id, title="Updated", tags="new,tags", type="idea")
        assert updated.title == "Updated"
        assert updated.tags == "new,tags"
        assert updated.type == "idea"

    def test_update_nonexistent_returns_none(self, db):
        assert db.update("nonexistent", title="New") is None

    def test_update_invalid_type_raises(self, db):
        saved = db.save(title="Test", content="Hello")
        with pytest.raises(ValueError, match="Tipo invalido"):
            db.update(saved.id, type="wrong")

    def test_update_changes_updated_at(self, db):
        saved = db.save(title="Test", content="Hello")
        updated = db.update(saved.id, title="Changed")
        assert updated.updated_at >= saved.updated_at


class TestDelete:
    def test_soft_delete(self, db):
        saved = db.save(title="Test", content="Hello")
        assert db.delete(saved.id) is True
        assert db.get(saved.id) is None
        cur = db.conn.execute("SELECT * FROM memories WHERE id = ?", (saved.id,))
        row = cur.fetchone()
        assert row is not None
        assert row["deleted_at"] is not None

    def test_hard_delete(self, db):
        saved = db.save(title="Test", content="Hello")
        assert db.delete(saved.id, hard=True) is True
        cur = db.conn.execute("SELECT * FROM memories WHERE id = ?", (saved.id,))
        assert cur.fetchone() is None

    def test_delete_nonexistent(self, db):
        assert db.delete("nonexistent") is False

    def test_double_soft_delete(self, db):
        saved = db.save(title="Test", content="Hello")
        assert db.delete(saved.id) is True
        assert db.delete(saved.id) is False


class TestProject:
    def test_save_with_project(self, db):
        m = db.save(title="A", content="x", project="webapp")
        assert m.project == "webapp"

    def test_timeline_filters_by_project(self, db):
        db.save(title="A", content="x", project="webapp")
        db.save(title="B", content="y", project="api")
        db.save(title="C", content="z", project="webapp")
        results = db.timeline(project="webapp")
        assert len(results) == 2
        assert all(r.project == "webapp" for r in results)

    def test_default_project_is_empty(self, db):
        m = db.save(title="No project", content="x")
        assert m.project == ""
