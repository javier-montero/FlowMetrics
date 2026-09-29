import { apiGet } from '../../lib/api';
import type { RunPage, RunQuery } from './types';

export function getRuns({
  limit = 25,
  offset = 0,
  search,
  sort_by = 'started_at',
  sort_order = 'desc',
  signal,
}: RunQuery = {}): Promise<RunPage> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
    sort_by,
    sort_order,
  });
  if (search) params.set('search', search);
  return apiGet<RunPage>(`/runs?${params}`, { signal });
}