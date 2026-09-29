from pydantic import Field

from app.schemas.execution import ExecutionStatus, ProcessExecutionRead
from app.schemas.workflow import ReadSchema


class SampleSummaryRead(ReadSchema):
    id: int
    sample_id: str
    status: ExecutionStatus


class SamplePageRead(ReadSchema):
    items: list[SampleSummaryRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class SampleRead(SampleSummaryRead):
    process_executions: list[ProcessExecutionRead] = Field(
        default_factory=list, validation_alias="executions"
    )