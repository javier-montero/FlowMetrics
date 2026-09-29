from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    run: Mapped["Run"] = relationship(back_populates="executions")
    process: Mapped["ProcessDefinition"] = relationship(back_populates="executions")
    sample: Mapped["Sample | None"] = relationship(back_populates="executions")
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