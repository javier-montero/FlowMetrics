export type RunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
export type RunSortField =
  | 'run_id'
  | 'workflow_name'
  | 'status'
  | 'sample_count'
  | 'started_at'
  | 'progress_percent';

export interface WorkflowDefinition {
  id: number;
  name: string;
  version: string;
}

export interface Run {
  id: number;
  run_id: string;
  workflow: WorkflowDefinition;
  status: RunStatus;
  sample_count: number;
  started_at: string | null;
  completed_at: string | null;
  tat_seconds: number | null;
  expected_tat_seconds: number | null;
  tat_variance_seconds: number | null;
  sequencer: string | null;
  current_step: string | null;
  progress_percent: number;
  failed_task_count: number;
  retried_task_count: number;
}

export interface RunQuery {
  limit?: number;
  offset?: number;
  search?: string;
  sort_by?: RunSortField;
  sort_order?: 'asc' | 'desc';
  signal?: AbortSignal;
}

export interface RunPage {
  items: Run[];
  total: number;
  limit: number;
  offset: number;
}