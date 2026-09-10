import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, AuthProvider } from '@/context';
import ProjectLayout from '@/ProjectLayout';

Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
});

vi.mock('react-i18next', () => ({
    useTranslation: () => ({
        t: str => str,
        i18n: {
            language: 'it',
            changeLanguage: () => Promise.resolve()
        }
    })
}));

vi.mock('@/utils', async () => {
    const actual = await vi.importActual('@/utils');
    return {
        ...actual,
        apiFetch: vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ([])
        })
    };
});

describe('Global Keyboard Shortcuts', () => {
    it('listens to Ctrl+S and triggers submit on active form', () => {
        const submitFn = vi.fn(e => e.preventDefault());
        render(
            <BrowserRouter>
                <AuthProvider>
                    <ThemeProvider>
                        <ProjectLayout />
                        <form onSubmit={submitFn}>
                            <button type="submit">Salva</button>
                        </form>
                    </ThemeProvider>
                </AuthProvider>
            </BrowserRouter>
        );

        fireEvent.keyDown(window, { key: 's', ctrlKey: true });
        expect(submitFn).toHaveBeenCalledTimes(1);
    });

    it('listens to Escape and closes modal if present', () => {
        const closeFn = vi.fn();
        render(
            <BrowserRouter>
                <AuthProvider>
                    <ThemeProvider>
                        <ProjectLayout />
                        <div className="modal show">
                            <button className="btn-close" onClick={closeFn}>Close</button>
                        </div>
                    </ThemeProvider>
                </AuthProvider>
            </BrowserRouter>
        );

        fireEvent.keyDown(window, { key: 'Escape' });
        expect(closeFn).toHaveBeenCalledTimes(1);
    });
});
