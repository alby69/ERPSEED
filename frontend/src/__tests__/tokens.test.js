import { describe, it, expect } from 'vitest';
import { DEFAULT_THEME_TOKENS, getDesignTokens } from '../theme/tokens';

describe('Design Tokens Module', () => {
    it('provides valid default tokens', () => {
        expect(DEFAULT_THEME_TOKENS.colorPrimary).toBe('#1677ff');
        expect(DEFAULT_THEME_TOKENS.borderRadius).toBe(6);
        expect(DEFAULT_THEME_TOKENS.spacing.md).toBe(16);
        expect(DEFAULT_THEME_TOKENS.fontSize.md).toBe(16);
    });

    it('generates light mode design tokens correctly', () => {
        const tokens = getDesignTokens({ primaryColor: '#0050b3', borderRadius: 8, mode: 'light' });
        expect(tokens.colorPrimary).toBe('#0050b3');
        expect(tokens.borderRadius).toBe(8);
        expect(tokens.colorTextBase).toBe('#000000');
        expect(tokens.colorBgBase).toBe('#ffffff');
    });

    it('generates dark mode design tokens correctly', () => {
        const tokens = getDesignTokens({ mode: 'dark' });
        expect(tokens.colorPrimary).toBe('#1677ff');
        expect(tokens.colorTextBase).toBe('#ffffff');
        expect(tokens.colorBgBase).toBe('#141414');
        expect(tokens.mode).toBe('dark');
    });
});
