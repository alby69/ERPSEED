import React, { useState, useEffect } from 'react';
import { Layout } from '../components';
import { apiFetch } from '../utils';

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/audit-logs?page=${page}`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h2>Audit Logs</h2>
      <div className="table-responsive bg-white rounded shadow-sm mt-3">
        <table className="table table-striped mb-0">
          <thead>
            <tr>
              <th>Data</th>
              <th>Utente</th>
              <th>Azione</th>
              <th>Modello</th>
              <th>ID Record</th>
              <th>Dettagli Modifiche</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.user ? log.user.email : 'System'}</td>
                <td><span className={`badge bg-${log.action === 'DELETE' ? 'danger' : log.action === 'CREATE' ? 'success' : 'warning'}`}>{log.action}</span></td>
                <td><code>{log.model_name}</code></td>
                <td>{log.record_id}</td>
                <td>
                  <small className="text-muted" style={{maxWidth: '400px', display: 'block', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                    {log.changes}
                  </small>
                </td>
              </tr>
            ))}
            {logs.length === 0 && <tr><td colSpan="6" className="text-center p-3">Nessun log trovato.</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="d-flex justify-content-center mt-3 gap-2">
        <button className="btn btn-outline-primary" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Precedente</button>
        <button className="btn btn-outline-primary" onClick={() => setPage(p => p + 1)}>Successivo</button>
      </div>
    </Layout>
  );
}

export default AuditLogs;