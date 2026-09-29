from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.run_workflow import RunWorkflowRead
from app.services.workflow import get_run_workflow

router = APIRouter()


@router.get("/runs/{run_id}/workflow", response_model=RunWorkflowRead)
def get_workflow(
    run_id: str,
    session: Session = Depends(get_db),
) -> RunWorkflowRead:
    workflow = get_run_workflow(session, run_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return workflow