import { Navigate, Route, Routes } from 'react-router-dom';

import RunsView from '../features/runs/view';
import SamplesView from '../features/samples/view';
import WorkflowView from '../features/workflow/view';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RunsView />} />
      <Route path="/runs/:runId/samples" element={<SamplesView />} />
      <Route path="/runs/:runId/workflow" element={<WorkflowView />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}