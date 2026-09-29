import { apiGet } from '../../lib/api';
import type { RunWorkflow } from './types';

export function getRunWorkflow(runId: string, signal?: AbortSignal): Promise<RunWorkflow> {
  return apiGet<RunWorkflow>(`/runs/${encodeURIComponent(runId)}/workflow`, { signal });
}