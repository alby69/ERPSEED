export const BASE_URL = 'http://localhost:5000';

const getToken = (key) => localStorage.getItem(key) || sessionStorage.getItem(key);
const removeToken = (key) => {
  localStorage.removeItem(key);
  sessionStorage.removeItem(key);
};
const setToken = (key, value) => {
  if (localStorage.getItem(key)) {
    localStorage.setItem(key, value);
  } else {
    sessionStorage.setItem(key, value);
  }
};

export const apiFetch = async (endpoint, options = {}) => {
  let token = getToken('access_token');
  const headers = { ...options.headers };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  let response = await fetch(url, { ...options, headers });

  // Gestione automatica del refresh token (401 Unauthorized)
  if (response.status === 401) {
    const refreshToken = getToken('refresh_token');
    if (refreshToken) {
      try {
        const refreshRes = await fetch(`${BASE_URL}/refresh`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${refreshToken}`
          }
        });

        if (refreshRes.ok) {
          const data = await refreshRes.json();
          setToken('access_token', data.access_token);
          
          // Riprova la richiesta originale con il nuovo token
          headers['Authorization'] = `Bearer ${data.access_token}`;
          response = await fetch(url, { ...options, headers });
        } else {
          // Refresh fallito
          removeToken('access_token');
          removeToken('refresh_token');
          window.location.href = '/login';
        }
      } catch (err) {
        removeToken('access_token');
        removeToken('refresh_token');
        window.location.href = '/login';
      }
    } else {
      // Nessun refresh token disponibile
      removeToken('access_token');
      if (!window.location.pathname.includes('/login')) {
         window.location.href = '/login';
      }
    }
  }

  return response;
};