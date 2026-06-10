import { useState, useCallback, useMemo } from 'react';

const STORAGE_PREFIX = 'columns_config_';

function loadConfig(pageKey) {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + pageKey);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveConfig(pageKey, config) {
  try {
    localStorage.setItem(STORAGE_PREFIX + pageKey, JSON.stringify(config));
  } catch {
  }
}

export function useColumnManager(pageKey, defaultColumns) {
  const defaultsKeyed = useMemo(() => {
    return defaultColumns.map((col, i) => ({
      ...col,
      _key: col.key || col.dataIndex || `_col${i}`,
      _defaultOrder: i,
    }));
  }, [defaultColumns]);

  const defaultOrder = useMemo(() => defaultsKeyed.map(c => c._key), [defaultsKeyed]);
  const defaultHidden = useMemo(() => ({}), []);

  const [config, setConfig] = useState(() => {
    const saved = loadConfig(pageKey);
    if (saved && Array.isArray(saved.order)) {
      return {
        order: saved.order,
        hidden: saved.hidden || {},
      };
    }
    return { order: [...defaultOrder], hidden: {} };
  });

  const allKeys = useMemo(() => {
    const keys = new Set(defaultOrder);
    config.order.forEach(k => keys.add(k));
    return [...keys];
  }, [defaultOrder, config.order]);

  const processedColumns = useMemo(() => {
    const colMap = {};
    defaultsKeyed.forEach(c => { colMap[c._key] = c; });

    const ordered = [];
    const seen = new Set();
    for (const key of config.order) {
      if (colMap[key] && !seen.has(key)) {
        seen.add(key);
        ordered.push(colMap[key]);
      }
    }
    for (const key of allKeys) {
      if (colMap[key] && !seen.has(key)) {
        seen.add(key);
        ordered.push(colMap[key]);
      }
    }

    return ordered.filter(c => !config.hidden[c._key]);
  }, [defaultsKeyed, config, allKeys]);

  const persist = useCallback((newConfig) => {
    setConfig(newConfig);
    saveConfig(pageKey, newConfig);
  }, [pageKey]);

  const toggleColumn = useCallback((key) => {
    setConfig(prev => {
      const hidden = { ...prev.hidden };
      if (hidden[key]) {
        delete hidden[key];
      } else {
        hidden[key] = true;
      }
      const next = { ...prev, hidden };
      saveConfig(pageKey, next);
      return next;
    });
  }, [pageKey]);

  const moveColumn = useCallback((key, direction) => {
    setConfig(prev => {
      const order = [...prev.order];
      const idx = order.indexOf(key);
      if (idx === -1) return prev;
      const newIdx = idx + direction;
      if (newIdx < 0 || newIdx >= order.length) return prev;
      [order[idx], order[newIdx]] = [order[newIdx], order[idx]];
      const next = { ...prev, order };
      saveConfig(pageKey, next);
      return next;
    });
  }, [pageKey]);

  const resetColumns = useCallback(() => {
    const next = { order: [...defaultOrder], hidden: {} };
    setConfig(next);
    saveConfig(pageKey, next);
  }, [pageKey, defaultOrder]);

  const allColumns = useMemo(() => {
    const colMap = {};
    defaultsKeyed.forEach(c => { colMap[c._key] = c; });

    const ordered = config.order.filter(k => colMap[k]);
    for (const key of allKeys) {
      if (colMap[key] && !ordered.includes(key)) {
        ordered.push(key);
      }
    }

    return ordered.map(key => ({
      ...colMap[key],
      _visible: !config.hidden[key],
    }));
  }, [defaultsKeyed, config, allKeys]);

  const hasChanges = useMemo(() => {
    if (config.order.length !== defaultOrder.length) return true;
    for (let i = 0; i < config.order.length; i++) {
      if (config.order[i] !== defaultOrder[i]) return true;
    }
    const hiddenKeys = Object.keys(config.hidden);
    if (hiddenKeys.length > 0) return true;
    return false;
  }, [config, defaultOrder]);

  return {
    processedColumns,
    allColumns,
    visibleColumns: allColumns.filter(c => c._visible),
    hiddenColumns: allColumns.filter(c => !c._visible),
    toggleColumn,
    moveColumn,
    resetColumns,
    hasChanges,
  };
}

export function useColumnManagerWithDrawer(pageKey, defaultColumns) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const mgr = useColumnManager(pageKey, defaultColumns);
  return {
    ...mgr,
    drawerOpen,
    openDrawer: () => setDrawerOpen(true),
    closeDrawer: () => setDrawerOpen(false),
  };
}

export default useColumnManager;
