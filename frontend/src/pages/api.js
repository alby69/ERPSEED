import { apiFetch } from '../utils';

// A simplified client object for common CRUD operations
const toBody = (data) => {
  if (data && typeof data === 'object' && !(data instanceof FormData)) {
    return JSON.stringify(data);
  }
  return data;
};

export const apiClient = {
    get: async (endpoint, options) => apiFetch(endpoint, { ...options, method: 'GET' }).then(res => res.json()),
    post: async (endpoint, data, options) => apiFetch(endpoint, { ...options, method: 'POST', body: toBody(data) }).then(res => res.json()),
    put: async (endpoint, data, options) => apiFetch(endpoint, { ...options, method: 'PUT', body: toBody(data) }).then(res => res.json()),
    delete: async (endpoint, options) => apiFetch(endpoint, { ...options, method: 'DELETE' }),
};