from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RunRead
from app.services.runs import list_runs

router = APIRouter()


@router.get("/runs", response_model=list[RunRead])
def get_runs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_db),
) -> list[RunRead]:
    return list_runs(session, limit=limit, offset=offset)