class TestSearch:
    def test_simple_search(self, db):
        db.save(title="Python tips", content="Use list comprehensions")
        db.save(title="Go tips", content="Use goroutines")
        results = db.search("Python")
        assert len(results) == 1
        assert results[0].title == "Python tips"

    def test_search_across_fields(self, db):
        db.save(title="Memory", content="test", context="Python project")
        results = db.search("Python")
        assert len(results) == 1

    def test_search_with_type_filter(self, db):
        db.save(title="Bug found", content="null pointer", type="bug")
        db.save(title="Bug idea", content="null check pattern", type="idea")
        results = db.search("null", type="bug")
        assert len(results) == 1
        assert results[0].type == "bug"

    def test_search_with_tags_filter(self, db):
        db.save(title="A", content="hello", tags="python,web")
        db.save(title="B", content="hello", tags="go,web")
        results = db.search("hello", tags="python")
        assert len(results) == 1
        assert results[0].title == "A"

    def test_search_excludes_deleted(self, db):
        saved = db.save(title="Secret", content="hidden data")
        db.delete(saved.id)
        results = db.search("Secret")
        assert len(results) == 0

    def test_search_with_limit(self, db):
        for i in range(5):
            db.save(title=f"Note {i}", content="common keyword")
        results = db.search("common", limit=3)
        assert len(results) == 3

    def test_search_phrase(self, db):
        db.save(title="A", content="full text search is great")
        db.save(title="B", content="search the full database")
        results = db.search('"full text search"')
        assert len(results) == 1
        assert results[0].title == "A"

    def test_search_no_results(self, db):
        db.save(title="A", content="hello")
        results = db.search("nonexistent_word_xyz")
        assert len(results) == 0

    def test_search_filters_by_project(self, db):
        db.save(title="React tip", content="use hooks", project="webapp")
        db.save(title="Python tip", content="use hooks wisely", project="api")
        results = db.search("hooks", project="webapp")
        assert len(results) == 1
        assert results[0].project == "webapp"

    def test_search_all_projects(self, db):
        db.save(title="React tip", content="use hooks", project="webapp")
        db.save(title="Python tip", content="use hooks wisely", project="api")
        results = db.search("hooks")
        assert len(results) == 2

    def test_search_finds_updated_content(self, db):
        m = db.save(title="Old title", content="original content")
        db.update(m.id, title="New title", content="updated content")
        assert len(db.search("original")) == 0
        assert len(db.search("updated")) == 1
        assert db.search("updated")[0].title == "New title"

    def test_search_tag_no_substring_match(self, db):
        db.save(title="A", content="hello", tags="python,web")
        db.save(title="B", content="hello", tags="py,web")
        results = db.search("hello", tags="py")
        assert len(results) == 1
        assert results[0].title == "B"


class TestTimeline:
    def test_timeline_order(self, db):
        db.conn.execute(
            "INSERT INTO memories (id, title, type, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "id1",
                "First",
                "observation",
                "a",
                "2026-01-01T00:00:00",
                "2026-01-01T00:00:00",
            ),
        )
        db.conn.execute(
            "INSERT INTO memories (id, title, type, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "id2",
                "Second",
                "observation",
                "b",
                "2026-01-02T00:00:00",
                "2026-01-02T00:00:00",
            ),
        )
        db.conn.execute(
            "INSERT INTO memories (id, title, type, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "id3",
                "Third",
                "observation",
                "c",
                "2026-01-03T00:00:00",
                "2026-01-03T00:00:00",
            ),
        )
        db.conn.commit()
        results = db.timeline()
        assert results[0].title == "Third"
        assert results[-1].title == "First"

    def test_timeline_with_type_filter(self, db):
        db.save(title="Bug", content="x", type="bug")
        db.save(title="Idea", content="y", type="idea")
        results = db.timeline(type="bug")
        assert len(results) == 1

    def test_timeline_with_tags_filter(self, db):
        db.save(title="A", content="x", tags="python,web")
        db.save(title="B", content="y", tags="go,web")
        results = db.timeline(tags="python")
        assert len(results) == 1
        assert results[0].title == "A"

    def test_timeline_tag_no_substring_match(self, db):
        db.save(title="A", content="x", tags="python,web")
        db.save(title="B", content="y", tags="py,web")
        results = db.timeline(tags="py")
        assert len(results) == 1
        assert results[0].title == "B"

    def test_timeline_with_limit_offset(self, db):
        for i in range(10):
            db.save(title=f"Note {i}", content="x")
        page1 = db.timeline(limit=3, offset=0)
        page2 = db.timeline(limit=3, offset=3)
        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0].id != page2[0].id

    def test_timeline_excludes_deleted(self, db):
        saved = db.save(title="Deleted", content="x")
        db.save(title="Active", content="y")
        db.delete(saved.id)
        results = db.timeline()
        assert len(results) == 1
        assert results[0].title == "Active"

    def test_timeline_with_since(self, db):
        db.save(title="Old", content="x")
        results = db.timeline(since="2099-01-01")
        assert len(results) == 0
