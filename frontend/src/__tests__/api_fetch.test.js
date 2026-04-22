import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch, BASE_URL } from '../utils';

// Mock global fetch
global.fetch = vi.fn();

describe('apiFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
  });

  it('should include Authorization header if token exists', async () => {
    localStorage.setItem('access_token', 'test-token');
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    await apiFetch('/test-endpoint');

    expect(fetch).toHaveBeenCalledWith(
      `${BASE_URL}/test-endpoint`,
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token',
        }),
      })
    );
  });

  it('should handle 401 and try to refresh token', async () => {
    localStorage.setItem('access_token', 'expired-token');
    localStorage.setItem('refresh_token', 'refresh-token');

    // First call returns 401
    fetch.mockResolvedValueOnce({
      status: 401,
      ok: false,
    });

    // Refresh call returns 200 with new token
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'new-token' }),
    });

    // Final call returns 200
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'secret' }),
    });

    const response = await apiFetch('/secure-data');
    const data = await response.json();

    expect(data.data).toBe('secret');
    expect(localStorage.getItem('access_token')).toBe('new-token');
    expect(fetch).toHaveBeenCalledTimes(3);
  });
});
