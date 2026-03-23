from second_brain_memory.tools.memories import mem_save
from second_brain_memory.tools.sessions import (
    mem_context,
    mem_session_end,
    mem_session_start,
)


class TestMemSessionStart:
    def test_start_session(self, patched_server):
        result = mem_session_start()
        assert "Sesion iniciada" in result

    def test_start_with_custom_id(self, patched_server):
        result = mem_session_start(id="custom-id")
        assert "custom-id" in result

    def test_start_auto_assigns_project(self, patched_server):
        result = mem_session_start()
        assert "test-project" in result


class TestMemSessionEnd:
    def test_end_session(self, patched_server):
        start_result = mem_session_start(id="end-test")
        result = mem_session_end(id="end-test", summary="Done")
        assert "finalizada" in result
        assert "Done" in result

    def test_end_nonexistent(self, patched_server):
        result = mem_session_end(id="nonexistent")
        assert "Error" in result


class TestMemContext:
    def test_context_with_sessions(self, patched_server):
        mem_session_start(id="ctx-test")
        mem_save(title="Context mem", content="important", session_id="ctx-test")
        mem_session_end(id="ctx-test", summary="Test session")
        result = mem_context()
        assert "1 sesiones recientes" in result
        assert "Context mem" in result

    def test_context_empty(self, patched_server):
        result = mem_context()
        assert "no hay sesiones previas" in result

    def test_context_scoped_to_project(self, patched_server):
        mem_session_start(id="scoped-1")
        mem_session_start(id="scoped-2", project="other")
        result = mem_context()
        assert "1 sesiones recientes" in result

    def test_context_includes_orphans(self, patched_server):
        mem_save(title="Orphan note", content="no session")
        result = mem_context()
        assert "Memorias sin sesion" in result
        assert "Orphan note" in result
