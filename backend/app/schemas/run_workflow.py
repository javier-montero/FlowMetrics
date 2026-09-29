from datetime import datetime

from pydantic import Field

from app.schemas.execution import ExecutionStatus, ProcessExecutionRead
from app.schemas.run import RunRead
from app.schemas.workflow import ProcessDefinitionRead, ReadSchema


class WorkflowStepRead(ReadSchema):
    process: ProcessDefinitionRead
    status: ExecutionStatus
    execution_count: int = Field(ge=0)
    completed_execution_count: int = Field(ge=0)
    failed_execution_count: int = Field(ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    max_queue_time_seconds: int | None = Field(default=None, ge=0)
    max_execution_time_seconds: int | None = Field(default=None, ge=0)
    executions: list[ProcessExecutionRead]


class RunWorkflowRead(ReadSchema):
    run: RunRead
    steps: list[WorkflowStepRead]