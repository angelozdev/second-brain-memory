import second_brain_memory.server as srv
from second_brain_memory.formatters import format_list, format_memory


@srv.mcp.tool()
def mem_save(
    title: str,
    content: str,
    type: str = "observation",
    context: str = "",
    insight: str = "",
    tags: str = "",
    project: str = "",
    vault_path: str = "",
    session_id: str = "",
) -> str:
    """Guarda una nueva memoria en la base de datos.

    El proyecto se asigna automaticamente segun el entorno.

    Args:
        title: Titulo breve de la memoria
        content: Contenido principal (que paso, que se observo, que se decidio)
        type: Tipo. Valores: observation, decision, bug, idea, learning, session_summary, preference
        context: Contexto, razon o fuente
        insight: Insight o aprendizaje clave derivado
        tags: Tags separados por coma (ej: "python,mcp")
        project: Proyecto (auto-detectado si no se proporciona)
        vault_path: Ruta relativa a nota Obsidian (opcional)
        session_id: ID de sesion a la que vincular (opcional)
    """
    db = srv.get_db()
    m = db.save(
        title=title,
        content=content,
        type=type,
        context=context,
        insight=insight,
        tags=tags,
        project=project or srv.CURRENT_PROJECT,
        vault_path=vault_path,
        session_id=session_id or None,
    )
    return f"Memoria guardada.\n\n{format_memory(m)}"


@srv.mcp.tool()
def mem_get(id: str) -> str:
    """Obtiene una memoria completa por su ID.

    Args:
        id: ID de la memoria (hex de 16 caracteres)
    """
    m = srv.get_db().get(id)
    if not m:
        return f"Error: no se encontro memoria con ID '{id}'."
    return format_memory(m)


@srv.mcp.tool()
def mem_update(
    id: str,
    title: str = "",
    content: str = "",
    type: str = "",
    context: str = "",
    insight: str = "",
    tags: str = "",
    project: str = "",
    vault_path: str = "",
) -> str:
    """Actualiza una memoria existente por su ID.

    Solo los campos proporcionados (no vacios) se actualizan.

    Args:
        id: ID de la memoria a actualizar
        title: Nuevo titulo (opcional)
        content: Nuevo contenido (opcional)
        type: Nuevo tipo (opcional)
        context: Nuevo contexto (opcional)
        insight: Nuevo insight (opcional)
        tags: Nuevos tags (opcional)
        project: Nuevo proyecto (opcional)
        vault_path: Nueva ruta vault (opcional)
    """
    kwargs = {
        k: v
        for k, v in {
            "title": title,
            "content": content,
            "type": type,
            "context": context,
            "insight": insight,
            "tags": tags,
            "project": project,
            "vault_path": vault_path,
        }.items()
        if v
    }
    if not kwargs:
        return "Error: no se proporcionaron campos para actualizar."
    m = srv.get_db().update(id, **kwargs)
    if not m:
        return f"Error: no se encontro memoria con ID '{id}'."
    return f"Memoria actualizada.\n\n{format_memory(m)}"


@srv.mcp.tool()
def mem_delete(id: str, hard: bool = False) -> str:
    """Elimina una memoria por su ID.

    Por defecto hace soft-delete (recuperable). Con hard=True elimina permanentemente.

    Args:
        id: ID de la memoria a eliminar
        hard: Si True, elimina permanentemente (default False)
    """
    deleted = srv.get_db().delete(id, hard=hard)
    if not deleted:
        return f"Error: no se encontro memoria activa con ID '{id}'."
    mode = "permanentemente" if hard else "(soft-delete)"
    return f"Memoria '{id}' eliminada {mode}."


@srv.mcp.tool()
def mem_search(
    query: str,
    type: str = "",
    tags: str = "",
    project: str = "",
    all_projects: bool = False,
    limit: int = 10,
) -> str:
    """Busca memorias por texto completo usando FTS5.

    Por defecto busca solo en el proyecto actual.

    Args:
        query: Texto de busqueda (soporta AND, OR, NOT, "frase exacta", prefijo*)
        type: Filtrar por tipo (opcional)
        tags: Filtrar por tags separados por coma (opcional)
        project: Filtrar por proyecto (auto-detectado)
        all_projects: Si True, busca en todos los proyectos
        limit: Maximo resultados (default 10)
    """
    effective_project = "" if all_projects else (project or srv.CURRENT_PROJECT)
    results = srv.get_db().search(
        query=query, type=type, tags=tags, project=effective_project, limit=limit
    )
    return format_list(results, label="Busqueda")


@srv.mcp.tool()
def mem_timeline(
    type: str = "",
    tags: str = "",
    project: str = "",
    all_projects: bool = False,
    limit: int = 20,
    offset: int = 0,
    since: str = "",
) -> str:
    """Lista memorias en orden cronologico inverso (mas recientes primero).

    Por defecto lista solo el proyecto actual.

    Args:
        type: Filtrar por tipo (opcional)
        tags: Filtrar por tags separados por coma (opcional)
        project: Filtrar por proyecto (auto-detectado)
        all_projects: Si True, muestra todos los proyectos
        limit: Maximo resultados (default 20)
        offset: Saltar N resultados para paginacion
        since: Solo memorias desde esta fecha ISO (ej: "2026-01-01")
    """
    effective_project = "" if all_projects else (project or srv.CURRENT_PROJECT)
    results = srv.get_db().timeline(
        type=type,
        tags=tags,
        project=effective_project,
        limit=limit,
        offset=offset,
        since=since,
    )
    return format_list(results, label="Timeline")
