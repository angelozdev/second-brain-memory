class TestStats:
    def test_stats_empty(self, db):
        s = db.stats()
        assert s["total"] == 0
        assert s["active"] == 0
        assert s["deleted"] == 0
        assert s["by_type"] == {}

    def test_stats_with_data(self, db):
        db.save(title="A", content="x", type="bug")
        db.save(title="B", content="y", type="bug")
        db.save(title="C", content="z", type="idea")
        saved = db.save(title="D", content="w", type="observation")
        db.delete(saved.id)
        s = db.stats()
        assert s["total"] == 4
        assert s["active"] == 3
        assert s["deleted"] == 1
        assert s["by_type"]["bug"] == 2
        assert s["by_type"]["idea"] == 1

    def test_stats_filters_by_project(self, db):
        db.save(title="A", content="x", type="bug", project="webapp")
        db.save(title="B", content="y", type="idea", project="api")
        db.save(title="C", content="z", type="bug", project="webapp")
        s = db.stats(project="webapp")
        assert s["active"] == 2
        assert s["by_type"]["bug"] == 2
