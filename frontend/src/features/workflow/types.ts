import type { Run } from '../runs/types';

export type ExecutionStatus =
  | 'pending'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'skipped';

export interface ProcessDefinition {
  id: number;
  name: string;
  expected_duration_seconds: number | null;
}

export interface SlurmJob {
  id: number;
  job_id: string;
  status: string;
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
  status: ExecutionStatus;
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

export interface WorkflowStep {
  process: ProcessDefinition;
  status: ExecutionStatus;
  execution_count: number;
  completed_execution_count: number;
  failed_execution_count: number;
  started_at: string | null;
  completed_at: string | null;
  max_queue_time_seconds: number | null;
  max_execution_time_seconds: number | null;
  executions: ProcessExecution[];
}

export interface RunWorkflow {
  run: Run;
  steps: WorkflowStep[];
}