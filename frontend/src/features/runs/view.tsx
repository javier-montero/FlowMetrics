import { useEffect, useState } from 'react';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { ProgressBar } from 'primereact/progressbar';
import { Tag } from 'primereact/tag';

import { getRuns } from './services';
import type { Run, RunSortField, RunStatus } from './types';

const pageSizes = [10, 25, 50];

const statusSeverity: Record<RunStatus, 'success' | 'info' | 'warning' | 'danger' | 'secondary'> = {
  queued: 'secondary',
  running: 'info',
  completed: 'success',
  failed: 'danger',
  cancelled: 'warning',
};

function formatDate(value: string | null): string {
  if (!value) return 'Not started';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours === 0) return `${minutes}m`;
  return minutes === 0 ? `${hours}h` : `${hours}h ${minutes}m`;
}

export default function RunsView() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [total, setTotal] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(25);
  const [sortField, setSortField] = useState<RunSortField>('started_at');
  const [sortOrder, setSortOrder] = useState<1 | -1>(-1);
  const [refreshKey, setRefreshKey] = useState(0);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
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

    getRuns({
      limit: rows,
      offset: first,
      search,
      sort_by: sortField,
      sort_order: sortOrder === 1 ? 'asc' : 'desc',
      signal: controller.signal,
    })
      .then((page) => {
        setRuns(page.items);
        setTotal(page.total);
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof Error && requestError.name === 'AbortError') return;
        setError('Runs could not be loaded. Check the API connection and try again.');
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [first, rows, search, sortField, sortOrder, refreshKey]);

  function statusBody(run: Run) {
    return <Tag value={run.status} severity={statusSeverity[run.status]} className="text-capitalize" />;
  }

  function progressBody(run: Run) {
    return (
      <div className="run-progress-cell">
        <ProgressBar value={run.progress_percent} showValue={false} />
        <span>{Math.round(run.progress_percent)}%</span>
      </div>
    );
  }

  return (
    <main className="runs-page container-fluid px-3 px-lg-4 py-4 py-lg-5">
      <header className="runs-header d-flex flex-column flex-md-row align-items-md-end justify-content-between gap-3">
        <div>
          <p className="runs-eyebrow mb-2">PIPELINE MONITOR</p>
          <div className="d-flex align-items-baseline gap-3">
            <h1 className="runs-title mb-0">Runs</h1>
            <span className="runs-total">{total.toLocaleString()} total</span>
          </div>
        </div>
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
            placeholder="Search runs, workflows, steps..."
            aria-label="Search runs"
          />
          {searchInput && (
            <button
              className="btn btn-outline-secondary"
              type="button"
              aria-label="Clear search"
              onClick={() => {
                setSearchInput('');
                setFirst(0);
              }}
            >
              <i className="bi bi-x-lg" aria-hidden="true" />
            </button>
          )}
        </label>
      </header>

      {error && (
        <div className="alert alert-danger d-flex align-items-center justify-content-between mt-4" role="alert">
          <span>{error}</span>
          <button className="btn btn-sm btn-outline-danger" type="button" onClick={() => setRefreshKey((key) => key + 1)}>
            Retry
          </button>
        </div>
      )}

      <section className="runs-table-wrap mt-4" aria-label="Sequencing runs">
        <DataTable
          value={runs}
          dataKey="id"
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
          sortMode="single"
          sortField={sortField}
          sortOrder={sortOrder}
          onSort={(event) => {
            setSortField(event.sortField as RunSortField);
            setSortOrder(event.sortOrder === 1 ? 1 : -1);
            setFirst(0);
          }}
          loading={loading}
          stripedRows
          scrollable
          scrollHeight="flex"
          responsiveLayout="scroll"
          paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
          currentPageReportTemplate="{first}–{last} of {totalRecords} runs"
          emptyMessage={search ? 'No runs match this search.' : 'No runs found.'}
          className="runs-table"
        >
          <Column
            field="run_id"
            header="Run ID"
            sortable
            body={(run: Run) => <span className="run-identifier">{run.run_id}</span>}
          />
          <Column
            field="workflow_name"
            header="Workflow"
            sortable
            body={(run: Run) => (
              <div className="workflow-cell">
                <span>{run.workflow.name}</span>
                <small>v{run.workflow.version}</small>
              </div>
            )}
          />
          <Column field="status" header="Status" sortable body={statusBody} />
          <Column field="sample_count" header="Samples" sortable body={(run: Run) => run.sample_count.toLocaleString()} />
          <Column field="started_at" header="Started" sortable body={(run: Run) => formatDate(run.started_at)} />
          <Column field="current_step" header="Current step" body={(run: Run) => run.current_step ?? '—'} />
          <Column field="progress_percent" header="Progress" sortable body={progressBody} />
          <Column field="tat_seconds" header="Turnaround" body={(run: Run) => formatDuration(run.tat_seconds)} />
        </DataTable>
      </section>
    </main>
  );
}