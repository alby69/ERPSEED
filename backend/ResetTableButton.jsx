import React, { useState } from 'react';
import { Button, Popconfirm, message } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '../utils/api';

const ResetTableButton = ({ modelId, onSuccess }) => {
    const [loading, setLoading] = useState(false);

    const handleReset = async () => {
        setLoading(true);
        try {
            const response = await apiFetch(`/sys-models/${modelId}/reset-table`, {
                method: 'POST',
            });

            if (response.ok) {
                const data = await response.json();
                message.success(data.message || 'Tabella resettata con successo.');
                if (onSuccess) onSuccess();
            } else {
                const error = await response.json();
                message.error(error.message || 'Errore durante il reset della tabella.');
            }
        } catch (error) {
            message.error('Errore di connessione.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Popconfirm
            title="Sei sicuro di voler resettare la tabella?"
            description={
                <div>
                    <p>Verrà creato un backup automatico dei dati in formato CSV.</p>
                    <p>Questa azione <b>ELIMINERÀ TUTTI I DATI</b> presenti nella tabella.</p>
                    <p>La tabella verrà ricreata vuota basandosi sulla definizione attuale.</p>
                    <p>L'operazione è irreversibile.</p>
                </div>
            }
            onConfirm={handleReset}
            okText="Sì, Resetta"
            cancelText="Annulla"
            icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
            okButtonProps={{ danger: true }}
        >
            <Button danger type="primary" loading={loading}>
                Reset Table
            </Button>
        </Popconfirm>
    );
};

export default ResetTableButton;