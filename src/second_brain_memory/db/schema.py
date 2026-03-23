SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project     TEXT NOT NULL,
    directory   TEXT DEFAULT '',
    started_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    ended_at    TEXT DEFAULT NULL,
    summary     TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS memories (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    title       TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'observation',
    content     TEXT NOT NULL,
    context     TEXT DEFAULT '',
    insight     TEXT DEFAULT '',
    tags        TEXT DEFAULT '',
    project     TEXT DEFAULT '',
    vault_path  TEXT DEFAULT '',
    session_id  TEXT DEFAULT NULL REFERENCES sessions(id),
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    deleted_at  TEXT DEFAULT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    title,
    content,
    context,
    insight,
    tags,
    project,
    content='memories',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, title, content, context, insight, tags, project)
    VALUES (new.rowid, new.title, new.content, new.context, new.insight, new.tags, new.project);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, context, insight, tags, project)
    VALUES ('delete', old.rowid, old.title, old.content, old.context, old.insight, old.tags, old.project);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, context, insight, tags, project)
    VALUES ('delete', old.rowid, old.title, old.content, old.context, old.insight, old.tags, old.project);
    INSERT INTO memories_fts(rowid, title, content, context, insight, tags, project)
    VALUES (new.rowid, new.title, new.content, new.context, new.insight, new.tags, new.project);
END;

CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_deleted ON memories(deleted_at);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);
CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at);
"""

MIGRATION_V2 = """
ALTER TABLE memories ADD COLUMN project TEXT DEFAULT '';
DROP TRIGGER IF EXISTS memories_ai;
DROP TRIGGER IF EXISTS memories_ad;
DROP TRIGGER IF EXISTS memories_au;
DROP TABLE IF EXISTS memories_fts;
CREATE VIRTUAL TABLE memories_fts USING fts5(
    title, content, context, insight, tags, project,
    content='memories', content_rowid='rowid'
);
CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, title, content, context, insight, tags, project)
    VALUES (new.rowid, new.title, new.content, new.context, new.insight, new.tags, new.project);
END;
CREATE TRIGGER memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, context, insight, tags, project)
    VALUES ('delete', old.rowid, old.title, old.content, old.context, old.insight, old.tags, old.project);
END;
CREATE TRIGGER memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, title, content, context, insight, tags, project)
    VALUES ('delete', old.rowid, old.title, old.content, old.context, old.insight, old.tags, old.project);
    INSERT INTO memories_fts(rowid, title, content, context, insight, tags, project)
    VALUES (new.rowid, new.title, new.content, new.context, new.insight, new.tags, new.project);
END;
INSERT INTO memories_fts(memories_fts) VALUES('rebuild');
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);
"""

MIGRATION_V3 = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    project TEXT NOT NULL,
    directory TEXT DEFAULT '',
    started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    ended_at TEXT DEFAULT NULL,
    summary TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at);
ALTER TABLE memories ADD COLUMN session_id TEXT DEFAULT NULL REFERENCES sessions(id);
CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id);
"""
