import React, { useState } from 'react';
import { Upload, Button, message } from 'antd';
import { apiFetch } from '@/utils';

const ImportProjectButton = ({ onSuccess }) => {
    const [loading, setLoading] = useState(false);

    const customRequest = async ({ file, onSuccess: onUploadSuccess, onError }) => {
        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        try {
            // Note: We don't set 'Content-Type' explicitly.
            // The browser will automatically set it as 'multipart/form-data' with the correct boundary.
            const response = await apiFetch('/projects/import', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                message.success(data.message || 'Project imported successfully!');
                onUploadSuccess(data);
                if (onSuccess) onSuccess();
            } else {
                const error = await response.json();
                message.error(error.message || 'Error during import.');
                onError(new Error(error.message));
            }
        } catch (err) {
            message.error('Connection error during upload.');
            onError(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Upload customRequest={customRequest} showUploadList={false} accept=".json">
            <Button loading={loading}>Import Template</Button>
        </Upload>
    );
};

export default ImportProjectButton;
