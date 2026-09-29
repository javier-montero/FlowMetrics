from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ProcessExecution, Run, WorkflowDefinition
from app.schemas.execution import ExecutionStatus
from app.schemas.run_workflow import RunWorkflowRead, WorkflowStepRead


def _step_status(executions: list[ProcessExecution]) -> ExecutionStatus:
    if not executions:
        return ExecutionStatus.PENDING

    statuses = {ExecutionStatus(execution.status) for execution in executions}
    if ExecutionStatus.RUNNING in statuses:
        return ExecutionStatus.RUNNING
    if statuses.intersection({ExecutionStatus.PENDING, ExecutionStatus.QUEUED}):
        return ExecutionStatus.QUEUED
    if ExecutionStatus.FAILED in statuses:
        return ExecutionStatus.FAILED
    if ExecutionStatus.CANCELLED in statuses:
        return ExecutionStatus.CANCELLED
    if ExecutionStatus.COMPLETED in statuses:
        return ExecutionStatus.COMPLETED
    return ExecutionStatus.SKIPPED


def get_run_workflow(session: Session, run_id: str) -> RunWorkflowRead | None:
    statement = (
        select(Run)
        .where(Run.run_id == run_id)
        .options(
            selectinload(Run.workflow).selectinload(WorkflowDefinition.processes),
            selectinload(Run.executions).selectinload(ProcessExecution.process),
            selectinload(Run.executions).selectinload(ProcessExecution.slurm_jobs),
        )
    )
    run = session.scalar(statement)
    if run is None:
        return None

    executions_by_process: dict[int, list[ProcessExecution]] = defaultdict(list)
    for execution in run.executions:
        executions_by_process[execution.process_id].append(execution)

    steps = []
    for process in sorted(run.workflow.processes, key=lambda item: item.sort_order):
        executions = sorted(
            executions_by_process[process.id],
            key=lambda item: (item.task_id, item.attempt),
        )
        statuses = {ExecutionStatus(execution.status) for execution in executions}
        active = statuses.intersection(
            {ExecutionStatus.PENDING, ExecutionStatus.QUEUED, ExecutionStatus.RUNNING}
        )
        started_times = [execution.started_at for execution in executions if execution.started_at]
        completed_times = [
            execution.completed_at for execution in executions if execution.completed_at
        ]
        steps.append(
            WorkflowStepRead(
                process=process,
                status=_step_status(executions),
                execution_count=len(executions),
                completed_execution_count=sum(
                    execution.status == ExecutionStatus.COMPLETED for execution in executions
                ),
                failed_execution_count=sum(
                    execution.status == ExecutionStatus.FAILED for execution in executions
                ),
                started_at=min(started_times) if started_times else None,
                completed_at=(
                    max(completed_times)
                    if completed_times and not active
                    else None
                ),
                max_queue_time_seconds=max(
                    (execution.queue_time_seconds for execution in executions if execution.queue_time_seconds is not None),
                    default=None,
                ),
                max_execution_time_seconds=max(
                    (execution.execution_time_seconds for execution in executions if execution.execution_time_seconds is not None),
                    default=None,
                ),
                executions=executions,
            )
        )

    return RunWorkflowRead(run=run, steps=steps)