import { useState, useEffect, useCallback } from 'react';
import { apiFetch } from '../utils';

export function useCrudData(apiPath, { initialPerPage = 10 } = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1, totalItems: 0, perPage: initialPerPage });
  const [sort, setSort] = useState({ field: '', order: 'asc' });
  const [filters, setFilters] = useState({});
  const [searchField, setSearchField] = useState('');
  const [searchValue, setSearchValue] = useState('');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('page', pagination.page);
      params.append('per_page', pagination.perPage);
      if (sort.field) {
        params.append('sort_by', sort.field);
        params.append('sort_order', sort.order);
      }
      if (searchField && searchValue) {
        params.append('search_field', searchField);
        params.append('search_value', searchValue);
      }
      Object.keys(filters).forEach(key => {
        if (key !== 'search_field' && key !== 'search_value' && filters[key] !== undefined && filters[key] !== '') {
          params.append(key, filters[key]);
        }
      });

      const response = await apiFetch(`${apiPath}?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const result = await response.json();

      if (Array.isArray(result)) {
        setData(result);
        setPagination(prev => ({ ...prev, totalPages: 1, totalItems: result.length }));
      } else {
        setData(result.items || []);
        setPagination(prev => ({
          ...prev,
          totalPages: result.pages || 1,
          totalItems: result.total || 0
        }));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiPath, pagination.page, pagination.perPage, sort, filters, searchField, searchValue, refreshTrigger]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const setPage = (page) => setPagination(prev => ({ ...prev, page }));

  const setSearch = (field, value) => {
    setSearchField(field);
    setSearchValue(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const clearSearch = () => {
    setSearchField('');
    setSearchValue('');
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const createItem = async (payload) => {
    const headers = {};
    if (!(payload instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    const body = payload instanceof FormData ? payload : JSON.stringify(payload);

    const response = await apiFetch(apiPath, {
      method: 'POST',
      headers,
      body
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.message || 'Failed to create item');
    }
    setRefreshTrigger(prev => prev + 1);
  };

  const updateItem = async (id, payload) => {
    const headers = {};
    if (!(payload instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    const body = payload instanceof FormData ? payload : JSON.stringify(payload);

    const response = await apiFetch(`${apiPath}/${id}`, {
      method: 'PUT',
      headers,
      body
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.message || 'Failed to update item');
    }
    setRefreshTrigger(prev => prev + 1);
  };

  const deleteItem = async (id) => {
    const response = await apiFetch(`${apiPath}/${id}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.message || 'Failed to delete item');
    }
    setRefreshTrigger(prev => prev + 1);
  };

  const bulkDeleteItem = async (ids) => {
    const response = await apiFetch(apiPath, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: ids })
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.message || 'Failed to delete items');
    }
    setRefreshTrigger(prev => prev + 1);
  };

  return {
    data,
    loading,
    error,
    pagination,
    sort,
    filters,
    searchField,
    searchValue,
    setPage,
    setSort,
    setFilters,
    setSearch,
    clearSearch,
    createItem,
    updateItem,
    deleteItem,
    bulkDeleteItem,
    refresh: () => setRefreshTrigger(prev => prev + 1)
  };
}
