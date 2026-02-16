import { apiFetch } from '../utils';

const api = {
    get: async (url) => apiFetch(url, { method: 'GET' }),
    post: async (url, data) => apiFetch(url, { method: 'POST', body: JSON.stringify(data) }),
    put: async (url, data) => apiFetch(url, { method: 'PUT', body: JSON.stringify(data) }),
    delete: async (url) => apiFetch(url, { method: 'DELETE' }),
};

export default api;
