import React from 'react';
import { useColumnManagerWithDrawer } from '../hooks/useColumnManager';
import ColumnSettingsButton from './ColumnSettingsButton';

/**
 * ColumnsControl è un componente "Plugin" che astrae la gestione delle colonne.
 * Gestisce visibilità, ordinamento e persistenza (localStorage) e fornisce
 * i dati processati e il pulsante di controllo ai suoi figli.
 */
export default function ColumnsControl({ pageKey, columns: rawColumns, children }) {
  const colManager = useColumnManagerWithDrawer(pageKey, rawColumns);
  
  if (typeof children === 'function') {
    return children({
      columns: colManager.processedColumns,
      button: <ColumnSettingsButton manager={colManager} />,
      manager: colManager
    });
  }
  return children;
}
