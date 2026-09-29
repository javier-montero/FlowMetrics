import { useEffect, useState } from 'react';

import { apiGet } from '../lib/api';

interface HealthResponse {
  status: string;
  database: string;
}

export default function App() {
  const [health, setHealth] = useState('Checking');

  useEffect(() => {
    apiGet<HealthResponse>('/health')
      .then((result) => setHealth(`API ${result.status}; database ${result.database}`))
      .catch(() => setHealth('API unavailable'));
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h3">FlowMetrics</h1>
      <p className="text-secondary">{health}</p>
      <button className="btn btn-outline-secondary" type="button" onClick={() => location.reload()}>
        <i className="bi bi-arrow-clockwise me-2" aria-hidden="true" />
        Refresh
      </button>
    </main>
  );
}