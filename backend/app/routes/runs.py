from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RunPageRead
from app.services.runs import list_runs

router = APIRouter()


@router.get("/runs", response_model=RunPageRead)
def get_runs(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=100),
    sort_by: Literal[
        "run_id",
        "workflow_name",
        "status",
        "sample_count",
        "started_at",
        "progress_percent",
    ] = "started_at",
    sort_order: Literal["asc", "desc"] = "desc",
    session: Session = Depends(get_db),
) -> RunPageRead:
    items, total = list_runs(
        session,
        limit=limit,
        offset=offset,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return RunPageRead(items=items, total=total, limit=limit, offset=offset)