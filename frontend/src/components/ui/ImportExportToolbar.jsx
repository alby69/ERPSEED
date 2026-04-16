import React, { useState } from 'react';
import { Button, Upload, message, Modal, Dropdown, Menu, Divider } from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  FileTextOutlined,
  InboxOutlined,
  MoreOutlined
} from '@ant-design/icons';

const { Dragger } = Upload;

function ImportExportToolbar({
  type = 'sysmodel',        // sysmodel, block, workflow, module, project
  entityId = null,         // ID dell'entità corrente
  projectId = null,        // ID del progetto
  onImportComplete = null, // Callback dopo import
  showImport = true,
  showExport = true,
  exportConfigLabel = 'Esporta Configurazione',
  exportDataLabel = 'Esporta Dati',
  importConfigLabel = 'Importa Configurazione',
  importDataLabel = 'Importa Dati'
}) {
  const [exporting, setExporting] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importMode, setImportMode] = useState('config'); // 'config' or 'data'

  // Costruisci URL per export
  const getExportUrl = (mode) => {
    const baseUrl = '/api/v1/import-export';
    switch (type) {
      case 'sysmodel':
        return mode === 'config'
          ? `${baseUrl}/sysmodel/${entityId}/export-config`
          : `${baseUrl}/sysmodel/${entityId}/export-data`;
      case 'sysmodels_project':
        return `${baseUrl}/sysmodels/project/${projectId}/export-all`;
      case 'block':
        return `${baseUrl}/block/${entityId}/export-config`;
      case 'workflow':
        return `${baseUrl}/workflow/${entityId}/export-config`;
      case 'module':
        return mode === 'config'
          ? `${baseUrl}/module/${entityId}/export-config`
          : `${baseUrl}/module/${entityId}/export-data`;
      case 'project':
        return `${baseUrl}/project/${projectId}/export-full`;
      default:
        return '';
    }
  };

  // Costruisci URL per import
  const getImportUrl = () => {
    const baseUrl = '/api/v1/import-export';
    const targetId = entityId || projectId;
    switch (type) {
      case 'sysmodel':
        return importMode === 'config'
          ? `${baseUrl}/sysmodel/${projectId}/import-config`
          : `${baseUrl}/sysmodel/${projectId}/import-data`;
      case 'block':
        return `${baseUrl}/block/${projectId}/import-config`;
      case 'workflow':
        return `${baseUrl}/workflow/${projectId}/import-config`;
      case 'module':
        return `${baseUrl}/module/${projectId}/import-config`;
      case 'project':
        return `${baseUrl}/project/${projectId}/import-full`;
      default:
        return '';
    }
  };

  // Esporta configurazione
  const handleExportConfig = async () => {
    if (!entityId && type !== 'project' && type !== 'sysmodels_project') {
      message.error('Seleziona un elemento da esportare');
      return;
    }

    setExporting(true);
    try {
      const url = getExportUrl('config');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Export failed');

      const data = await response.json();

      // Download file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const filename = type === 'sysmodels_project'
        ? `sysmodels_project_${new Date().toISOString().split('T')[0]}.json`
        : `${type}_config_${new Date().toISOString().split('T')[0]}.json`;
      const urlBlob = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(urlBlob);

      message.success('Configurazione esportata!');
    } catch (error) {
      message.error('Errore nell\'export: ' + error.message);
    } finally {
      setExporting(false);
    }
  };

  // Esporta dati
  const handleExportData = async () => {
    if (!entityId && type !== 'project' && type !== 'sysmodels_project') {
      message.error('Seleziona un elemento da esportare');
      return;
    }

    setExporting(true);
    try {
      const url = getExportUrl('data');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Export failed');

      const data = await response.json();

      // Download file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const filename = `${type}_data_${new Date().toISOString().split('T')[0]}.json`;
      const urlBlob = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(urlBlob);

      message.success('Dati esportati!');
    } catch (error) {
      message.error('Errore nell\'export: ' + error.message);
    } finally {
      setExporting(false);
    }
  };

  // Importa file
  const handleImport = async (file) => {
    setImporting(true);

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
    } finally {
      setImporting(false);
    }

    return false; // Prevent default upload
  };

  // Menu contestuale
  const getExportMenu = () => ({
    items: [
      showExport && entityId && type !== 'project' && type !== 'block' && type !== 'workflow' && type !== 'sysmodels_project' ? {
        key: 'export-data',
        icon: <FileTextOutlined />,
        label: exportDataLabel,
        onClick: handleExportData
      } : null,
      showExport ? {
        key: 'export-config',
        icon: <DownloadOutlined />,
        label: exportConfigLabel,
        onClick: handleExportConfig
      } : null,
    ].filter(Boolean)
  });

  return (
    <div style={{ display: 'inline-flex', gap: 8 }}>
      {/* Pulsante Export */}
      {showExport && (
        <Dropdown menu={getExportMenu()} trigger={['click']}>
          <Button icon={<DownloadOutlined />} loading={exporting}>
            Export
          </Button>
        </Dropdown>
      )}

      {/* Pulsante Import con Drag & Drop */}
      {showImport && (
        <Dragger
          accept=".json"
          showUploadList={false}
          beforeUpload={handleImport}
          disabled={importing}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Trascina un file JSON qui</p>
          <p className="ant-upload-hint">oppure clicca per importare</p>
        </Dragger>
      )}
    </div>
  );
}

export default ImportExportToolbar;
