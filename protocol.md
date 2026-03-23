# Memory Protocol

This protocol makes the memory system automatic. It consists of two parts:

1. **`memory-init` skill** — starts a session and loads context with `/memory-init`
2. **Memory rules** — tells the agent when to save, search, and close sessions

## Setup

Install the skill:

```bash
just install-global             # available in all projects
# or
just install-project ~/my-app   # available only in that project
```

Then:

1. Add the MCP server to your project's `.mcp.json` (see [README](README.md#configure-your-ai-agent))
2. Copy the memory rules below into your `CLAUDE.md`
3. Restart Claude Code

## Using the skill

Start every conversation with:

```
/memory-init
```

This calls `mem_session_start` + `mem_context` and gives you a summary of previous sessions.

---

## Memory Rules

Copy this block into your `CLAUDE.md` (per-project) or `~/.claude/CLAUDE.md` (global):

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
/memory-init (or Skill("memory-init"))
    |
    v
mem_session_start --> registers session (auto-ID, auto-close stale)
mem_context       --> loads recent sessions + orphan memories
    |
    v
Agent has full context from previous sessions
    |
    v
During conversation: saves proactively, searches when needed
    |
    v
Before ending: session summary + session end
    |
    v
Next session picks up where this one left off
```
