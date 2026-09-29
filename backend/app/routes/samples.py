from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.execution import ExecutionStatus
from app.schemas.sample import SamplePageRead, SampleRead
from app.services.samples import get_sample, list_samples

router = APIRouter()


@router.get("/runs/{run_id}/samples", response_model=SamplePageRead)
def get_samples(
    run_id: str,
    limit: int = Query(default=25, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=100),
    status: ExecutionStatus | None = Query(default=None),
    session: Session = Depends(get_db),
) -> SamplePageRead:
    result = list_samples(
        session,
        run_id,
        limit=limit,
        offset=offset,
        search=search,
        status=status.value if status else None,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found")

    items, total = result
    return SamplePageRead(items=items, total=total, limit=limit, offset=offset)


@router.get("/runs/{run_id}/samples/{sample_id}", response_model=SampleRead)
def get_sample_detail(
    run_id: str,
    sample_id: str,
    session: Session = Depends(get_db),
) -> SampleRead:
    sample = get_sample(session, run_id, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found in run")
    return sample