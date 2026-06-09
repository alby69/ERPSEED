import React, { useState, useEffect } from 'react';
import { Drawer, Button, Spin, Typography } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiFetch } from '@/utils';
import './HelpDrawer.css';

const { Title } = Typography;

const HelpDrawer = ({ moduleName, moduleTitle }) => {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open || !moduleName) return;
    setLoading(true);
    setError(null);
    apiFetch(`/api/v1/tutorials/${moduleName}`)
      .then(res => {
        if (!res.ok) throw new Error('Tutorial non disponibile');
        return res.json();
      })
      .then(data => setContent(data.content))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [open, moduleName]);

  return (
    <>
      <Button
        type="text"
        icon={<QuestionCircleOutlined />}
        onClick={() => setOpen(true)}
        title="Guida"
      />
      <Drawer
        title={moduleTitle || 'Guida'}
        placement="right"
        width={560}
        onClose={() => setOpen(false)}
        open={open}
      >
        {loading && (
          <div style={{ textAlign: 'center', padding: 48 }}>
            <Spin size="large" />
          </div>
        )}
        {error && <Typography.Text type="danger">{error}</Typography.Text>}
        {content && (
          <div className="help-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </Drawer>
    </>
  );
};

export default HelpDrawer;
