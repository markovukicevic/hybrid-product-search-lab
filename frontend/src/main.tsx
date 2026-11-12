import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [status, setStatus] = React.useState('Checking backend…');
  React.useEffect(() => {
    const controller = new AbortController();
    fetch('/api/health/ready', { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error(); return response.json(); })
      .then(() => setStatus('Backend and database ready'))
      .catch(error => { if (error.name !== 'AbortError') setStatus('Backend unavailable'); });
    return () => controller.abort();
  }, []);
  return <main><p className="eyebrow">AMAZON ESCI · SEARCH LAB</p>
    <h1>Product search,<br/>measured.</h1>
    <p>Compare full-text, semantic, hybrid and reranked retrieval on judged shopping queries.</p>
    <section><h2>Project foundation</h2><p role="status">{status}</p>
      <p>Dataset ingestion and search experiments are the next development stages.</p></section>
    <p className="note">No search results or evaluation scores have been generated yet.</p>
  </main>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
