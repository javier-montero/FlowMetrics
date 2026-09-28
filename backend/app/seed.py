from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import (
    ProcessDefinition,
    ProcessExecution,
    Run,
    Sample,
    SlurmJob,
    WorkflowDefinition,
)


def _ensure_record(session, model, lookup, values):
    record = session.scalar(select(model).filter_by(**lookup))
    if record is not None:
        return record, False

    record = model(**{**values, **lookup})
    session.add(record)
    session.flush()
    return record, True


def seed():
    Base.metadata.create_all(bind=engine)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    fake = Faker("en_US")
    fake.seed_instance(42042)
    inserted_count = 0

    with SessionLocal.begin() as session:
        workflow, inserted = _ensure_record(
            session,
            WorkflowDefinition,
            {"name": "Genome Sequencing", "version": "2.4.1"},
            {},
        )
        inserted_count += inserted

        processes = {}
        for name, expected_seconds, sort_order in [
            ("FASTQC", 300, 1),
            ("TRIM_READS", 900, 2),
            ("ALIGN", 2400, 3),
        ]:
            processes[name], inserted = _ensure_record(
                session,
                ProcessDefinition,
                {"workflow_id": workflow.id, "name": name},
                {
                    "expected_duration_seconds": expected_seconds,
                    "sort_order": sort_order,
                },
            )
            inserted_count += inserted

        completed_start = now - timedelta(hours=8)
        completed_end = completed_start + timedelta(hours=5)
        active_start = now - timedelta(minutes=35)
        runs = {}
        for run_id, values in [
            (
                "BG-RUN-0042",
                {
                    "status": "completed",
                    "sample_count": 2,
                    "started_at": completed_start,
                    "completed_at": completed_end,
                    "tat_seconds": 18000,
                    "expected_tat_seconds": 14400,
                    "tat_variance_seconds": 3600,
                    "sequencer": fake.random_element(
                        elements=("NovaSeq X", "NextSeq 2000", "NovaSeq 6000")
                    ),
                    "current_step": None,
                    "progress_percent": 100,
                    "failed_task_count": 0,
                    "retried_task_count": 1,
                },
            ),
            (
                "BG-RUN-0043",
                {
                    "status": "running",
                    "sample_count": 1,
                    "started_at": active_start,
                    "completed_at": None,
                    "tat_seconds": None,
                    "expected_tat_seconds": 18000,
                    "tat_variance_seconds": None,
                    "sequencer": fake.random_element(
                        elements=("NovaSeq X", "NextSeq 2000", "NovaSeq 6000")
                    ),
                    "current_step": "ALIGN",
                    "progress_percent": 62.5,
                    "failed_task_count": 0,
                    "retried_task_count": 0,
                },
            ),
        ]:
            runs[run_id], inserted = _ensure_record(
                session,
                Run,
                {"run_id": run_id},
                {"workflow_id": workflow.id, **values},
            )
            inserted_count += inserted

        samples = {}
        for run_id, sample_id, status in [
            ("BG-RUN-0042", "SAMPLE-001", "completed"),
            ("BG-RUN-0042", "SAMPLE-002", "completed"),
            ("BG-RUN-0043", "SAMPLE-003", "running"),
        ]:
            samples[sample_id], inserted = _ensure_record(
                session,
                Sample,
                {"sample_id": sample_id},
                {"run_id": runs[run_id].id, "status": status},
            )
            inserted_count += inserted

        executions = [
            {
                "task_id": "438",
                "run_id": "BG-RUN-0042",
                "process": "FASTQC",
                "sample": "SAMPLE-001",
                "status": "completed",
                "submitted_at": completed_start + timedelta(minutes=5),
                "started_at": completed_start + timedelta(minutes=5, seconds=30),
                "completed_at": completed_start + timedelta(minutes=7),
                "queue_time_seconds": 30,
                "execution_time_seconds": 90,
                "cpu_count": 2,
                "cpu_utilization_percent": 84.0,
                "memory_requested_mb": 4096,
                "peak_memory_mb": 2210,
                "exit_code": 0,
                "attempt": 1,
                "slurm_job": {
                    "job_id": "928471",
                    "status": "completed",
                    "submitted_at": completed_start + timedelta(minutes=5),
                    "started_at": completed_start + timedelta(minutes=5, seconds=30),
                    "completed_at": completed_start + timedelta(minutes=7),
                    "requested_cpus": 2,
                    "requested_memory_mb": 4096,
                    "peak_memory_mb": 2210,
                    "exit_code": 0,
                    "node_list": fake.bothify(text="compute-###"),
                },
            },
            {
                "task_id": "439",
                "run_id": "BG-RUN-0042",
                "process": "ALIGN",
                "sample": "SAMPLE-001",
                "status": "completed",
                "submitted_at": completed_start + timedelta(minutes=12),
                "started_at": completed_start + timedelta(minutes=14),
                "completed_at": completed_start + timedelta(minutes=44),
                "queue_time_seconds": 120,
                "execution_time_seconds": 1800,
                "cpu_count": 8,
                "cpu_utilization_percent": 78.5,
                "memory_requested_mb": 16384,
                "peak_memory_mb": 12540,
                "exit_code": 0,
                "attempt": 2,
                "slurm_job": {
                    "job_id": "928472",
                    "status": "completed",
                    "submitted_at": completed_start + timedelta(minutes=12),
                    "started_at": completed_start + timedelta(minutes=14),
                    "completed_at": completed_start + timedelta(minutes=44),
                    "requested_cpus": 8,
                    "requested_memory_mb": 16384,
                    "peak_memory_mb": 12540,
                    "exit_code": 0,
                    "node_list": fake.bothify(text="compute-###"),
                },
            },
            {
                "task_id": "440",
                "run_id": "BG-RUN-0042",
                "process": "FASTQC",
                "sample": "SAMPLE-002",
                "status": "completed",
                "submitted_at": completed_start + timedelta(minutes=8),
                "started_at": completed_start + timedelta(minutes=8, seconds=45),
                "completed_at": completed_start + timedelta(minutes=10),
                "queue_time_seconds": 45,
                "execution_time_seconds": 75,
                "cpu_count": 2,
                "cpu_utilization_percent": 81.0,
                "memory_requested_mb": 4096,
                "peak_memory_mb": 1980,
                "exit_code": 0,
                "attempt": 1,
                "slurm_job": {
                    "job_id": "928473",
                    "status": "completed",
                    "submitted_at": completed_start + timedelta(minutes=8),
                    "started_at": completed_start + timedelta(minutes=8, seconds=45),
                    "completed_at": completed_start + timedelta(minutes=10),
                    "requested_cpus": 2,
                    "requested_memory_mb": 4096,
                    "peak_memory_mb": 1980,
                    "exit_code": 0,
                    "node_list": fake.bothify(text="compute-###"),
                },
            },
            {
                "task_id": "512",
                "run_id": "BG-RUN-0043",
                "process": "ALIGN",
                "sample": "SAMPLE-003": formatting/linting, type checks, unit tests, dependency scanning,
                "status": "running",
                "submitted_at": now - timedelta(minutes=12),
                "started_at": now - timedelta(minutes=11),
                "completed_at": None,
                "queue_time_seconds": 60,
                "execution_time_seconds": None,
                "cpu_count": 8,
                "cpu_utilization_percent": 66.0,
                "memory_requested_mb": 16384,
                "peak_memory_mb": 8300,
                "exit_code": None,
                "attempt": 1,
                "slurm_job": {
                    "job_id": "928474",
                    "status": "running",
                    "submitted_at": now - timedelta(minutes=12),
                    "started_at": now - timedelta(minutes=11),
                    "completed_at": None,
                    "requested_cpus": 8,
                    "requested_memory_mb": 16384,
                    "peak_memory_mb": 8300,
                    "exit_code": None,
                    "node_list": fake.bothify(text="compute-###"),
                },
            },
        ]

        for execution_data in executions:
            execution_values = {
                key: value
                for key, value in execution_data.items()
                if key not in {"task_id", "run_id", "process", "sample", "slurm_job"}
            }
            execution, inserted = _ensure_record(
                session,
                ProcessExecution,
                {"task_id": execution_data["task_id"]},
                {
                    **execution_values,
                    "run_id": runs[execution_data["run_id"]].id,
                    "process_id": processes[execution_data["process"]].id,
                    "sample_id": execution_data["sample"],
                },
            )
            inserted_count += inserted
            _, inserted = _ensure_record(
                session,
                SlurmJob,
                {"job_id": execution_data["slurm_job"]["job_id"]},
                {**execution_data["slurm_job"], "process_execution_id": execution.id},
            )
            inserted_count += inserted

    print(f"Inserted {inserted_count} RunScope record(s).")
    return inserted_count


if __name__ == "__main__":
    seed()