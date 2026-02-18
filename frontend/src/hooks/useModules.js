/**
 * useModules Hook - Frontend hook per gestione moduli
 */
import { useState, useEffect, useCallback } from 'react';
import { api } from '../components/api';

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
      
      const response = await api.get('/system/modules-info');
      
      setModules({
        available: response.data.available_modules || [],
        enabled: response.data.enabled_modules || [],
        menu: response.data.menu || [],
        widgets: response.data.widgets || [],
        loading: false,
        error: null
      });
    } catch (error) {
      setModules(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.message || error.message
      }));
    }
  }, []);

  useEffect(() => {
    fetchModulesInfo();
  }, [fetchModulesInfo]);

  const enableModule = useCallback(async (moduleId, config = {}, licenseKey = null) => {
    try {
      const response = await api.post('/modules/enabled', {
        module_id: moduleId,
        config,
        license_key: licenseKey
      });
      
      await fetchModulesInfo();
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Errore nell\'attivazione del modulo');
    }
  }, [fetchModulesInfo]);

  const disableModule = useCallback(async (moduleId) => {
    try {
      await api.delete(`/modules/${moduleId}`);
      await fetchModulesInfo();
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Errore nella disattivazione del modulo');
    }
  }, [fetchModulesInfo]);

  const isModuleEnabled = useCallback((moduleId) => {
    return modules.enabled.includes(moduleId);
  }, [modules.enabled]);

  const getModuleConfig = useCallback(async (moduleId) => {
    try {
      const response = await api.get(`/modules/${moduleId}/config`);
      return response.data.config || {};
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Errore nel recupero della configurazione');
    }
  }, []);

  const updateModuleConfig = useCallback(async (moduleId, config) => {
    try {
      const response = await api.put(`/modules/${moduleId}/config`, { config });
      return response.data.config;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Errore nell\'aggiornamento della configurazione');
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
