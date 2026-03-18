/**
 * useModules Hook - Frontend hook per gestione moduli
 */
import { useState, useEffect, useCallback } from 'react';
import { apiFetch } from '../utils';

export function useModules() {
  const [modules, setModules] = useState({
    available: [],
    enabled: [],
    menu: [],
    widgets: [],
    loading: true,
    error: null
  });

  const fetchModulesInfo = useCallback(async () => {
    try {
      setModules(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await apiFetch('/api/v1/system/modules-info');
      const data = await response.json();
      
      setModules({
        available: data.available_modules || [],
        enabled: data.enabled_modules || [],
        menu: data.menu || [],
        widgets: data.widgets || [],
        loading: false,
        error: null
      });
    } catch (error) {
      setModules(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Errore nel caricamento moduli'
      }));
    }
  }, []);

  useEffect(() => {
    fetchModulesInfo();
  }, [fetchModulesInfo]);

  const enableModule = useCallback(async (moduleId, config = {}, licenseKey = null) => {
    try {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';
      
      const response = await fetch(`${BASE_URL}/api/v1/modules/enabled`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ module_id: moduleId })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Errore ${response.status}`);
      }
      
      await fetchModulesInfo();
      return await response.json();
    } catch (error) {
      throw new Error(error.message || 'Errore nell\'attivazione del modulo');
    }
  }, [fetchModulesInfo]);

  const disableModule = useCallback(async (moduleId) => {
    try {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5002'}/api/v1/modules/${moduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Errore ${response.status}`);
      }
      
      await fetchModulesInfo();
    } catch (error) {
      throw new Error(error.message || 'Errore nella disattivazione del modulo');
    }
  }, [fetchModulesInfo]);

  const isModuleEnabled = useCallback((moduleId) => {
    return modules.enabled.includes(moduleId);
  }, [modules.enabled]);

  const getModuleConfig = useCallback(async (moduleId) => {
    try {
      const response = await apiFetch(`/api/v1/modules/${moduleId}/config`);
      const data = await response.json();
      return data.config || {};
    } catch (error) {
      throw new Error(error.message || 'Errore nel recupero della configurazione');
    }
  }, []);

  const updateModuleConfig = useCallback(async (moduleId, config) => {
    try {
      const response = await apiFetch(`/api/v1/modules/${moduleId}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config })
      });
      const data = await response.json();
      return data.config;
    } catch (error) {
      throw new Error(error.message || 'Errore nell\'aggiornamento della configurazione');
    }
  }, []);

  return {
    ...modules,
    enableModule,
    disableModule,
    isModuleEnabled,
    getModuleConfig,
    updateModuleConfig,
    refresh: fetchModulesInfo
  };
}

/**
 * Hook per verificare accesso a un modulo specifico
 */
export function useModuleAccess(moduleId) {
  const { enabled, loading, error } = useModules();
  
  return {
    hasAccess: enabled.includes(moduleId),
    loading,
    error
  };
}

/**
 * Hook per ottenere solo il menu
 */
export function useMenu() {
  const { menu, loading, error } = useModules();
  return { menu, loading, error };
}

/**
 * Hook per ottenere solo i widget
 */
export function useWidgets() {
  const { widgets, loading, error } = useModules();
  return { widgets, loading, error };
}

export default useModules;
