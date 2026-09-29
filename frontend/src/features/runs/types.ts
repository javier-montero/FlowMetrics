export type RunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

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
}