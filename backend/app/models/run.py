from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="runs")
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