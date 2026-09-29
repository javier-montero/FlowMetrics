from datetime import datetime
from enum import StrEnum

from pydantic import Field

from app.schemas.workflow import ProcessDefinitionRead, ReadSchema


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