import { useState, useEffect } from 'react';
import { Layout } from '../components';
import { apiFetch } from '../utils';

function Users() {
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newPassword, setNewPassword] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = () => {
    apiFetch('/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(console.error);
  };

  const openResetModal = (user) => {
    setSelectedUser(user);
    setNewPassword('');
    setShowModal(true);
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!selectedUser) return;

    try {
      const res = await apiFetch(`/users/${selectedUser.id}/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: newPassword })
      });

      if (res.ok) {
        alert(`Password per ${selectedUser.email} aggiornata.`);
        setShowModal(false);
      } else {
        const data = await res.json();
        alert(data.message || "Errore durante il reset");
      }
    } catch (err) {
      console.error(err);
      alert("Errore di connessione");
    }
  };

  return (
    <Layout>
      <h2>Gestione Utenti</h2>
      <div className="card shadow-sm mt-4">
        <div className="card-body p-0">
          <table className="table table-hover mb-0">
            <thead className="table-light">
              <tr>
                <th>Email</th>
                <th>Ruolo</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td><span className="badge bg-secondary">{u.role}</span></td>
                  <td>
                    <button 
                      className="btn btn-sm btn-outline-warning"
                      onClick={() => openResetModal(u)}
                    >
                      Reset Password
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Reset Password: {selectedUser?.email}</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <form onSubmit={handleResetPassword}>
                  <div className="mb-3">
                    <label className="form-label">Nuova Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={newPassword} 
                      onChange={(e) => setNewPassword(e.target.value)} 
                      required 
                      minLength="6"
                    />
                  </div>
                  <div className="d-flex justify-content-end gap-2">
                    <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Annulla</button>
                    <button type="submit" className="btn btn-primary">Salva</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default Users;