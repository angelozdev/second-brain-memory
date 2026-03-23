import pytest

from second_brain_memory.tools.memories import (
    mem_delete,
    mem_get,
    mem_save,
    mem_search,
    mem_timeline,
    mem_update,
)


class TestMemSave:
    def test_save_basic(self, patched_server):
        result = mem_save(title="Test", content="Hello world")
        assert "Memoria guardada" in result
        assert "Test" in result

    def test_save_with_type(self, patched_server):
        result = mem_save(title="Bug", content="NPE", type="bug")
        assert "bug" in result

    def test_save_invalid_type(self, patched_server):
        with pytest.raises(ValueError):
            mem_save(title="Bad", content="x", type="wrong")

    def test_save_auto_assigns_project(self, patched_server):
        result = mem_save(title="Auto", content="test")
        assert "test-project" in result

    def test_save_override_project(self, patched_server):
        result = mem_save(title="Override", content="test", project="other")
        assert "other" in result


class TestMemGet:
    def test_get_existing(self, patched_server):
        save_result = mem_save(title="Findme", content="hello")
        mem_id = save_result.split("[")[1].split("]")[0]
        result = mem_get(id=mem_id)
        assert "Findme" in result

    def test_get_nonexistent(self, patched_server):
        result = mem_get(id="0000000000000000")
        assert "Error" in result


class TestMemSearch:
    def test_search_finds_memory(self, patched_server):
        mem_save(title="Python tips", content="Use comprehensions")
        result = mem_search(query="Python")
        assert "Python tips" in result

    def test_search_no_results(self, patched_server):
        result = mem_search(query="nonexistent_xyz")
        assert "ninguno" in result

    def test_search_scoped_to_project(self, patched_server):
        mem_save(title="Scoped note", content="hello")
        mem_save(title="Other note", content="hello", project="other")
        result = mem_search(query="hello")
        assert "Busqueda: 1" in result

    def test_search_all_projects(self, patched_server):
        mem_save(title="A", content="hello")
        mem_save(title="B", content="hello", project="other")
        result = mem_search(query="hello", all_projects=True)
        assert "Busqueda: 2" in result


class TestMemUpdate:
    def test_update_existing(self, patched_server):
        save_result = mem_save(title="Old", content="Hello")
        mem_id = save_result.split("[")[1].split("]")[0]
        result = mem_update(id=mem_id, title="New")
        assert "actualizada" in result
        assert "New" in result

    def test_update_nonexistent(self, patched_server):
        result = mem_update(id="0000000000000000", title="New")
        assert "Error" in result

    def test_update_no_fields(self, patched_server):
        result = mem_update(id="anything")
        assert "Error" in result
        assert "no se proporcionaron" in result


class TestMemDelete:
    def test_soft_delete(self, patched_server):
        save_result = mem_save(title="ToDelete", content="bye")
        mem_id = save_result.split("[")[1].split("]")[0]
        result = mem_delete(id=mem_id)
        assert "eliminada" in result
        assert "soft-delete" in result

    def test_hard_delete(self, patched_server):
        save_result = mem_save(title="Gone", content="forever")
        mem_id = save_result.split("[")[1].split("]")[0]
        result = mem_delete(id=mem_id, hard=True)
        assert "permanentemente" in result

    def test_delete_nonexistent(self, patched_server):
        result = mem_delete(id="0000000000000000")
        assert "Error" in result


class TestMemTimeline:
    def test_timeline_returns_memories(self, patched_server):
        mem_save(title="A", content="x")
        mem_save(title="B", content="y")
        result = mem_timeline()
        assert "Timeline: 2" in result

    def test_timeline_empty(self, patched_server):
        result = mem_timeline()
        assert "ninguno" in result

    def test_timeline_scoped_to_project(self, patched_server):
        mem_save(title="Mine", content="x")
        mem_save(title="Theirs", content="y", project="other")
        result = mem_timeline()
        assert "Timeline: 1" in result
