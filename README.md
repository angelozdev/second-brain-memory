# second-brain-memory

Persistent memory system for AI coding agents via [MCP](https://modelcontextprotocol.io/) (Model Context Protocol).

Give your AI agents a brain that persists across sessions. Built with Python, SQLite + FTS5, and FastMCP.

## Features

- **10 MCP tools** for saving, searching, updating, and deleting memories
- **Full-text search** powered by SQLite FTS5
- **Session management** to track what happened across conversations
- **Project isolation** via `SBM_PROJECT` environment variable
- **Auto-generated session IDs** and auto-close of stale sessions
- **Soft delete** with recovery support
- **Zero external dependencies** beyond the MCP SDK (SQLite is built into Python)

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [just](https://github.com/casey/just) (optional, for setup commands)

### Installation

```bash
git clone https://github.com/angelozdev/second-brain-memory.git
cd second-brain-memory
just install                    # install dependencies
just install-global             # skill available in all projects
# or
just install-project ~/my-app   # skill only in that project
```

Without `just`:
```bash
uv sync
# then manually symlink skills/memory-init to ~/.claude/skills/ or .claude/skills/
```

### Configure your AI agent

Create a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "memory": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory", "/path/to/second-brain-memory",
        "run", "second-brain-memory"
      ],
      "env": {
        "SBM_PROJECT": "my-project"
      }
    }
  }
}
```

This works with **Claude Code**, **OpenCode**, **Cursor**, and any MCP-compatible agent.

## Tools

### Memory Operations

| Tool | Description |
|------|-------------|
| `mem_save` | Save a new memory (observation, decision, bug, idea, learning, preference) |
| `mem_get` | Get a memory by ID |
| `mem_update` | Update an existing memory |
| `mem_delete` | Soft or hard delete a memory |
| `mem_search` | Full-text search across all memories (FTS5) |
| `mem_timeline` | List memories in reverse chronological order |
| `mem_stats` | Show memory statistics |

### Session Management

| Tool | Description |
|------|-------------|
| `mem_session_start` | Start a new session (auto-generates ID, auto-closes stale sessions) |
| `mem_session_end` | End a session with an optional summary |
| `mem_context` | Get recent sessions with their memories (the key tool for cross-session continuity) |

## Usage Example

```
Agent: mem_session_start()
> Session started: [a1b2c3d4]

Agent: mem_save(title="Auth refactor", content="Switched from JWT to session cookies", type="decision")
> Memory saved: [f5e6d7c8]

Agent: mem_session_end(id="a1b2c3d4", summary="Refactored auth system")
> Session ended.

--- Next conversation ---

Agent: mem_context()
> Context: 1 recent session
>
> [a1b2c3d4] Session (ended 2026-03-23T15:00:00)
>   Project: my-project | Started: 2026-03-23T14:00:00
>   Summary: Refactored auth system
>   Memories: 1
>     [f5e6d7c8] Auth refactor (decision)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SBM_PROJECT` | Project name for auto-tagging memories | `""` (no project) |
| `SBM_DB_PATH` | Custom path for the SQLite database | `~/.second-brain-memory/data/memories.db` |

### Project Isolation

Set `SBM_PROJECT` in your `.mcp.json` to isolate memories per project. Search, timeline, and stats filter by project automatically. Use `all_projects=True` on any tool to query across all projects.

## Memory Types

| Type | Use case |
|------|----------|
| `observation` | General observation about code or behavior |
| `decision` | Architecture or design decision with rationale |
| `bug` | Bug found and how it was resolved |
| `idea` | Raw idea for future exploration |
| `learning` | Something learned during a session |
| `session_summary` | End-of-session summary |
| `preference` | User preference or workflow pattern |

## Project Structure

```
src/second_brain_memory/
├── models.py            # Memory and Session dataclasses
├── db/
│   ├── connection.py    # SQLite connection, migrations
│   ├── schema.py        # SQL schema + migration scripts
│   ├── memories.py      # CRUD for memories
│   ├── sessions.py      # Session management + context
│   └── stats.py         # Statistics
├── tools/
│   ├── memories.py      # MCP tools for memories
│   ├── sessions.py      # MCP tools for sessions
│   └── stats.py         # MCP tool for stats
├── formatters.py        # Output formatting
└── server.py            # FastMCP server entry point
```

## Available Commands

```
just install                    # Install dependencies
just test                       # Run tests
just test-verbose               # Run tests with verbose output
just install-global             # Install skill globally
just install-project dir="."    # Install skill in a project
just uninstall-global           # Remove global skill
just uninstall-project dir="."  # Remove skill from project
just show-config                # Show example .mcp.json
```

## Development

```bash
just install   # install deps
just test      # run tests
```

### Database

The SQLite database is stored at `~/.second-brain-memory/data/memories.db` by default. It uses:

- **WAL mode** for better concurrent read performance
- **FTS5** virtual table for full-text search
- **Automatic migrations** (V1 -> V2 -> V3) when the schema changes

## Automatic Protocol

The memory system works best when the agent knows **when** to save, search, and close sessions automatically. See [`protocol.md`](protocol.md) for a ready-to-use protocol that includes:

- **`memory-init` skill** — starts a session and loads context with `/memory-init`
- **Memory rules** — proactive save triggers, search behavior, session close, and post-compaction recovery

Install the skill with `just install-global` or `just install-project`, then see [`protocol.md`](protocol.md) for the memory rules to add to your `CLAUDE.md`.

## Inspired by

[Engram](https://github.com/Gentleman-Programming/engram) by Gentleman Programming.

## License

[MIT](LICENSE)
