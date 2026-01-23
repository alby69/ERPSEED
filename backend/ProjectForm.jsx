import React, { useEffect } from 'react';
import { Form, Input, Button, message } from 'antd';
import { apiFetch } from '../utils/api';

const ProjectForm = ({ project, onSuccess, onCancel }) => {
    const [form] = Form.useForm();

    useEffect(() => {
        if (project) {
            form.setFieldsValue(project);
        } else {
            form.resetFields();
        }
    }, [project, form]);

    const onFinish = async (values) => {
        const method = project ? 'PUT' : 'POST';
        const url = project ? `/projects/${project.id}` : '/projects';

        try {
            const response = await apiFetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(values),
            });

            if (response.ok) {
                message.success(`Progetto ${project ? 'aggiornato' : 'creato'} con successo`);
                onSuccess();
            } else {
                const errorData = await response.json();
                message.error(errorData.message || `Errore nel ${project ? 'aggiornare' : 'creare'} il progetto.`);
            }
        } catch (error) {
            message.error('Si è verificato un errore durante il salvataggio del progetto.');
        }
    };

    return (
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ name: '', title: '', description: '', version: '1.0.0' }}>
            <Form.Item
                name="name"
                label="Nome Interno"
                rules={[
                    { required: true, message: 'Per favore, inserisci il nome interno!' },
                    { pattern: /^[a-z0-9_]+$/, message: 'Solo lettere minuscole, numeri e underscore sono permessi.' }
                ]}
                help="Usato per riferimenti interni (es. fleet_management)."
            >
                <Input disabled={!!project} />
            </Form.Item>
            <Form.Item
                name="title"
                label="Titolo Visibile"
                rules={[{ required: true, message: 'Per favore, inserisci il titolo!' }]}
                help="Il nome mostrato nell'interfaccia utente."
            >
                <Input />
            </Form.Item>
            <Form.Item
                name="version"
                label="Versione"
                rules={[{ required: true, message: 'Inserisci la versione!' }]}
            >
                <Input placeholder="1.0.0" />
            </Form.Item>
            <Form.Item name="description" label="Descrizione">
                <Input.TextArea rows={4} />
            </Form.Item>
            <Form.Item style={{ textAlign: 'right' }}>
                <Button onClick={onCancel} style={{ marginRight: 8 }}>Annulla</Button>
                <Button type="primary" htmlType="submit">{project ? 'Aggiorna' : 'Crea'}</Button>
            </Form.Item>
        </Form>
    );
};

export default ProjectForm;