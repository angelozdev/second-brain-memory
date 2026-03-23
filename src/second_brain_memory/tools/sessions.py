import second_brain_memory.server as srv
from second_brain_memory.formatters import format_context, format_session


@srv.mcp.tool()
def mem_session_start(id: str = "", project: str = "", directory: str = "") -> str:
    """Registra el inicio de una sesion de trabajo.

    Si no se proporciona ID, se genera uno automaticamente.
    Si hay una sesion abierta del mismo proyecto, se cierra automaticamente.

    Args:
        id: ID unico de la sesion (auto-generado si vacio)
        project: Proyecto (auto-detectado si no se proporciona)
        directory: Directorio de trabajo (opcional)
    """
    s = srv.get_db().session_start(
        project=project or srv.CURRENT_PROJECT,
        id=id or None,
        directory=directory,
    )
    return f"Sesion iniciada.\n\n{format_session(s)}"


@srv.mcp.tool()
def mem_session_end(id: str, summary: str = "") -> str:
    """Marca una sesion como finalizada con un resumen opcional.

    Args:
        id: ID de la sesion a finalizar
        summary: Resumen de lo logrado en la sesion (recomendado)
    """
    s = srv.get_db().session_end(id=id, summary=summary)
    if not s:
        return f"Error: no se encontro sesion activa con ID '{id}'."
    return f"Sesion finalizada.\n\n{format_session(s)}"


@srv.mcp.tool()
def mem_context(
    project: str = "",
    all_projects: bool = False,
    limit: int = 5,
    memories_per_session: int = 10,
) -> str:
    """Obtiene contexto de sesiones recientes con sus memorias asociadas.

    Este es el tool principal para dar continuidad entre sesiones.
    Incluye las sesiones mas recientes y memorias sin sesion asignada.

    Args:
        project: Filtrar por proyecto (auto-detectado)
        all_projects: Si True, incluye todos los proyectos
        limit: Numero de sesiones recientes (default 5)
        memories_per_session: Maximo memorias por sesion (default 10)
    """
    effective_project = "" if all_projects else (project or srv.CURRENT_PROJECT)
    data = srv.get_db().context(
        project=effective_project,
        limit=limit,
        memories_per_session=memories_per_session,
    )
    return format_context(data)
