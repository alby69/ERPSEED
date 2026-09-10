import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import InlineEditableTable from '@/components/ui/InlineEditableTable';

// Mock matchMedia for Ant Design components in jsdom environment
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

describe('InlineEditableTable Component', () => {
    it('renders empty table and total summary', () => {
        render(<InlineEditableTable value={[]} />);
        expect(screen.getByText(/Totale Ordine/i)).toBeDefined();
        const zeros = screen.getAllByText(/€ 0.00/i);
        expect(zeros.length).toBeGreaterThan(0);
    });

    it('triggers onChange when add line button is clicked', () => {
        const handleChange = vi.fn();
        render(<InlineEditableTable value={[]} onChange={handleChange} />);

        const addBtn = screen.getByRole('button', { name: /Aggiungi Riga/i });
        fireEvent.click(addBtn);

        expect(handleChange).toHaveBeenCalledTimes(1);
        const newLines = handleChange.mock.calls[0][0];
        expect(newLines.length).toBe(1);
        expect(newLines[0].quantity).toBe(1);
    });

    it('calculates total price correctly with discount', () => {
        const lines = [
            {
                id: 1,
                product_id: 10,
                description: 'Prodotto Test',
                quantity: 2,
                unit_price: 100,
                discount_percent: 10,
                total_price: 180
            }
        ];
        render(<InlineEditableTable value={lines} />);
        expect(screen.getByDisplayValue('Prodotto Test')).toBeDefined();
        expect(screen.getByText('€ 180.00')).toBeDefined();
        expect(screen.getByText(/Sconto Totale: -€ 20.00/i)).toBeDefined();
    });
});
