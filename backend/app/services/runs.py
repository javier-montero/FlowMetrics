from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Run, WorkflowDefinition


RunSortField = Literal[
    "run_id",
    "workflow_name",
    "status",
    "sample_count",
    "started_at",
    "progress_percent",
]


def list_runs(
    session: Session,
    *,
    limit: int = 25,
    offset: int = 0,
    search: str | None = None,
    sort_by: RunSortField = "started_at",
    sort_order: Literal["asc", "desc"] = "desc",
) -> tuple[list[Run], int]:
    filters = []
    search = search.strip() if search else None
    if search:
        pattern = f"%{search}%"
        filters.append(
            or_(
                Run.run_id.ilike(pattern),
                Run.status.ilike(pattern),
                Run.current_step.ilike(pattern),
                Run.sequencer.ilike(pattern),
                Run.workflow.has(WorkflowDefinition.name.ilike(pattern)),
            )
        )

    total = session.scalar(select(func.count(Run.id)).where(*filters)) or 0
    sort_columns = {
        "run_id": Run.run_id,
        "workflow_name": WorkflowDefinition.name,
        "status": Run.status,
        "sample_count": Run.sample_count,
        "started_at": Run.started_at,
        "progress_percent": Run.progress_percent,
    }
    sort_column = sort_columns[sort_by]
    statement = select(Run).options(selectinload(Run.workflow)).where(*filters)
    if sort_by == "workflow_name":
        statement = statement.join(Run.workflow)

    ordering = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    statement = statement.order_by(ordering.nullslast(), Run.id.desc())
    statement = statement.limit(limit).offset(offset)
    return list(session.scalars(statement).all()), total