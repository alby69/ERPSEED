import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiFetch } from '../utils';
import LanguageSelector from '../components/LanguageSelector';
import { useTranslation } from 'react-i18next';
import { useAuth, useTheme } from '../context';
import { Button } from 'antd';

function Login() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();
  const { themeConfig } = useTheme();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await apiFetch('/api/v1/auth/login', {
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      await login(data.access_token, data.refresh_token, rememberMe);
      
      if (data.force_password_change) {
        navigate('/profile?force=true');
      } else {
        navigate('/projects');
      }
    } catch (err) {
      setError(err.data?.message || err.message || 'Server connection error');
    }
  };

  return (
    <div className="container-fluid vh-100">
      <div className="row h-100">
        {/* Colonna Sinistra: Immagine/Branding */}
        <div className="col-md-6 d-none d-md-flex text-white flex-column align-items-center justify-content-center p-5"
             style={{ 
               background: `linear-gradient(135deg, ${themeConfig.primaryColor} 0%, ${themeConfig.primaryColor}dd 100%)`,
               boxShadow: 'inset -5px 0 15px rgba(0,0,0,0.1)',
               position: 'relative'
             }}>
          <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
            <LanguageSelector />
          </div>
          <div className="text-center mb-4">
            <i className="bi bi-layers-half display-1 mb-3"></i>
            <h1 className="fw-bold display-4">ERPSeed</h1>
            <p className="lead opacity-75">Manage your business with simplicity and power.</p>
          </div>
          <div className="mt-auto text-center opacity-50 small">
            &copy; {new Date().getFullYear()} ERPSeed Inc. All rights reserved.
          </div>
        </div>

        {/* Colonna Destra: Form Login */}
        <div className="col-md-6 d-flex align-items-center justify-content-center bg-white">
          <div className="w-100 p-4" style={{ maxWidth: '450px' }}>
            <div className="d-flex justify-content-end mb-3">
              <LanguageSelector />
            </div>
            <div className="text-center mb-5 d-md-none">
              <h2 className="fw-bold text-primary">ERPSeed</h2>
            </div>
            
            <h3 className="mb-4 fw-bold">Welcome!</h3>
            <p className="text-muted mb-4">Enter your credentials to access the control panel.</p>

            {error && <div className="alert alert-danger d-flex align-items-center"><i className="bi bi-exclamation-triangle-fill me-2"></i>{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div className="form-floating mb-3">
                <input type="email" className="form-control" id="floatingInput" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <label htmlFor="floatingInput">Email Address</label>
              </div>
              <div className="form-floating mb-4">
                <input type="password" className="form-control" id="floatingPassword" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <label htmlFor="floatingPassword">Password</label>
              </div>

              <div className="d-flex justify-content-between align-items-center mb-4">
                <div className="form-check">
                  <input type="checkbox" className="form-check-input" id="rememberMe" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} />
                  <label className="form-check-label small" htmlFor="rememberMe">Remember me</label>
                </div>
                <Link to="/forgot-password" style={{ textDecoration: 'none', fontSize: '0.9rem' }}>Forgot password?</Link>
              </div>

              <Button type="primary" htmlType="submit" size="large" className="w-100 py-2 fw-bold shadow-sm">Login</Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;