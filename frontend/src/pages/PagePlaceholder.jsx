import React from 'react';
import { Card, Typography, Tag } from 'antd';
import { useParams } from 'react-router-dom'; // No date fields in this page
import { ToolOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const PagePlaceholder = ({ title, moduleName, priority, backend }) => {
    const { projectId } = useParams();

    return (
        <div style={{ padding: 24 }}>
            <Card>
                <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                    <ToolOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 20 }} />
                    <Title level={3}>{title || moduleName || 'In costruzione'}</Title>
                    <Paragraph type="secondary">
                        Questo modulo è in fase di implementazione.
                    </Paragraph>
                    {priority && <Tag color={priority === 'P0' ? 'red' : priority === 'P1' ? 'orange' : 'blue'}>{priority}</Tag>}
                    {backend && <Tag color="purple" style={{ marginLeft: 8 }}>{backend}</Tag>}
                    {projectId && <Paragraph type="secondary" style={{ marginTop: 16 }}>Progetto: {projectId}</Paragraph>}
                </div>
            </Card>
        </div>
    );
};

export default PagePlaceholder;
