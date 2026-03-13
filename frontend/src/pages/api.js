import { apiFetch } from '../utils';

// A simplified client object for common CRUD operations
export const apiClient = {
    get: async (endpoint, options) => apiFetch(endpoint, { ...options, method: 'GET' }).then(res => res.json()),
    post: async (endpoint, data, options) => apiFetch(endpoint, { ...options, method: 'POST', body: data }).then(res => res.json()),
    put: async (endpoint, data, options) => apiFetch(endpoint, { ...options, method: 'PUT', body: data }).then(res => res.json()),
    delete: async (endpoint, options) => apiFetch(endpoint, { ...options, method: 'DELETE' }),
};