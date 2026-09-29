from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Run


def list_runs(session: Session, *, limit: int = 100, offset: int = 0) -> list[Run]:
    statement = (
        select(Run)
        .options(selectinload(Run.workflow))
        .order_by(Run.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement).all())