import { useEffect, useState } from 'react';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { ProgressBar } from 'primereact/progressbar';
import { Tag } from 'primereact/tag';
import { Link, useParams } from 'react-router-dom';

import { getRunWorkflow } from './services';
import type { ExecutionStatus, ProcessExecution, RunWorkflow, WorkflowStep } from './types';

const statusSeverity: Record<ExecutionStatus, 'success' | 'info' | 'warning' | 'danger' | 'secondary'> = {
  pending: 'secondary',
  queued: 'secondary',
  running: 'info',
  completed: 'success',
  failed: 'danger',
  cancelled: 'warning',
  skipped: 'warning',
};

function formatDate(value: string | null): string {
  if (!value) return '—';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m ${remainingSeconds}s`;
  return `${remainingSeconds}s`;
}

function statusTag(status: ExecutionStatus) {
  return <Tag value={status} severity={statusSeverity[status]} className="text-capitalize" />;
}

function resourceSummary(execution: ProcessExecution): string {
  const cpu = execution.cpu_count ? `${execution.cpu_count} CPU` : null;
  const memory = execution.memory_requested_mb
    ? `${(execution.memory_requested_mb / 1024).toFixed(1)} GB`
    : null;
  const peak = execution.peak_memory_mb
    ? `peak ${(execution.peak_memory_mb / 1024).toFixed(1)} GB`
    : null;
  return [cpu, memory, peak].filter(Boolean).join(' · ') || '—';
}

function executionDetails(step: WorkflowStep, runId: string) {
  if (step.executions.length === 0) {
    return <p className="workflow-no-executions mb-0">No task executions recorded for this process.</p>;
  }

  return (
    <div className="workflow-executions">
      <div className="workflow-executions-heading">Task executions</div>
      <DataTable
        value={step.executions}
        dataKey="id"
        paginator={step.executions.length > 10}
        rows={10}
        rowsPerPageOptions={[10, 25, 50]}
        stripedRows
        responsiveLayout="scroll"
        paginatorTemplate="RowsPerPageDropdown PrevPageLink PageLinks NextPageLink CurrentPageReport"
        currentPageReportTemplate="{first}–{last} of {totalRecords} tasks"
        className="workflow-executions-table"
      >
        <Column field="task_id" header="Task" body={(execution: ProcessExecution) => (
          <span className="workflow-task-id">{execution.task_id}</span>
        )} />
        <Column field="sample_id" header="Sample" body={(execution: ProcessExecution) => (
          execution.sample_id ? (
            <Link to={`/runs/${encodeURIComponent(runId)}/samples`} className="workflow-sample-link">
              {execution.sample_id}
            </Link>
          ) : 'Run-level'
        )} />
        <Column field="status" header="Status" body={(execution: ProcessExecution) => statusTag(execution.status)} />
        <Column field="attempt" header="Attempt" />
        <Column field="queue_time_seconds" header="Queue" body={(execution: ProcessExecution) => formatDuration(execution.queue_time_seconds)} />
        <Column field="execution_time_seconds" header="Execution" body={(execution: ProcessExecution) => formatDuration(execution.execution_time_seconds)} />
        <Column field="resources" header="Resources" body={(execution: ProcessExecution) => resourceSummary(execution)} />
        <Column field="slurm_jobs" header="SLURM job" body={(execution: ProcessExecution) => (
          execution.slurm_jobs.length > 0 ? execution.slurm_jobs.map((job) => (
            <span className="workflow-slurm-job" key={job.id}>
              {job.job_id}{job.node_list ? <small>{job.node_list}</small> : null}
            </span>
          )) : '—'
        )} />
        <Column field="exit_code" header="Exit" body={(execution: ProcessExecution) => execution.exit_code ?? '—'} />
      </DataTable>
    </div>
  );
}

export default function WorkflowView() {
  const { runId = '' } = useParams<{ runId: string }>();
  const [workflow, setWorkflow] = useState<RunWorkflow | null>(null);
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    getRunWorkflow(runId, controller.signal)
      .then((result) => setWorkflow(result))
      .catch(() => {
        if (controller.signal.aborted) return;
        setError('Workflow details could not be loaded. Check the API connection and try again.');
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [runId, refreshKey]);

  const run = workflow?.run;
  const executionCount = workflow?.steps.reduce((count, step) => count + step.execution_count, 0) ?? 0;

  return (
    <main className="runs-page workflow-page container-fluid px-3 px-lg-4 py-4 py-lg-5">
      <header className="runs-header workflow-header d-flex flex-column flex-md-row align-items-md-end justify-content-between gap-3">
        <div>
          <nav className="workflow-breadcrumb mb-2" aria-label="Breadcrumb">
            <Link to="/" className="workflow-back-link">
              <i className="bi bi-arrow-left" aria-hidden="true" />
              Runs
            </Link>
            <span aria-hidden="true">/</span>
            <span>{runId}</span>
          </nav>
          <div className="d-flex align-items-baseline gap-3">
            <h1 className="runs-title mb-0">Workflow</h1>
            {run && <span className="runs-total">{run.workflow.name} · v{run.workflow.version}</span>}
          </div>
        </div>
        {run && (
          <div className="workflow-run-summary">
            {statusTag(run.status)}
            <span><strong>{workflow?.steps.length ?? 0}</strong> processes</span>
            <span><strong>{executionCount.toLocaleString()}</strong> tasks</span>
            <div className="workflow-run-progress">
              <ProgressBar value={run.progress_percent} showValue={false} />
              <span>{Math.round(run.progress_percent)}%</span>
            </div>
          </div>
        )}
      </header>

      {error && (
        <div className="alert alert-danger d-flex align-items-center justify-content-between mt-4" role="alert">
          <span>{error}</span>
          <button className="btn btn-sm btn-outline-danger" type="button" onClick={() => setRefreshKey((key) => key + 1)}>
            Retry
          </button>
        </div>
      )}

      <section className="runs-table-wrap mt-4" aria-label={`Workflow steps for run ${runId}`}>
        <DataTable
          value={workflow?.steps ?? []}
          dataKey="process.id"
          expandedRows={expandedRows}
          onRowToggle={(event) => setExpandedRows(event.data as Record<string, boolean>)}
          rowExpansionTemplate={(step: WorkflowStep) => executionDetails(step, runId)}
          loading={loading}
          stripedRows
          scrollable
          scrollHeight="flex"
          responsiveLayout="scroll"
          emptyMessage={error ? 'Workflow unavailable.' : 'No workflow steps found.'}
          className="runs-table workflow-table"
        >
          <Column expander style={{ width: '3rem' }} />
          <Column field="process.name" header="Process" body={(step: WorkflowStep) => (
            <div className="workflow-process-cell">
              <span>{step.process.name}</span>
              {step.process.expected_duration_seconds !== null && (
                <small>Expected {formatDuration(step.process.expected_duration_seconds)}</small>
              )}
            </div>
          )} />
          <Column field="status" header="Status" body={(step: WorkflowStep) => statusTag(step.status)} />
          <Column field="execution_count" header="Tasks" />
          <Column field="completed_execution_count" header="Completed" />
          <Column field="failed_execution_count" header="Failed" />
          <Column field="started_at" header="Started" body={(step: WorkflowStep) => formatDate(step.started_at)} />
          <Column field="completed_at" header="Completed" body={(step: WorkflowStep) => formatDate(step.completed_at)} />
          <Column field="max_queue_time_seconds" header="Max queue" body={(step: WorkflowStep) => formatDuration(step.max_queue_time_seconds)} />
          <Column field="max_execution_time_seconds" header="Max execution" body={(step: WorkflowStep) => formatDuration(step.max_execution_time_seconds)} />
        </DataTable>
      </section>
    </main>
  );
}