import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { apiFetch } from '../utils';

/**
 * Modernized useCrudData hook powered by TanStack Query (@tanstack/react-query).
 * Automatically handles data caching, background refetching, pagination, search,
 * sorting, filters, and cache-invalidated mutations.
 *
 * @param {string} apiPath - Base REST API path
 * @param {object} options - Initial options (initialPerPage, etc.)
 */
export function useCrudData(apiPath, { initialPerPage = 10 } = {}) {
  const queryClient = useQueryClient();

  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    totalItems: 0,
    perPage: initialPerPage
  });
  const [sort, setSort] = useState({ field: '', order: 'asc' });
  const [filters, setFilters] = useState({});
  const [searchField, setSearchField] = useState('');
  const [searchValue, setSearchValue] = useState('');

  // Construct query params for API call
  const queryParamsString = useMemo(() => {
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
    return params.toString();
  }, [pagination.page, pagination.perPage, sort, filters, searchField, searchValue]);

  // Query key uniquely identifies resource & current filter state
  const queryKey = useMemo(
    () => [apiPath, pagination.page, pagination.perPage, sort, filters, searchField, searchValue],
    [apiPath, pagination.page, pagination.perPage, sort, filters, searchField, searchValue]
  );

  const {
    data: queryResult,
    isLoading,
    isFetching,
    error: queryError,
    refetch
  } = useQuery({
    queryKey,
    queryFn: async () => {
      if (!apiPath) return { items: [], pages: 1, total: 0 };
      const response = await apiFetch(`${apiPath}?${queryParamsString}`);
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      const result = await response.json();
      if (Array.isArray(result)) {
        return { items: result, pages: 1, total: result.length };
      }
      return {
        items: result.items || [],
        pages: result.pages || 1,
        total: result.total || 0
      };
    },
    enabled: Boolean(apiPath),
    placeholderData: keepPreviousData
  });

  const data = queryResult?.items || [];
  const totalPages = queryResult?.pages || 1;
  const totalItems = queryResult?.total || 0;

  const currentPagination = useMemo(() => ({
    page: pagination.page,
    perPage: pagination.perPage,
    totalPages,
    totalItems
  }), [pagination.page, pagination.perPage, totalPages, totalItems]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: async (payload) => {
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
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [apiPath] });
    }
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, payload }) => {
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
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [apiPath] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      const response = await apiFetch(`${apiPath}/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to delete item');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [apiPath] });
    }
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: async (ids) => {
      const response = await apiFetch(apiPath, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: ids })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || 'Failed to delete items');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [apiPath] });
    }
  });

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

  return {
    data,
    loading: isLoading,
    isFetching,
    error: queryError ? queryError.message : null,
    pagination: currentPagination,
    sort,
    filters,
    searchField,
    searchValue,
    setPage,
    setSort,
    setFilters,
    setSearch,
    clearSearch,
    createItem: (payload) => createMutation.mutateAsync(payload),
    updateItem: (id, payload) => updateMutation.mutateAsync({ id, payload }),
    deleteItem: (id) => deleteMutation.mutateAsync(id),
    bulkDeleteItem: (ids) => bulkDeleteMutation.mutateAsync(ids),
    refresh: () => refetch()
  };
}

export default useCrudData;
