from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = (UniqueConstraint("name", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    version: Mapped[str] = mapped_column(String(50))
    processes: Mapped[list["ProcessDefinition"]] = relationship(back_populates="workflow")
    runs: Mapped[list["Run"]] = relationship(back_populates="workflow")


class ProcessDefinition(Base):
    __tablename__ = "process_definitions"
    __table_args__ = (UniqueConstraint("workflow_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow_definitions.id"))
    name: Mapped[str] = mapped_column(String(150))
    expected_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer)
    workflow: Mapped[WorkflowDefinition] = relationship(back_populates="processes")
    executions: Mapped[list["ProcessExecution"]] = relationship(back_populates="process")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflow_definitions.id"))
    status: Mapped[str] = mapped_column(String(30))
    sample_count: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tat_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_tat_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tat_variance_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sequencer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_step: Mapped[str | None] = mapped_column(String(150), nullable=True)
    progress_percent: Mapped[float] = mapped_column(Float)
    failed_task_count: Mapped[int] = mapped_column(Integer, default=0)
    retried_task_count: Mapped[int] = mapped_column(Integer, default=0)
    workflow: Mapped[WorkflowDefinition] = relationship(back_populates="runs")
    samples: Mapped[list["Sample"]] = relationship(back_populates="run")
    executions: Mapped[list["ProcessExecution"]] = relationship(back_populates="run")


class Sample(Base):
    __tablename__ = "samples"
    __table_args__ = (UniqueConstraint("run_id", "sample_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    sample_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30))
    run: Mapped[Run] = relationship(back_populates="samples")
    executions: Mapped[list["ProcessExecution"]] = relationship(back_populates="sample")


class ProcessExecution(Base):
    __tablename__ = "process_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    process_id: Mapped[int] = mapped_column(ForeignKey("process_definitions.id"))
    sample_id: Mapped[str | None] = mapped_column(
        ForeignKey("samples.sample_id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    queue_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cpu_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cpu_utilization_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_requested_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_memory_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    run: Mapped[Run] = relationship(back_populates="executions")
    process: Mapped[ProcessDefinition] = relationship(back_populates="executions")
    sample: Mapped[Sample | None] = relationship(back_populates="executions")
    slurm_jobs: Mapped[list["SlurmJob"]] = relationship(back_populates="execution")


class SlurmJob(Base):
    __tablename__ = "slurm_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    process_execution_id: Mapped[int] = mapped_column(ForeignKey("process_executions.id"))
    status: Mapped[str] = mapped_column(String(30))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requested_cpus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requested_memory_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_memory_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_list: Mapped[str | None] = mapped_column(String(255), nullable=True)
    execution: Mapped[ProcessExecution] = relationship(back_populates="slurm_jobs")