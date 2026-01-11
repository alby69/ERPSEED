import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { BASE_URL } from '../utils';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      const response = await fetch(`${BASE_URL}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Password aggiornata con successo! Reindirizzamento...');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError(data.message || 'Errore nel reset della password');
      }
    } catch (err) {
      setError('Errore di connessione');
    }
  };

  if (!token) return <div className="p-5 text-center">Token mancante.</div>;

  return (
    <div className="d-flex align-items-center justify-content-center vh-100 bg-light">
      <div className="card shadow p-4" style={{ width: '400px' }}>
        <h3 className="text-center mb-4">Nuova Password</h3>
        {message && <div className="alert alert-success">{message}</div>}
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Nuova Password</label>
            <input type="password" className="form-control" value={password} onChange={(e) => setPassword(e.target.value)} required minLength="6" />
          </div>
          <button type="submit" className="btn btn-primary w-100">Salva Password</button>
        </form>
      </div>
    </div>
  );
}

export default ResetPassword;