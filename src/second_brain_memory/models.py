from dataclasses import dataclass
from typing import Optional

VALID_TYPES = frozenset({
    "observation",
    "decision",
    "bug",
    "idea",
    "learning",
    "session_summary",
    "preference",
})


@dataclass
class Memory:
    id: str
    title: str
    type: str
    content: str
    context: str = ""
    insight: str = ""
    tags: str = ""
    project: str = ""
    vault_path: str = ""
    session_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    deleted_at: Optional[str] = None


@dataclass
class Session:
    id: str
    project: str
    directory: str = ""
    started_at: str = ""
    ended_at: Optional[str] = None
    summary: Optional[str] = None
