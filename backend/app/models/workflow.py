from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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