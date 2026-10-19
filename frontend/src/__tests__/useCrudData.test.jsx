import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCrudData } from '@/hooks/useCrudData';
import * as utils from '@/utils';

vi.mock('@/utils', async () => {
  const actual = await vi.importActual('@/utils');
  return {
    ...actual,
    apiFetch: vi.fn()
  };
});

describe('useCrudData hook with TanStack Query', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  it('fetches data successfully using TanStack Query', async () => {
    const mockData = { items: [{ id: 1, name: 'Item 1' }], pages: 1, total: 1 };
    utils.apiFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    const { result } = renderHook(() => useCrudData('/api/v1/test'), { wrapper });

    expect(result.current.loading).toBe(true);

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.data).toEqual([{ id: 1, name: 'Item 1' }]);
    expect(result.current.pagination.totalItems).toBe(1);
    expect(result.current.error).toBeNull();
  });

  it('handles mutations and query invalidation', async () => {
    utils.apiFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], pages: 1, total: 0 })
    });

    const { result } = renderHook(() => useCrudData('/api/v1/test'), { wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));

    utils.apiFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 2, name: 'New Item' })
    });

    utils.apiFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [{ id: 2, name: 'New Item' }], pages: 1, total: 1 })
    });

    await result.current.createItem({ name: 'New Item' });

    await waitFor(() => {
      expect(result.current.data).toEqual([{ id: 2, name: 'New Item' }]);
    });
  });
});
