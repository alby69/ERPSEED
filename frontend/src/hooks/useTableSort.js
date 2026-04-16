import { useState, useEffect, useCallback, useRef } from 'react';
import { apiFetch } from '../utils';

export function useTableSort(apiPath, { initialSortField = '', initialSortOrder = 'asc' } = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1, totalItems: 0, perPage: 10 });
  const [sortField, setSortField] = useState(initialSortField);
  const [sortOrder, setSortOrder] = useState(initialSortOrder);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchField, setSearchField] = useState('');
  const [searchValue, setSearchValue] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('page', pagination.page);
      params.append('per_page', pagination.perPage);
      if (sortField) {
        params.append('sort_by', sortField);
        params.append('sort_order', sortOrder);
      }
      if (searchTerm) {
        params.append('q', searchTerm);
      }
      if (searchField && searchValue) {
        params.append('search_field', searchField);
        params.append('search_value', searchValue);
      }

      const response = await apiFetch(`${apiPath}?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch data');

      const result = await response.json();

      if (Array.isArray(result)) {
        setData(result);
        setPagination(prev => ({ ...prev, page: 1, totalPages: 1, totalItems: result.length }));
      } else {
        setData(result.items || []);
        setPagination(prev => ({
          ...prev,
          page: result.page || 1,
          totalPages: result.pages || 1,
          totalItems: result.total || 0
        }));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiPath, pagination.page, pagination.perPage, sortField, sortOrder, searchTerm, searchField, searchValue]);

  useEffect(() => {
    fetchData();
  }, [sortField, sortOrder, pagination.page, pagination.perPage, searchTerm, searchField, searchValue]);

  const handleSort = useCallback((field) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
    setPagination(prev => ({ ...prev, page: 1 }));
  }, [sortField]);

  const handleSearch = useCallback((term) => {
    setSearchTerm(term);
    setSearchField('');
    setSearchValue('');
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handleSearchField = useCallback((field, value) => {
    setSearchField(field);
    setSearchValue(value || '');
    setSearchTerm('');
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handleSearchSubmit = useCallback(() => {
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handleClearSearch = useCallback(() => {
    setSearchTerm('');
    setSearchField('');
    setSearchValue('');
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const handlePageChange = useCallback((page) => {
    setPagination(prev => ({ ...prev, page }));
  }, []);

  return {
    data,
    loading,
    error,
    pagination,
    sortField,
    sortOrder,
    searchTerm,
    searchField,
    searchValue,
    setSortField,
    setSortOrder,
    setSearchTerm,
    setSearchField,
    setSearchValue,
    fetchData,
    handleSort,
    handleSearch,
    handleSearchField,
    handleSearchSubmit,
    handleClearSearch,
    handlePageChange
  };
}

export default useTableSort;
