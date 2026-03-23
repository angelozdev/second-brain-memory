from second_brain_memory.tools.memories import mem_save
from second_brain_memory.tools.stats import mem_stats


class TestMemStats:
    def test_stats_empty(self, patched_server):
        result = mem_stats()
        assert "Total: 0" in result

    def test_stats_with_data(self, patched_server):
        mem_save(title="A", content="x", type="bug")
        mem_save(title="B", content="y", type="idea")
        result = mem_stats()
        assert "Total: 2" in result
        assert "bug: 1" in result
        assert "idea: 1" in result

    def test_stats_scoped_to_project(self, patched_server):
        mem_save(title="A", content="x", type="bug")
        mem_save(title="B", content="y", type="bug", project="other")
        result = mem_stats()
        assert "Total: 1" in result
