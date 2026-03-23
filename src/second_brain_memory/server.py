import os

from mcp.server.fastmcp import FastMCP

from second_brain_memory.db import MemoryDB

mcp = FastMCP("second-brain-memory")

_db: MemoryDB | None = None


def get_db() -> MemoryDB:
    global _db
    if _db is None:
        _db = MemoryDB()
    return _db


CURRENT_PROJECT = os.environ.get("SBM_PROJECT", "")

# Import tools to register them with mcp
import second_brain_memory.tools  # noqa: F401, E402


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
