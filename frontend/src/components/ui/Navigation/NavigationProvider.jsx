import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { apiFetch } from '@/utils';
import { DEFAULT_NAVIGATIONS, PERMISSION_LEVELS, hasPermission } from './constants';

const NavigationContext = createContext(null);

export const NavigationProvider = ({ 
  children, 
  customNavigation = null,
  projectMenuItems = [],
}) => {
  const [navigation, setNavigation] = useState(DEFAULT_NAVIGATIONS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load custom navigation from API
  const loadNavigation = useCallback(async (projectId = null) => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to fetch custom navigation from API
      const endpoint = projectId 
        ? `/api/projects/${projectId}/navigation`
        : '/api/navigation';
      
      const response = await apiFetch(endpoint);
      
      if (response.ok) {
        const customNav = await response.json();
        setNavigation(customNav);
      }
    } catch (err) {
      console.warn('Using default navigation:', err.message);
      // Use default navigation on error
    } finally {
      setLoading(false);
    }
  }, []);

  // Merge project menu items into navigation
  const getMergedNavigation = useCallback((user) => {
    const nav = { ...navigation };
    
    // Add project menu items to app section
    if (projectMenuItems.length > 0 && nav.main) {
      const appSection = nav.main.find(item => item.id === 'app-section');
      if (appSection && appSection.children) {
        // Filter out duplicates
        const existingPaths = appSection.children.map(child => child.path);
        const newItems = projectMenuItems.filter(
          item => !existingPaths.includes(item.path)
        );
        appSection.children = [...appSection.children, ...newItems];
      }
    }
    
    return nav;
  }, [navigation, projectMenuItems]);

  // Filter navigation by permission
  const getFilteredNavigation = useCallback((user) => {
    const merged = getMergedNavigation(user);
    
    const filterByPermission = (items) => {
      return items
        .filter(item => hasPermission(item, user))
        .map(item => {
          if (item.children) {
            return {
              ...item,
              children: filterByPermission(item.children),
            };
          }
          return item;
        });
    };

    const filtered = {};
    Object.keys(merged).forEach(key => {
      filtered[key] = filterByPermission(merged[key]);
    });

    return filtered;
  }, [getMergedNavigation]);

  // Add custom section to navigation
  const addSection = useCallback((sectionKey, items) => {
    setNavigation(prev => ({
      ...prev,
      [sectionKey]: items,
    }));
  }, []);

  // Remove section from navigation
  const removeSection = useCallback((sectionKey) => {
    setNavigation(prev => {
      const newNav = { ...prev };
      delete newNav[sectionKey];
      return newNav;
    });
  }, []);

  // Update single item in navigation
  const updateItem = useCallback((sectionKey, itemId, updates) => {
    setNavigation(prev => {
      const section = prev[sectionKey];
      if (!section) return prev;

      const updateInItems = (items) => {
        return items.map(item => {
          if (item.id === itemId) {
            return { ...item, ...updates };
          }
          if (item.children) {
            return { ...item, children: updateInItems(item.children) };
          }
          return item;
        });
      };

      return {
        ...prev,
        [sectionKey]: updateInItems(section),
      };
    });
  }, []);

  const value = {
    navigation,
    loading,
    error,
    loadNavigation,
    getMergedNavigation,
    getFilteredNavigation,
    addSection,
    removeSection,
    updateItem,
    PERMISSION_LEVELS,
    hasPermission,
  };

  return (
    <NavigationContext.Provider value={value}>
      {children}
    </NavigationContext.Provider>
  );
};

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within NavigationProvider');
  }
  return context;
};

export default NavigationContext;
