import { apiGet } from '../../lib/api';
import type { SampleDetail, SamplePage, SampleQuery } from './types';

export function getSamples(runId: string, {
  limit = 25,
  offset = 0,
  search,
  status,
  signal,
}: SampleQuery = {}): Promise<SamplePage> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (search) params.set('search', search);
  if (status) params.set('status', status);
  return apiGet<SamplePage>(`/runs/${encodeURIComponent(runId)}/samples?${params}`, { signal });
}

export function getSample(runId: string, sampleId: string, signal?: AbortSignal): Promise<SampleDetail> {
  return apiGet<SampleDetail>(
    `/runs/${encodeURIComponent(runId)}/samples/${encodeURIComponent(sampleId)}`,
    { signal },
  );
}