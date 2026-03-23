import pytest


class TestSessionStart:
    def test_start_returns_session(self, db):
        s = db.session_start(project="test", id="sess-001")
        assert s.id == "sess-001"
        assert s.project == "test"
        assert s.started_at
        assert s.ended_at is None
        assert s.summary is None

    def test_start_with_directory(self, db):
        s = db.session_start(
            project="test", id="sess-002", directory="/home/user/project"
        )
        assert s.directory == "/home/user/project"

    def test_start_auto_generates_id(self, db):
        s = db.session_start(project="test")
        assert s.id
        assert len(s.id) == 16

    def test_start_auto_closes_previous(self, db):
        s1 = db.session_start(project="test", id="old-sess")
        s2 = db.session_start(project="test", id="new-sess")
        # Old session should be closed
        old = db.session_get("old-sess")
        assert old.ended_at is not None
        # New session is open
        assert s2.ended_at is None

    def test_start_doesnt_close_other_project(self, db):
        db.session_start(project="alpha", id="alpha-sess")
        db.session_start(project="beta", id="beta-sess")
        alpha = db.session_get("alpha-sess")
        assert alpha.ended_at is None  # Still open

    def test_duplicate_id_raises(self, db):
        db.session_start(project="test", id="dup")
        with pytest.raises(Exception):
            db.session_start(project="test", id="dup")


class TestSessionEnd:
    def test_end_sets_ended_at(self, db):
        db.session_start(project="test", id="sess-end")
        s = db.session_end(id="sess-end")
        assert s is not None
        assert s.ended_at is not None

    def test_end_with_summary(self, db):
        db.session_start(project="test", id="sess-sum")
        s = db.session_end(id="sess-sum", summary="Added session management")
        assert s.summary == "Added session management"

    def test_end_nonexistent_returns_none(self, db):
        assert db.session_end(id="nonexistent") is None

    def test_double_end_returns_none(self, db):
        db.session_start(project="test", id="sess-dbl")
        db.session_end(id="sess-dbl")
        assert db.session_end(id="sess-dbl") is None


class TestSessionGet:
    def test_get_existing(self, db):
        db.session_start(project="test", id="sess-get")
        s = db.session_get("sess-get")
        assert s is not None
        assert s.id == "sess-get"

    def test_get_nonexistent(self, db):
        assert db.session_get("nonexistent") is None


class TestContext:
    def test_context_returns_sessions_with_memories(self, db):
        db.session_start(project="test", id="ctx-1")
        db.save(title="Mem A", content="x", project="test", session_id="ctx-1")
        db.save(title="Mem B", content="y", project="test", session_id="ctx-1")
        db.session_end(id="ctx-1", summary="First session")
        result = db.context(project="test")
        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["session"].id == "ctx-1"
        assert len(result["sessions"][0]["memories"]) == 2

    def test_context_order_most_recent_first(self, db):
        db.session_start(project="test", id="old")
        db.session_end(id="old")
        db.session_start(project="test", id="new")
        result = db.context(project="test")
        assert result["sessions"][0]["session"].id == "new"

    def test_context_filters_by_project(self, db):
        db.session_start(project="alpha", id="s-a")
        db.session_start(project="beta", id="s-b")
        result = db.context(project="alpha")
        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["session"].project == "alpha"

    def test_context_respects_limit(self, db):
        for i in range(5):
            db.session_start(project="test", id=f"s-{i}")
            db.session_end(id=f"s-{i}")
        result = db.context(project="test", limit=3)
        assert len(result["sessions"]) == 3

    def test_context_empty(self, db):
        result = db.context(project="test")
        assert result["sessions"] == []
        assert result["orphan_memories"] == []

    def test_context_excludes_deleted_memories(self, db):
        db.session_start(project="test", id="ctx-del")
        m = db.save(title="Deleted", content="x", project="test", session_id="ctx-del")
        db.save(title="Active", content="y", project="test", session_id="ctx-del")
        db.delete(m.id)
        result = db.context(project="test")
        assert len(result["sessions"][0]["memories"]) == 1

    def test_context_includes_orphan_memories(self, db):
        db.save(title="Orphan", content="no session", project="test")
        result = db.context(project="test")
        assert len(result["orphan_memories"]) == 1
        assert result["orphan_memories"][0].title == "Orphan"

    def test_context_orphans_filtered_by_project(self, db):
        db.save(title="Mine", content="x", project="alpha")
        db.save(title="Theirs", content="y", project="beta")
        result = db.context(project="alpha")
        assert len(result["orphan_memories"]) == 1
        assert result["orphan_memories"][0].title == "Mine"
