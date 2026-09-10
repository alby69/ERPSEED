import { useState, useEffect, useCallback } from 'react';

/**
 * useCommandPalette Hook
 *
 * Manages Command Palette visibility and listens globally for Ctrl+K / Cmd+K.
 */
export const useCommandPalette = () => {
    const [isOpen, setIsOpen] = useState(false);

    const open = useCallback(() => setIsOpen(true), []);
    const close = useCallback(() => setIsOpen(false), []);
    const toggle = useCallback(() => setIsOpen(prev => !prev), []);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                toggle();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [toggle]);

    return { isOpen, open, close, toggle };
};

export default useCommandPalette;
