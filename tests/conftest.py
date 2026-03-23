from unittest.mock import patch

import pytest

from second_brain_memory.db import MemoryDB


@pytest.fixture
def db():
    mem_db = MemoryDB(db_path=":memory:")
    yield mem_db
    mem_db.close()


@pytest.fixture
def patched_server(db):
    with (
        patch("second_brain_memory.server.get_db", return_value=db),
        patch("second_brain_memory.server.CURRENT_PROJECT", "test-project"),
    ):
        yield db
