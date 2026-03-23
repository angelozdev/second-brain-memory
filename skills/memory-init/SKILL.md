---
name: memory-init
description: Initialize a memory session and load context from previous sessions. Use at the start of any conversation where the memory MCP server is available. Calls mem_session_start and mem_context automatically.
---

# Memory Init

Initialize the memory system for this conversation.

## Steps

1. Call `mem_session_start` to register a new session (ID is auto-generated, project is auto-detected from `SBM_PROJECT`)
2. Call `mem_context` to load recent sessions and their associated memories
3. Present the loaded context to the user as a brief summary

## When to use

- At the start of a new conversation in a project with `second-brain-memory` configured
- After `/clear` to re-establish session context
- When the user says "load context", "start session", or similar

## When NOT to use

- If `mem_session_start` or `mem_context` tools are not available (MCP server not configured)
- If a session was already started in this conversation

## Output

After running both tools, summarize:
- Session ID created
- Number of previous sessions found
- Key memories from recent sessions (if any)
- Orphan memories (if any)

Keep the summary brief — 3-5 lines max.
