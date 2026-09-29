from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import ProcessExecution, Run, Sample


def list_samples(
    session: Session,
    run_id: str,
    *,
    limit: int = 25,
    offset: int = 0,
    search: str | None = None,
    status: str | None = None,
) -> tuple[list[Sample], int] | None:
    run_pk = session.scalar(select(Run.id).where(Run.run_id == run_id))
    if run_pk is None:
        return None

    filters = [Sample.run_id == run_pk]
    search = search.strip() if search else None
    if search:
        filters.append(Sample.sample_id.ilike(f"%{search}%"))
    if status:
        filters.append(Sample.status == status)

    total = session.scalar(select(func.count(Sample.id)).where(*filters)) or 0
    statement = (
        select(Sample)
        .where(*filters)
        .order_by(Sample.sample_id.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement).all()), total


def get_sample(session: Session, run_id: str, sample_id: str) -> Sample | None:
    statement = (
        select(Sample)
        .join(Sample.run)
        .where(Run.run_id == run_id, Sample.sample_id == sample_id)
        .options(
            selectinload(Sample.executions).selectinload(ProcessExecution.process),
            selectinload(Sample.executions).selectinload(ProcessExecution.slurm_jobs),
        )
    )
    return session.scalar(statement)