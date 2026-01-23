import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { apiFetch } from '../utils/api';

const ImportProjectButton = ({ onSuccess }) => {
    const [loading, setLoading] = useState(false);

    const customRequest = async ({ file, onSuccess: onUploadSuccess, onError }) => {
        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        try {
            // Nota: Non impostiamo 'Content-Type' esplicitamente.
            // Il browser lo imposterà automaticamente come 'multipart/form-data' con il boundary corretto.
            const response = await apiFetch('/projects/import', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                message.success(data.message || 'Progetto importato con successo!');
                onUploadSuccess(data);
                if (onSuccess) onSuccess();
            } else {
                const error = await response.json();
                message.error(error.message || 'Errore durante l\'importazione.');
                onError(new Error(error.message));
            }
        } catch (err) {
            message.error('Errore di connessione durante l\'upload.');
            onError(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Upload customRequest={customRequest} showUploadList={false} accept=".json">
            <Button loading={loading}>Importa Template</Button>
        </Upload>
    );
};

export default ImportProjectButton;