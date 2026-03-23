# Memory Protocol

This protocol makes the memory system automatic. It consists of two parts:

1. **SessionStart hook** — automatically starts a session and loads context when you open a conversation
2. **Memory rules** — tells the agent when to save, search, and close sessions

## Setup

### Option A: Per-project (recommended)

Activate memory only in specific projects.

**Step 1.** Add the MCP server to your project's `.mcp.json` (see [README](README.md#configure-your-ai-agent))

**Step 2.** Add the SessionStart hook to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "agent",
            "prompt": "If mem_session_start and mem_context tools are available: 1) Call mem_session_start to register this session. 2) Call mem_context to load recent context. 3) Return the context summary so it is available in the conversation. If the tools are not available, do nothing and return nothing."
          }
        ]
      }
    ]
  }
}
```

**Step 3.** Add the memory rules below to your project's `CLAUDE.md`.

### Option B: Global

Activate memory in all projects where the MCP server is configured.

**Step 1.** Add the hook to `~/.claude/settings.json` (same JSON as above)

**Step 2.** Add the memory rules below to `~/.claude/CLAUDE.md`

The hook is safe in projects without the MCP server — it checks for tool availability before calling anything.

---

## Memory Rules

Copy this block into your `CLAUDE.md`:

````markdown
## Memory Protocol (second-brain-memory)

> This protocol applies only when `mem_*` tools are available.

### Save proactively (don't wait for the user to ask)

Call `mem_save` immediately after:
- Architecture or design decisions
- Bug fixes (include root cause)
- Non-obvious discoveries about the codebase
- User preferences or constraints learned
- Conventions or patterns established

**Before saving, ask yourself:** "Would an agent in a future session need to know this?" If not, don't save.

**Format:**
- `title`: verb + what — short, searchable (e.g. "Fixed N+1 query in UserList")
- `type`: `decision` | `bug` | `learning` | `preference` | `observation`
- `tags`: comma-separated keywords
- `content`: What / Why / Where / Learned

### Search proactively

- User's first message about a topic → `mem_search` with relevant keywords
- "remember", "what did we do", "how did we solve" → `mem_context` then `mem_search`
- Before working on something that might have prior context → search first

### Close session (mandatory)

Before saying "done" or ending the conversation:

1. Call `mem_save` with `type: "session_summary"`:
   - **Goal**: what we were working on
   - **Accomplished**: what got done
   - **Discoveries**: non-obvious findings
   - **Next Steps**: what remains

2. Call `mem_session_end(id, summary)` with a brief summary

### After compaction

If the context gets compacted:
1. Save a summary of what was done so far with `mem_save`
2. Call `mem_context` to recover prior context
3. Continue working
````

---

## How it works

```
Session starts
    ↓
Hook runs automatically
    ↓
mem_session_start → registers session
mem_context → loads recent sessions + memories
    ↓
Agent has full context from previous sessions
    ↓
During conversation: saves proactively, searches when needed
    ↓
Before ending: session summary + session end
    ↓
Next session picks up where this one left off
```
