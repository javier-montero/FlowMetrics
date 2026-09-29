from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.execution import ExecutionStatus, ProcessExecutionRead
from app.schemas.workflow import ReadSchema, WorkflowDefinitionRead


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunRead(ReadSchema):
    id: int
    run_id: str
    workflow: WorkflowDefinitionRead
    status: RunStatus
    sample_count: int = Field(ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tat_seconds: int | None = Field(default=None, ge=0)
    expected_tat_seconds: int | None = Field(default=None, ge=0)
    tat_variance_seconds: int | None = None
    sequencer: str | None = None
    current_step: str | None = None
    progress_percent: float = Field(ge=0, le=100)
    failed_task_count: int = Field(default=0, ge=0)
    retried_task_count: int = Field(default=0, ge=0)


class SampleSummaryRead(ReadSchema):
    id: int
    sample_id: str
    status: ExecutionStatus


class SampleRead(SampleSummaryRead):
    process_executions: list[ProcessExecutionRead] = Field(
        default_factory=list, validation_alias="executions"
    )