import { useEffect, useState } from 'react';
import { Button } from 'primereact/button';

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export default function App() {
  const [health, setHealth] = useState('Checking');

  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((response) => {
        if (!response.ok) throw new Error('API unavailable');
        return response.json();
      })
      .then((result) => setHealth(`API ${result.status}; database ${result.database}`))
      .catch(() => setHealth('API unavailable'));
  }, []);

  return (
    <main className="container py-5">
      <h1 className="h3">FlowMetrics</h1>
      <p className="text-secondary">{health}</p>
      <Button label="Refresh" icon="pi pi-refresh" onClick={() => location.reload()} />
    </main>
  );
}