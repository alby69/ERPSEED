import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useResponsive } from '../hooks/useResponsive';
import { Grid } from 'antd';

vi.mock('antd', async (importOriginal) => {
    const actual = await importOriginal();
    return {
        ...actual,
        Grid: {
            useBreakpoint: vi.fn(),
        },
    };
});

describe('useResponsive Hook', () => {
    it('identifies mobile screens correctly (<768px)', () => {
        vi.mocked(Grid.useBreakpoint).mockReturnValue({ xs: true, sm: true });
        const { result } = renderHook(() => useResponsive());

        expect(result.current.isMobile).toBe(true);
        expect(result.current.isTablet).toBe(false);
        expect(result.current.isDesktop).toBe(false);
    });

    it('identifies tablet screens correctly (768px - 991px)', () => {
        vi.mocked(Grid.useBreakpoint).mockReturnValue({ xs: true, sm: true, md: true });
        const { result } = renderHook(() => useResponsive());

        expect(result.current.isMobile).toBe(false);
        expect(result.current.isTablet).toBe(true);
        expect(result.current.isDesktop).toBe(false);
    });

    it('identifies desktop screens correctly (>=992px)', () => {
        vi.mocked(Grid.useBreakpoint).mockReturnValue({ xs: true, sm: true, md: true, lg: true, xl: true });
        const { result } = renderHook(() => useResponsive());

        expect(result.current.isMobile).toBe(false);
        expect(result.current.isTablet).toBe(false);
        expect(result.current.isDesktop).toBe(true);
    });
});
