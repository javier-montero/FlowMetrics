import { apiGet } from '../../lib/api';
import type { Run, RunQuery } from './types';

export function getRuns({ limit = 100, offset = 0 }: RunQuery = {}): Promise<Run[]> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiGet<Run[]>(`/runs?${params}`);
}