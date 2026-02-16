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
                message.success(`Project ${project ? 'updated' : 'created'} successfully`);
                onSuccess();
            } else {
                const errorData = await response.json();
                message.error(errorData.message || `Error ${project ? 'updating' : 'creating'} the project.`);
            }
        } catch (error) {
            message.error('An error occurred while saving the project.');
        }
    };

    return (
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{ name: '', title: '', description: '', version: '1.0.0' }}>
            <Form.Item
                name="name"
                label="Internal Name"
                rules={[
                    { required: true, message: 'Please enter the internal name!' },
                    { pattern: /^[a-z0-9_]+$/, message: 'Only lowercase letters, numbers, and underscores are allowed.' }
                ]}
                help="Used for internal references (e.g., fleet_management)."
            >
                <Input disabled={!!project} />
            </Form.Item>
            <Form.Item
                name="title"
                label="Visible Title"
                rules={[{ required: true, message: 'Please enter the title!' }]}
                help="The name displayed in the user interface."
            >
                <Input />
            </Form.Item>
            <Form.Item
                name="version"
                label="Version"
                rules={[{ required: true, message: 'Please enter the version!' }]}
            >
                <Input placeholder="1.0.0" />
            </Form.Item>
            <Form.Item name="description" label="Description">
                <Input.TextArea rows={4} />
            </Form.Item>
            <Form.Item style={{ textAlign: 'right' }}>
                <Button onClick={onCancel} style={{ marginRight: 8 }}>Cancel</Button>
                <Button type="primary" htmlType="submit">{project ? 'Update' : 'Create'}</Button>
            </Form.Item>
        </Form>
    );
};

export default ProjectForm;
