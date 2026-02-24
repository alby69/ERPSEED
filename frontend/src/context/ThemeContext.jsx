import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { ConfigProvider, theme as antTheme } from 'antd';
import { useParams } from 'react-router-dom';
import { apiFetch } from '@/utils';

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
    const [themeConfig, setThemeConfig] = useState({
        primaryColor: '#1677ff',
        borderRadius: 6,
        mode: 'light',
    });
    const [loading, setLoading] = useState(false);

    const fetchTheme = async (id) => {
        if (!id) return;
        setLoading(true);
        try {
            const response = await apiFetch(`/projects/${id}`);
            if (response.ok) {
                const project = await response.json();
                setThemeConfig({
                    primaryColor: project.primary_color || '#1677ff',
                    borderRadius: project.border_radius || 6,
                    mode: project.theme_mode || 'light',
                });
            }
        } catch (error) {
            console.error('Error fetching theme:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateTheme = (newConfig) => {
        setThemeConfig(prev => ({ ...prev, ...newConfig }));
    };

    const resetTheme = () => {
        setThemeConfig({
            primaryColor: '#1677ff',
            borderRadius: 6,
            mode: 'light',
        });
    };

    const antdThemeConfig = useMemo(() => ({
        algorithm: themeConfig.mode === 'dark' ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
        token: {
            colorPrimary: themeConfig.primaryColor,
            borderRadius: themeConfig.borderRadius,
        },
    }), [themeConfig]);

    return (
        <ThemeContext.Provider value={{ themeConfig, updateTheme, fetchTheme, resetTheme }}>
            <ConfigProvider theme={antdThemeConfig}>
                {children}
            </ConfigProvider>
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
