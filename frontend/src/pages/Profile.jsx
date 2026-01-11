import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components';
import { apiFetch } from '../utils';
import { useAuth } from '../context';

function Profile() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [passwords, setPasswords] = useState({ current: '', new: '' });
  const [message, setMessage] = useState({ type: '', text: '' });
  const navigate = useNavigate();
  const isForced = searchParams.get('force') === 'true';

  const handleChange = (e) => {
    setPasswords({ ...passwords, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const res = await apiFetch('/me/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          current_password: passwords.current, 
          new_password: passwords.new 
        })
      });

      const data = await res.json();

      if (res.ok) {
        setMessage({ type: 'success', text: 'Password aggiornata con successo!' });
        setPasswords({ current: '', new: '' });
        if (isForced) {
            setTimeout(() => navigate('/dashboard'), 1500);
        }
      } else {
        setMessage({ type: 'danger', text: data.message || 'Errore durante l\'aggiornamento' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Errore di connessione' });
    }
  };

  return (
    <Layout>
      <h2>Profilo Utente</h2>
      <p className="text-muted">Email: {user?.email}</p>
      <hr />

      <div className="card shadow-sm" style={{ maxWidth: '500px' }}>
        <div className="card-body">
          <h5 className="card-title mb-3">Cambia Password</h5>
          {isForced && (
            <div className="alert alert-warning">
              <strong>Attenzione:</strong> È necessario cambiare la password al primo accesso o dopo un reset.
            </div>
          )}

          {message.text && <div className={`alert alert-${message.type}`}>{message.text}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Password Attuale</label>
              <input 
                type="password" 
                className="form-control" 
                name="current" 
                value={passwords.current} 
                onChange={handleChange} 
                required 
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Nuova Password</label>
              <input 
                type="password" 
                className="form-control" 
                name="new" 
                value={passwords.new} 
                onChange={handleChange} 
                required 
                minLength="6"
              />
            </div>
            <button type="submit" className="btn btn-primary">Aggiorna Password</button>
          </form>
        </div>
      </div>
    </Layout>
  );
}

export default Profile;