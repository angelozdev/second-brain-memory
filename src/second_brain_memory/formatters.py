from second_brain_memory.models import Memory, Session


def format_memory(m: Memory) -> str:
    lines = [
        f"[{m.id}] {m.title}",
        f"  Tipo: {m.type} | Creado: {m.created_at}",
    ]
    if m.project:
        lines.append(f"  Proyecto: {m.project}")
    if m.tags:
        lines.append(f"  Tags: {m.tags}")
    if m.vault_path:
        lines.append(f"  Vault: {m.vault_path}")
    if m.session_id:
        lines.append(f"  Sesion: {m.session_id}")
    lines.append(f"  Contenido: {m.content}")
    if m.context:
        lines.append(f"  Contexto: {m.context}")
    if m.insight:
        lines.append(f"  Insight: {m.insight}")
    return "\n".join(lines)


def format_memory_brief(m: Memory) -> str:
    return f"[{m.id}] {m.title} ({m.type})"


def format_list(memories: list[Memory], label: str = "Resultados") -> str:
    if not memories:
        return f"{label}: ninguno encontrado."
    parts = [f"{label}: {len(memories)}"]
    for m in memories:
        parts.append("")
        parts.append(format_memory(m))
    return "\n".join(parts)


def format_session(s: Session, memories: list[Memory] | None = None) -> str:
    status = "activa" if not s.ended_at else f"finalizada {s.ended_at}"
    lines = [
        f"[{s.id}] Sesion ({status})",
        f"  Proyecto: {s.project} | Inicio: {s.started_at}",
    ]
    if s.directory:
        lines.append(f"  Directorio: {s.directory}")
    if s.summary:
        lines.append(f"  Resumen: {s.summary}")
    if memories:
        lines.append(f"  Memorias: {len(memories)}")
        for m in memories:
            lines.append(f"    {format_memory_brief(m)}")
    return "\n".join(lines)


def format_context(context_data: dict) -> str:
    sessions = context_data.get("sessions", [])
    orphans = context_data.get("orphan_memories", [])

    if not sessions and not orphans:
        return "Contexto: no hay sesiones previas ni memorias."

    parts = []
    if sessions:
        parts.append(f"Contexto: {len(sessions)} sesiones recientes")
        for entry in sessions:
            parts.append("")
            parts.append(format_session(entry["session"], entry.get("memories", [])))

    if orphans:
        parts.append("")
        parts.append(f"Memorias sin sesion: {len(orphans)}")
        for m in orphans:
            parts.append(f"  {format_memory_brief(m)}")

    return "\n".join(parts)
