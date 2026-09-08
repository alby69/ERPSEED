import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Form, Input, Button, Alert, Typography, Flex } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { BASE_URL } from '../utils';

const { Title } = Typography;

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/password/reset/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: values.password }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Password updated successfully! Redirecting to login...');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError(data.message || 'Error resetting password');
      }
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <Flex justify="center" align="center" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Card style={{ width: 400, textAlign: 'center' }}>
          <Alert message="Missing or invalid password reset token." type="error" showIcon />
        </Card>
      </Flex>
    );
  }

  return (
    <Flex justify="center" align="center" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <Title level={3} style={{ textAlign: 'center', marginBottom: 24 }}>
          New Password
        </Title>
        {message && <Alert message={message} type="success" showIcon style={{ marginBottom: 16 }} />}
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}
        <Form layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { required: true, message: 'Please enter your new password' },
              { min: 6, message: 'Password must be at least 6 characters' }
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Enter new password" size="large" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button type="primary" htmlType="submit" size="large" block loading={loading}>
              Save Password
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </Flex>
  );
}

export default ResetPassword;
