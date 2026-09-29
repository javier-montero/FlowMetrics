import type { ReactNode } from 'react';

interface RunsViewProps {
  children?: ReactNode;
}

export default function RunsView({ children }: RunsViewProps) {
  return (
    <main className="container py-4">
      <h1 className="h3">Runs</h1>
      {children}
    </main>
  );
}