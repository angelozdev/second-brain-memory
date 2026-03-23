import second_brain_memory.server as srv


@srv.mcp.tool()
def mem_stats(project: str = "", all_projects: bool = False) -> str:
    """Muestra estadisticas de la base de datos de memorias.

    Por defecto muestra stats del proyecto actual.

    Args:
        project: Filtrar por proyecto (auto-detectado)
        all_projects: Si True, muestra todos los proyectos
    """
    effective_project = "" if all_projects else (project or srv.CURRENT_PROJECT)
    s = srv.get_db().stats(project=effective_project)
    lines = [
        f"Total: {s['total']} | Activas: {s['active']} | Eliminadas: {s['deleted']}"
    ]
    if s["by_type"]:
        lines.append("Por tipo:")
        for t, count in s["by_type"].items():
            lines.append(f"  {t}: {count}")
    return "\n".join(lines)
