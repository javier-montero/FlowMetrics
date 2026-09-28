from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class SlurmJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    OUT_OF_MEMORY = "out_of_memory"


class ReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WorkflowDefinitionRead(ReadSchema):
    id: int
    name: str
    version: str


class ProcessDefinitionRead(ReadSchema):
    id: int
    name: str
    expected_duration_seconds: int | None = None


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


class SlurmJobRead(ReadSchema):
    id: int
    job_id: str
    status: SlurmJobStatus
    submitted_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    requested_cpus: int | None = Field(default=None, ge=1)
    requested_memory_mb: float | None = Field(default=None, gt=0)
    peak_memory_mb: float | None = Field(default=None, ge=0)
    exit_code: int | None = None
    node_list: str | None = None


class ProcessExecutionRead(ReadSchema):
    id: int
    task_id: str
    process: ProcessDefinitionRead
    status: ExecutionStatus
    sample_id: str | None = None
    submitted_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    queue_time_seconds: int | None = Field(default=None, ge=0)
    execution_time_seconds: int | None = Field(default=None, ge=0)
    cpu_count: int | None = Field(default=None, ge=1)
    cpu_utilization_percent: float | None = Field(default=None, ge=0)
    memory_requested_mb: float | None = Field(default=None, gt=0)
    peak_memory_mb: float | None = Field(default=None, ge=0)
    exit_code: int | None = None
    attempt: int = Field(ge=1)
    slurm_jobs: list[SlurmJobRead] = Field(default_factory=list)


class SampleSummaryRead(ReadSchema):
    id: int
    sample_id: str
    status: ExecutionStatus


class SampleRead(SampleSummaryRead):
    process_executions: list[ProcessExecutionRead] = Field(
        default_factory=list, validation_alias="executions"
    )