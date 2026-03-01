import React from 'react';
import { Dropdown, message } from 'antd';
import { 
  DownloadOutlined, 
  UploadOutlined,
  FileTextOutlined 
} from '@ant-design/icons';

function ImportExportContextMenu({ 
  type,
  entityId,
  projectId,
  entityName = '',
  onImportComplete = null,
  children,
  showExportConfig = true,
  showExportData = false,
  showImport = true,
  exportConfigLabel = 'Esporta Configurazione',
  exportDataLabel = 'Esporta Dati',
  importConfigLabel = 'Importa Configurazione'
}) {
  const getExportUrl = (mode) => {
    const baseUrl = '/api/v1/import-export';
    switch (type) {
      case 'sysmodel':
        return mode === 'config' 
          ? `${baseUrl}/sysmodel/${entityId}/export-config`
          : `${baseUrl}/sysmodel/${entityId}/export-data`;
      case 'block':
        return `${baseUrl}/block/${entityId}/export-config`;
      case 'workflow':
        return `${baseUrl}/workflow/${entityId}/export-config`;
      case 'module':
        return mode === 'config'
          ? `${baseUrl}/module/${entityId}/export-config`
          : `${baseUrl}/module/${entityId}/export-data`;
      default:
        return '';
    }
  };

  const getImportUrl = () => {
    const baseUrl = '/api/v1/import-export';
    switch (type) {
      case 'sysmodel':
        return `${baseUrl}/sysmodel/${projectId}/import-config`;
      case 'block':
        return `${baseUrl}/block/${projectId}/import-config`;
      case 'workflow':
        return `${baseUrl}/workflow/${projectId}/import-config`;
      case 'module':
        return `${baseUrl}/module/${projectId}/import-config`;
      default:
        return '';
    }
  };

  const handleExport = async (mode = 'config') => {
    if (!entityId) {
      message.error('Seleziona un elemento da esportare');
      return;
    }

    try {
      const url = getExportUrl(mode);
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Export failed');

      const data = await response.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const filename = `${type}_${entityName || entityId}_${mode}_${new Date().toISOString().split('T')[0]}.json`;
      const urlBlob = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(urlBlob);
      
      message.success('Esportazione completata!');
    } catch (error) {
      message.error('Errore nell\'export: ' + error.message);
    }
  };

  const handleImport = async (file) => {
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      
      const url = getImportUrl();
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Import failed');
      }

      const result = await response.json();
      message.success(`Import completato: ${JSON.stringify(result)}`);
      
      if (onImportComplete) {
        onImportComplete(result);
      }
    } catch (error) {
      message.error('Errore nell\'import: ' + error.message);
    }
    
    return false;
  };

  const menuItems = [
    ...(showExportConfig ? [{
      key: 'export-config',
      icon: <DownloadOutlined />,
      label: exportConfigLabel,
      onClick: () => handleExport('config')
    }] : []),
    ...(showExportData ? [{
      key: 'export-data',
      icon: <FileTextOutlined />,
      label: exportDataLabel,
      onClick: () => handleExport('data')
    }] : []),
    ...(showImport ? [{
      key: 'import',
      icon: <UploadOutlined />,
      label: importConfigLabel,
      onClick: () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
          const file = e.target.files[0];
          if (file) {
            await handleImport(file);
          }
        };
        input.click();
      }
    }] : [])
  ];

  if (menuItems.length === 0) {
    return <>{children}</>;
  }

  return (
    <Dropdown 
      menu={{ items: menuItems }} 
      trigger={['contextMenu']}
    >
      {children}
    </Dropdown>
  );
}

export default ImportExportContextMenu;
