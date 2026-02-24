export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

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

  // Lancia errore per risposte non ok
  if (!response.ok) {
    let errorMessage = `Errore ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.error || errorMessage;
    } catch (e) {
      // Se non è JSON, usa il testo dello stato
    }
    const error = new Error(errorMessage);
    error.response = response;
    throw error;
  }

  return response;
};

// Helper for accessing nested properties (e.g. "supplier.name")
export const getNestedValue = (obj, path) => {
  if (!path || !obj) return '';
  const result = path.split('.').reduce((acc, part) => acc && acc[part], obj);
  return result !== undefined && result !== null ? result : '';
};

// Format date to locale string
export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Format currency
export const formatCurrency = (amount, currency = 'EUR') => {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency }).format(amount);
};