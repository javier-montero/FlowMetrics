import argparse

from sqlalchemy import insert, select

from app.database import Base, SessionLocal, engine
from app.dummy_data import PROCESS_DEFINITIONS, generate_dummy_data
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

def _existing_keys(session, column, values):
    values = list(set(values))
    existing = set()
    for offset in range(0, len(values), 800):
        chunk = values[offset : offset + 800]
        existing.update(session.scalars(select(column).where(column.in_(chunk))))
    return existing


def _lookup_ids(session, key_column, id_column, values):
    values = list(set(values))
    ids = {}
    for offset in range(0, len(values), 800):
        chunk = values[offset : offset + 800]
        ids.update(
            session.execute(
                select(key_column, id_column).where(key_column.in_(chunk))
            ).all()
        )
    return ids


def _insert_missing(session, model, key_column, key_name, rows):
    if not rows:
        return 0
    existing = _existing_keys(session, key_column, [row[key_name] for row in rows])
    missing = [row for row in rows if row[key_name] not in existing]
    if missing:
        session.execute(insert(model), missing)
    return len(missing)


def seed(run_count=32, seed_value=42042):
    generated = generate_dummy_data(run_count=run_count, seed_value=seed_value)
    Base.metadata.create_all(bind=engine)
    inserted_count = 0

    with SessionLocal.begin() as session:
        workflow, inserted = _ensure_record(
            session,
            WorkflowDefinition,
            {"name": "Genome Sequencing", "version": "2.4.1"},
            {},
        )
        inserted_count += inserted

        process_ids = {}
        for process_data in generated["processes"]:
            process, inserted = _ensure_record(
                session,
                ProcessDefinition,
                {"workflow_id": workflow.id, "name": process_data["name"]},
                {
                    "expected_duration_seconds": process_data[
                        "expected_duration_seconds"
                    ],
                    "sort_order": process_data["sort_order"],
                },
            )
            process_ids[process_data["name"]] = process.id
            inserted_count += inserted

        run_rows = [
            {"workflow_id": workflow.id, **run_data}
            for run_data in generated["runs"]
        ]
        inserted_count += _insert_missing(session, Run, Run.run_id, "run_id", run_rows)
        run_ids = _lookup_ids(
            session, Run.run_id, Run.id, [row["run_id"] for row in run_rows]
        )

        sample_rows = [
            {
                "run_id": run_ids[sample_data["run_id"]],
                "sample_id": sample_data["sample_id"],
                "status": sample_data["status"],
            }
            for sample_data in generated["samples"]
        ]
        inserted_count += _insert_missing(
            session, Sample, Sample.sample_id, "sample_id", sample_rows
        )

        execution_rows = []
        for execution_data in generated["executions"]:
            execution_rows.append(
                {
                    key: value
                    for key, value in {
                        **execution_data,
                        "run_id": run_ids[execution_data["run_id"]],
                        "process_id": process_ids[execution_data["process_name"]],
                    }.items()
                    if key not in {"process_name", "slurm_job"}
                }
            )
        inserted_count += _insert_missing(
            session,
            ProcessExecution,
            ProcessExecution.task_id,
            "task_id",
            execution_rows,
        )
        execution_ids = _lookup_ids(
            session,
            ProcessExecution.task_id,
            ProcessExecution.id,
            [row["task_id"] for row in execution_rows],
        )

        slurm_rows = [
            {
                **execution_data["slurm_job"],
                "process_execution_id": execution_ids[execution_data["task_id"]],
            }
            for execution_data in generated["executions"]
            if execution_data["slurm_job"] is not None
        ]
        inserted_count += _insert_missing(
            session, SlurmJob, SlurmJob.job_id, "job_id", slurm_rows
        )

    print(f"Inserted {inserted_count} RunScope record(s).")
    return inserted_count


def main():
    parser = argparse.ArgumentParser(description="Seed FlowMetrics with dummy run data.")
    parser.add_argument("--runs", type=int, default=32, help="number of runs to seed")
    parser.add_argument("--seed", type=int, default=42042, help="random seed")
    arguments = parser.parse_args()
    seed(run_count=arguments.runs, seed_value=arguments.seed)


if __name__ == "__main__":
    main()
    seed()