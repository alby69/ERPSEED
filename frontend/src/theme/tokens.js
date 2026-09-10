/**
 * Centralized Design Token Layer for ERPSEED UI/UX
 * Provides a single source of truth for colors, spacing, typography, radii, and status feedback.
 */

export const DEFAULT_THEME_TOKENS = {
    colorPrimary: '#1677ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1677ff',
    colorTextBase: '#000000',
    colorBgBase: '#ffffff',
    borderRadius: 6,
    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
    },
    fontSize: {
        xs: 12,
        sm: 14,
        md: 16,
        lg: 20,
        xl: 24,
    },
};

/**
 * Derives dynamic theme tokens based on user configuration.
 * @param {Object} themeConfig - Theme configuration object
 * @returns {Object} Full token object for Ant Design & custom components
 */
export const getDesignTokens = (themeConfig = {}) => {
    const isDark = themeConfig.mode === 'dark';
    const primaryColor = themeConfig.primaryColor || DEFAULT_THEME_TOKENS.colorPrimary;
    const borderRadius = themeConfig.borderRadius ?? DEFAULT_THEME_TOKENS.borderRadius;

    return {
        ...DEFAULT_THEME_TOKENS,
        colorPrimary: primaryColor,
        borderRadius: borderRadius,
        colorTextBase: isDark ? '#ffffff' : '#000000',
        colorBgBase: isDark ? '#141414' : '#ffffff',
        colorBgContainerDark: '#1f1f1f',
        colorTextDark: '#e6f7ff',
        mode: themeConfig.mode || 'light',
    };
};
