repo_dir := justfile_directory()
skill_src := repo_dir / "skills" / "memory-init" / "SKILL.md"

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
    mkdir -p ~/.claude/skills/memory-init
    ln -sf "{{ skill_src }}" ~/.claude/skills/memory-init/SKILL.md
    @echo "Skill installed globally: ~/.claude/skills/memory-init/"

# Install skill in a specific project
install-project dir=".": install
    mkdir -p "{{ dir }}/.claude/skills/memory-init"
    ln -sf "{{ skill_src }}" "{{ dir }}/.claude/skills/memory-init/SKILL.md"
    @echo "Skill installed in {{ dir }}"

# Uninstall skill from global
uninstall-global:
    rm -rf ~/.claude/skills/memory-init
    @echo "Skill removed from ~/.claude/skills/"

# Uninstall skill from a project
uninstall-project dir=".":
    rm -rf "{{ dir }}/.claude/skills/memory-init"
    @echo "Skill removed from {{ dir }}"

# Show example .mcp.json configuration
show-config:
    @cat "{{ repo_dir }}/mcp.example.json"
