/**
 * Frontend Utilities Module
 * -------------------------
 * This module provides centralized utility functions for the React frontend,
 * including a robust API fetcher with automatic JWT token management,
 * formatting helpers, and nested object access.
 */

export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

/**
 * Retrieves a token from storage (localStorage or sessionStorage).
 */
const getToken = (key) => localStorage.getItem(key) || sessionStorage.getItem(key);

/**
 * Removes a token from both storage types.
 */
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

/**
 * Enhanced fetch wrapper for ERPSeed API calls.
 *
 * Features:
 * - Automatically injects JWT Bearer token
 * - Handles 'Content-Type' for JSON and FormData
 * - Automatic 401 token refresh logic
 * - Standardized error handling
 *
 * @param {string} endpoint - API endpoint (relative to BASE_URL or absolute)
 * @param {object} options - Fetch options
 * @returns {Promise<Response>}
 */
export const apiFetch = async (endpoint, options = {}) => {
  let token = getToken('access_token');
  const headers = { ...options.headers };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData - browser will set it with boundary
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  let response = await fetch(url, { ...options, headers });

  // Gestione automatica del refresh token (401 Unauthorized)
  if (response.status === 401) {
    const refreshToken = getToken('refresh_token');
    if (refreshToken) {
      try {
        const refreshRes = await fetch(`${BASE_URL}/api/v1/auth/refreshes`, {
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