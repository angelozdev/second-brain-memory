#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="$REPO_DIR/skills/memory-init"
PROTOCOL_SRC="$REPO_DIR/protocol.md"

# Colors
BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}$*${NC}"; }
success() { echo -e "${GREEN}$*${NC}"; }
warn()  { echo -e "${YELLOW}$*${NC}"; }
step()  { echo -e "\n${BOLD}$*${NC}"; }

echo -e "${BOLD}second-brain-memory setup${NC}"
echo -e "${DIM}Persistent memory for AI coding agents${NC}\n"

# 1. Check uv
if ! command -v uv &> /dev/null; then
    warn "uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 2. Install dependencies
step "[1/3] Installing dependencies..."
(cd "$REPO_DIR" && uv sync --quiet)
success "Dependencies installed."

# 3. Install skill
step "[2/3] Installing memory-init skill..."
echo ""
echo "  1) Global  — available in all projects (~/.claude/skills/)"
echo "  2) Project — available only in current project (.claude/skills/)"
echo "  3) Skip    — don't install the skill"
echo ""
read -rp "Choose (1/2/3): " choice

case "$choice" in
    1)
        TARGET="$HOME/.claude/skills/memory-init"
        mkdir -p "$HOME/.claude/skills"
        if [ -e "$TARGET" ]; then
            warn "Skill already exists at $TARGET — skipping."
        else
            ln -s "$SKILL_SRC" "$TARGET"
            success "Skill installed globally: $TARGET -> $SKILL_SRC"
        fi
        ;;
    2)
        if [ -z "${PROJECT_DIR:-}" ]; then
            read -rp "Project path (default: current directory): " PROJECT_DIR
            PROJECT_DIR="${PROJECT_DIR:-.}"
        fi
        PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
        TARGET="$PROJECT_DIR/.claude/skills/memory-init"
        mkdir -p "$PROJECT_DIR/.claude/skills"
        if [ -e "$TARGET" ]; then
            warn "Skill already exists at $TARGET — skipping."
        else
            ln -s "$SKILL_SRC" "$TARGET"
            success "Skill installed for project: $TARGET"
        fi
        ;;
    3)
        info "Skill installation skipped."
        ;;
    *)
        warn "Invalid choice. Skill installation skipped."
        ;;
esac

# 4. Show next steps
step "[3/3] Next steps"
echo ""
info "1. Add the MCP server to your project's .mcp.json:"
echo ""
cat <<EOF
  {
    "mcpServers": {
      "memory": {
        "type": "stdio",
        "command": "uv",
        "args": ["--directory", "$REPO_DIR", "run", "second-brain-memory"],
        "env": { "SBM_PROJECT": "my-project" }
      }
    }
  }
EOF
echo ""
info "2. Add memory rules to your CLAUDE.md (see protocol.md)"
echo ""
info "3. Restart Claude Code"
echo ""
info "4. Use /memory-init or Skill(\"memory-init\") to start a session"
echo ""
success "Setup complete."
