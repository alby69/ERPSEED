import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, renderHook, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import useCommandPalette from '@/hooks/useCommandPalette';
import CommandPalette from '@/components/core/CommandPalette';

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

describe('useCommandPalette Hook', () => {
    it('toggles palette on Ctrl+K keyboard shortcut', () => {
        const { result } = renderHook(() => useCommandPalette());
        expect(result.current.isOpen).toBe(false);

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }));
        });

        expect(result.current.isOpen).toBe(true);

        act(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }));
        });

        expect(result.current.isOpen).toBe(false);
    });
});

describe('CommandPalette Component', () => {
    it('renders search input and commands when open', () => {
        render(
            <BrowserRouter>
                <CommandPalette isOpen={true} onClose={vi.fn()} />
            </BrowserRouter>
        );

        expect(screen.getByPlaceholderText(/Cerca pagina o azione rapida/i)).toBeDefined();
        expect(screen.getByText('Dashboard')).toBeDefined();
        expect(screen.getByText('Ordini Vendita')).toBeDefined();
    });

    it('filters commands when query is typed', () => {
        render(
            <BrowserRouter>
                <CommandPalette isOpen={true} onClose={vi.fn()} />
            </BrowserRouter>
        );

        const input = screen.getByPlaceholderText(/Cerca pagina o azione rapida/i);
        fireEvent.change(input, { target: { value: 'Prodott' } });

        expect(screen.getByText('Catalogo Prodotti')).toBeDefined();
        expect(screen.getByText('Nuovo Prodotto')).toBeDefined();
        expect(screen.queryByText('Dashboard')).toBeNull();
    });
});
