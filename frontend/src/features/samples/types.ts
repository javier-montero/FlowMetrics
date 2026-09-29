export type SampleStatus =
  | 'pending'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'skipped';

export interface SampleSummary {
  id: number;
  sample_id: string;
  status: SampleStatus;
}

export interface SamplePage {
  items: SampleSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface SampleQuery {
  limit?: number;
  offset?: number;
  search?: string;
  status?: SampleStatus;
  signal?: AbortSignal;
}

export interface ProcessDefinition {
  id: number;
  name: string;
  expected_duration_seconds: number | null;
}

export interface SlurmJob {
  id: number;
  job_id: string;
  status: string;
  submitted_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  requested_cpus: number | null;
  requested_memory_mb: number | null;
  peak_memory_mb: number | null;
  exit_code: number | null;
  node_list: string | null;
}

export interface ProcessExecution {
  id: number;
  task_id: string;
  process: ProcessDefinition;
  status: SampleStatus;
  sample_id: string | null;
  submitted_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  queue_time_seconds: number | null;
  execution_time_seconds: number | null;
  cpu_count: number | null;
  cpu_utilization_percent: number | null;
  memory_requested_mb: number | null;
  peak_memory_mb: number | null;
  exit_code: number | null;
  attempt: number;
  slurm_jobs: SlurmJob[];
}

export interface SampleDetail extends SampleSummary {
  process_executions: ProcessExecution[];
}