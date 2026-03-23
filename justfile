repo_dir := justfile_directory()
skill_src := repo_dir / "skills" / "memory-init"

# Install dependencies
install:
    uv sync

# Run tests
test:
    uv run pytest

# Run tests with verbose output
test-verbose:
    uv run pytest -v

# Install skill globally (~/.claude/skills/)
install-global: install
    mkdir -p ~/.claude/skills
    ln -sf {{ skill_src }} ~/.claude/skills/memory-init
    @echo "Skill installed globally: ~/.claude/skills/memory-init"

# Install skill in a specific project
install-project dir=".": install
    mkdir -p {{ dir }}/.claude/skills
    ln -sf {{ skill_src }} {{ dir }}/.claude/skills/memory-init
    @echo "Skill installed in {{ dir }}/.claude/skills/memory-init"

# Uninstall skill from global
uninstall-global:
    rm -f ~/.claude/skills/memory-init
    @echo "Skill removed from ~/.claude/skills/"

# Uninstall skill from a project
uninstall-project dir=".":
    rm -f {{ dir }}/.claude/skills/memory-init
    @echo "Skill removed from {{ dir }}/.claude/skills/"

# Show example .mcp.json configuration
show-config:
    @cat {{ repo_dir }}/mcp.example.json
