import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Tag } from 'primereact/tag';

import { getSample, getSamples } from './services';
import type { ProcessExecution, SampleDetail, SampleStatus, SampleSummary } from './types';

const pageSizes = [25, 50, 100, 500];
const sampleStatuses: SampleStatus[] = ['queued', 'running', 'completed', 'failed', 'cancelled', 'skipped'];
const statusSeverity: Record<SampleStatus, 'success' | 'info' | 'warning' | 'danger' | 'secondary'> = {
  pending: 'secondary',
  queued: 'secondary',
  running: 'info',
  completed: 'success',
  failed: 'danger',
  cancelled: 'warning',
  skipped: 'warning',
};

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainder = seconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m ${remainder}s`;
  return `${remainder}s`;
}

function statusTag(status: SampleStatus) {
  return <Tag value={status} severity={statusSeverity[status]} className="text-capitalize" />;
}

function executionRows(executions: ProcessExecution[]) {
  if (executions.length === 0) {
    return <p className="sample-detail-empty mb-0">No process executions recorded for this sample.</p>;
  }

  return (
    <div className="sample-executions">
      <h2 className="sample-detail-heading">Process executions</h2>
      <div className="table-responsive">
        <table className="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th scope="col">Process</th>
              <th scope="col">Status</th>
              <th scope="col">Attempt</th>
              <th scope="col">Queue</th>
              <th scope="col">Execution</th>
              <th scope="col">Resources</th>
              <th scope="col">SLURM job</th>
            </tr>
          </thead>
          <tbody>
            {executions.map((execution) => (
              <tr key={execution.id}>
                <td className="fw-semibold">{execution.process.name}</td>
                <td>{statusTag(execution.status)}</td>
                <td>{execution.attempt}</td>
                <td>{formatDuration(execution.queue_time_seconds)}</td>
                <td>{formatDuration(execution.execution_time_seconds)}</td>
                <td>
                  {execution.cpu_count ? `${execution.cpu_count} CPU` : '—'}
                  {execution.memory_requested_mb ? ` · ${Math.round(execution.memory_requested_mb / 1024)} GB` : ''}
                </td>
                <td>
                  {execution.slurm_jobs.length === 0 ? '—' : execution.slurm_jobs.map((job) => (
                    <span className="slurm-job" key={job.id}>
                      <span>{job.job_id}</span>
                      {job.node_list && <small>{job.node_list}</small>}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function SamplesView() {
  const { runId = '' } = useParams<{ runId: string }>();
  const [samples, setSamples] = useState<SampleSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(25);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<SampleStatus | ''>('');
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [details, setDetails] = useState<Record<string, SampleDetail>>({});
  const [detailLoading, setDetailLoading] = useState<Record<string, boolean>>({});
  const [detailErrors, setDetailErrors] = useState<Record<string, string>>({});
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timeout = window.setTimeout(() => setSearch(searchInput.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [searchInput]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    getSamples(runId, {
      limit: rows,
      offset: first,
      search,
      status: status || undefined,
      signal: controller.signal,
    })
      .then((page) => {
        setSamples(page.items);
        setTotal(page.total);
      })
      .catch(() => {
        if (controller.signal.aborted) return;
        setError('Samples could not be loaded. Check the API connection and try again.');
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [runId, first, rows, search, status, refreshKey]);

  function loadSampleDetail(sample: SampleSummary) {
    if (details[sample.sample_id] || detailLoading[sample.sample_id]) return;

    setDetailLoading((current) => ({ ...current, [sample.sample_id]: true }));
    setDetailErrors((current) => ({ ...current, [sample.sample_id]: '' }));
    getSample(runId, sample.sample_id)
      .then((detail) => setDetails((current) => ({ ...current, [sample.sample_id]: detail })))
      .catch(() => setDetailErrors((current) => ({
        ...current,
        [sample.sample_id]: 'Execution details could not be loaded.',
      })))
      .finally(() => setDetailLoading((current) => ({ ...current, [sample.sample_id]: false })));
  }

  function rowExpansion(sample: SampleSummary) {
    if (detailLoading[sample.sample_id]) {
      return <div className="sample-detail-loading" role="status">Loading execution details...</div>;
    }
    if (detailErrors[sample.sample_id]) {
      return <div className="sample-detail-error" role="alert">{detailErrors[sample.sample_id]}</div>;
    }
    return <div className="sample-detail-content">{executionRows(details[sample.sample_id]?.process_executions ?? [])}</div>;
  }

  return (
    <main className="runs-page samples-page container-fluid px-3 px-lg-4 py-4 py-lg-5">
      <header className="runs-header d-flex flex-column flex-md-row align-items-md-end justify-content-between gap-3">
        <div>
          <nav className="samples-breadcrumb mb-2" aria-label="Breadcrumb">
            <Link to="/" className="samples-back-link">
              <i className="bi bi-arrow-left" aria-hidden="true" />
              Runs
            </Link>
            <span aria-hidden="true">/</span>
            <span>{runId}</span>
          </nav>
          <div className="d-flex align-items-baseline gap-3">
            <h1 className="runs-title mb-0">Samples</h1>
            <span className="runs-total">{total.toLocaleString()} total</span>
          </div>
        </div>
        <div className="samples-filters d-flex flex-column flex-sm-row gap-2">
          <label className="run-search input-group">
            <span className="input-group-text" aria-hidden="true">
              <i className="bi bi-search" />
            </span>
            <input
              className="form-control"
              type="search"
              value={searchInput}
              onChange={(event) => {
                setSearchInput(event.target.value);
                setFirst(0);
              }}
              placeholder="Search sample IDs..."
              aria-label="Search samples"
            />
          </label>
          <label className="visually-hidden" htmlFor="sample-status">Filter samples by status</label>
          <select
            id="sample-status"
            className="form-select sample-status-filter"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as SampleStatus | '');
              setFirst(0);
            }}
          >
            <option value="">All statuses</option>
            {sampleStatuses.map((sampleStatus) => (
              <option key={sampleStatus} value={sampleStatus}>{sampleStatus}</option>
            ))}
          </select>
        </div>
      </header>

      {error && (
        <div className="alert alert-danger d-flex align-items-center justify-content-between mt-4" role="alert">
          <span>{error}</span>
          <button className="btn btn-sm btn-outline-danger" type="button" onClick={() => setRefreshKey((key) => key + 1)}>
            Retry
          </button>
        </div>
      )}

      <section className="runs-table-wrap mt-4" aria-label={`Samples for run ${runId}`}>
        <DataTable
          value={samples}
          dataKey="sample_id"
          lazy
          paginator
          first={first}
          rows={rows}
          totalRecords={total}
          rowsPerPageOptions={pageSizes}
          onPage={(event) => {
            setFirst(event.first);
            setRows(event.rows);
          }}
          expandedRows={expandedRows}
          onRowToggle={(event) => setExpandedRows(event.data as Record<string, boolean>)}
          onRowExpand={(event) => loadSampleDetail(event.data as SampleSummary)}
          rowExpansionTemplate={rowExpansion}
          loading={loading}
          stripedRows
          scrollable
          scrollHeight="flex"
          responsiveLayout="scroll"
          paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
          currentPageReportTemplate="{first}–{last} of {totalRecords} samples"
          emptyMessage={search || status ? 'No samples match these filters.' : 'No samples found for this run.'}
          className="runs-table samples-table"
        >
          <Column expander style={{ width: '3rem' }} />
          <Column
            field="sample_id"
            header="Sample ID"
            body={(sample: SampleSummary) => <span className="run-identifier">{sample.sample_id}</span>}
          />
          <Column field="status" header="Status" body={(sample: SampleSummary) => statusTag(sample.status)} />
        </DataTable>
      </section>
    </main>
  );
}