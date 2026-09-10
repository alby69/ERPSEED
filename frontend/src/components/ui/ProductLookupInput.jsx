import React, { useState, useEffect, useRef } from 'react';
import { Select, Spin } from 'antd';
import { apiFetch } from '@/utils';

/**
 * ProductLookupInput - Debounced Product Autocomplete Select
 *
 * @param {number|string} value - Selected product ID or name
 * @param {function} onChange - Triggered on selection change
 * @param {function} onSelectProduct - Callback with full product object when selected
 * @param {string} placeholder - Input placeholder
 * @param {boolean} disabled - Disabled state
 */
const ProductLookupInput = ({
    value,
    onChange,
    onSelectProduct,
    placeholder = 'Cerca prodotto per codice o nome...',
    disabled = false,
    style
}) => {
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(false);
    const debounceTimeout = useRef(null);

    const searchProducts = (query = '') => {
        if (debounceTimeout.current) {
            clearTimeout(debounceTimeout.current);
        }

        debounceTimeout.current = setTimeout(() => {
            setLoading(true);
            const endpoint = query ? `/api/v1/products?q=${encodeURIComponent(query)}` : '/api/v1/products?per_page=20';
            apiFetch(endpoint)
                .then(res => res.json())
                .then(data => {
                    const items = Array.isArray(data) ? data : (data.items || []);
                    const mapped = items.map(p => ({
                        value: p.id,
                        label: `${p.code ? '[' + p.code + '] ' : ''}${p.name || p.description || 'Prodotto #' + p.id} - €${p.price || p.unit_price || 0}`,
                        product: p
                    }));
                    setOptions(mapped);
                })
                .catch(err => {
                    console.error('Error fetching products:', err);
                    setOptions([]);
                })
                .finally(() => setLoading(false));
        }, 300);
    };

    useEffect(() => {
        searchProducts('');
        return () => {
            if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
        };
    }, []);

    const handleSelect = (selectedValue, option) => {
        if (onChange) onChange(selectedValue);
        if (onSelectProduct && option?.product) {
            onSelectProduct(option.product);
        }
    };

    return (
        <Select
            showSearch
            value={value || undefined}
            placeholder={placeholder}
            disabled={disabled}
            style={style || { width: '100%' }}
            filterOption={false}
            onSearch={searchProducts}
            onSelect={handleSelect}
            notFoundContent={loading ? <Spin size="small" /> : 'Nessun prodotto trovato'}
            options={options}
            allowClear
            onClear={() => {
                if (onChange) onChange(null);
                if (onSelectProduct) onSelectProduct(null);
            }}
        />
    );
};

export default ProductLookupInput;
