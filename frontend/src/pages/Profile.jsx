import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components';
import { apiFetch } from '../utils';
import { useAuth } from '../context';

function Profile() {
  const { user, refreshUser } = useAuth();
  const [searchParams] = useSearchParams();
  const [passwords, setPasswords] = useState({ current: '', new: '' });
  const [profileData, setProfileData] = useState({ first_name: '', last_name: '' });
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const navigate = useNavigate();
  const isForced = searchParams.get('force') === 'true';

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || ''
      });
      if (user.avatar) {
        setAvatarPreview(`http://localhost:5000/uploads/${user.avatar}`);
      }
    }
  }, [user]);

  const handleChange = (e) => {
    setPasswords({ ...passwords, [e.target.name]: e.target.value });
  };

  const handleProfileChange = (e) => {
    setProfileData({ ...profileData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('first_name', profileData.first_name);
    formData.append('last_name', profileData.last_name);
    if (avatarFile) {
      formData.append('avatar', avatarFile);
    }

    try {
      const res = await apiFetch('/api/v1/auth/me', { method: 'PUT', body: formData });
      if (res.ok) {
        setMessage({ type: 'success', text: 'Profile updated!' });
        if (refreshUser) refreshUser();
      } else {
        setMessage({ type: 'danger', text: 'Error updating profile' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Connection error' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const res = await apiFetch('/api/v1/auth/me/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          current_password: passwords.current, 
          new_password: passwords.new 
        })
      });

      const data = await res.json();

      if (res.ok) {
        setMessage({ type: 'success', text: 'Password updated successfully!' });
        setPasswords({ current: '', new: '' });
        if (isForced) {
            setTimeout(() => navigate('/dashboard'), 1500);
        }
      } else {
        setMessage({ type: 'danger', text: data.message || 'Error updating password' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Connection error' });
    }
  };

  return (
    <Layout>
      <h2>User Profile</h2>
      <hr />

      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h5 className="card-title mb-3">Personal Data</h5>
              <form onSubmit={handleProfileSubmit}>
                <div className="text-center mb-3">
                  <div className="position-relative d-inline-block">
                    <img 
                      src={avatarPreview || `https://ui-avatars.com/api/?name=${user?.first_name}+${user?.last_name}&background=random`} 
                      alt="Avatar" 
                      className="rounded-circle border"
                      style={{ width: '100px', height: '100px', objectFit: 'cover' }}
                    />
                    <label className="position-absolute bottom-0 end-0 btn btn-sm btn-primary rounded-circle" style={{ cursor: 'pointer' }}>
                      <i className="bi bi-camera"></i>
                      <input type="file" className="d-none" onChange={handleFileChange} accept="image/*" />
                    </label>
                  </div>
                </div>
                <div className="mb-3">
                  <label className="form-label">First Name</label>
                  <input type="text" className="form-control" name="first_name" value={profileData.first_name} onChange={handleProfileChange} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Last Name</label>
                  <input type="text" className="form-control" name="last_name" value={profileData.last_name} onChange={handleProfileChange} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input type="text" className="form-control" value={user?.email} disabled readOnly />
                </div>
                <button type="submit" className="btn btn-success">Save Profile</button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <div className="card shadow-sm h-100">
            <div className="card-body">
          <h5 className="card-title mb-3">Change Password</h5>
          {isForced && (
            <div className="alert alert-warning">
              <strong>Warning:</strong> You must change your password on first login or after a reset.
            </div>
          )}

          {message.text && <div className={`alert alert-${message.type}`}>{message.text}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Current Password</label>
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
              <label className="form-label">New Password</label>
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
            <button type="submit" className="btn btn-primary">Update Password</button>
          </form>
        </div>
      </div>
        </div>
      </div>
    </Layout>
  );
}

export default Profile;