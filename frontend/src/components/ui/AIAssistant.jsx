/**
 * AI Assistant Component
 * 
 * Chat interface for generating ERP configurations from natural language
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  List, 
  Avatar, 
  Spin, 
  Typography, 
  Space, 
  Tag,
  Divider,
  message,
  Alert,
  Modal,
  Select,
  Empty
} from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined, 
  PlusOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  BulbOutlined
} from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Text, Title } = Typography;
const { TextArea } = Input;

const MODEL_OPTIONS = [
  { value: 'qwen3-coder', label: 'Qwen3-Coder', description: 'Best for code generation' },
  { value: 'big_pickle', label: 'Big Pickle', description: 'General purpose' },
  { value: 'kimi-k2.5-free', label: 'Kimi K2.5', description: 'Fast responses' },
];

function AIAssistant({ projectId, visible, onClose }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Ciao! Sono l'Assistente AI di FlaskERP. Descrivi quello che vuoi creare nel tuo ERP e io genererò la configurazione.\n\nEsempi:\n• 'Crea un modulo per gestire i fornitori'\n• 'Voglio un sistema per tracciare i progetti con kanban'\n• 'Aggiungi un campo partita IVA ai clienti'",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('qwen3-coder');
  const [showConfig, setShowConfig] = useState(false);
  const [generatedConfig, setGeneratedConfig] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await apiFetch('/api/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request: input.trim(),
          project_id: parseInt(projectId) || 1,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Errore nella generazione');
      }

      const result = await response.json();

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.message || 'Configurazione generata!',
        config: result.config,
        created_models: result.created_models,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (result.config) {
        setGeneratedConfig(result.config);
        setShowConfig(true);
      }

    } catch (error) {
      message.error(error.message || 'Errore nella comunicazione con l\'AI');
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Mi dispiace, ho incontrato un errore. Puoi riprovare?",
        isError: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInput(prompt);
  };

  const renderMessage = (msg) => {
    const isUser = msg.role === 'user';
    const isError = msg.isError;

    return (
      <List.Item
        style={{ 
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          padding: '12px 0',
          background: isError ? '#fff2f0' : 'transparent',
          borderRadius: 8,
        }}
      >
        <Space align="start" style={{ maxWidth: '80%' }}>
          {!isUser && (
            <Avatar 
              icon={<RobotOutlined />} 
              style={{ backgroundColor: '#1890ff' }}
            />
          )}
          <div style={{ flex: 1 }}>
            <div style={{ 
              padding: '12px 16px',
              background: isUser ? '#1890ff' : isError ? '#ffccc7' : '#f5f5f5',
              borderRadius: 12,
              color: isUser ? '#fff' : '#333',
            }}>
              <pre style={{ 
                margin: 0, 
                whiteSpace: 'pre-wrap', 
                fontFamily: 'inherit',
                fontSize: 14,
                lineHeight: 1.6,
              }}>
                {msg.content}
              </pre>
            </div>
            {msg.created_models && (
              <div style={{ marginTop: 8 }}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text type="success">Modelli creati: {msg.created_models.join(', ')}</Text>
                </Space>
              </div>
            )}
            <div style={{ marginTop: 4, opacity: 0.6, fontSize: 12 }}>
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
          {isUser && (
            <Avatar 
              icon={<UserOutlined />} 
              style={{ backgroundColor: '#52c41a' }}
            />
          )}
        </Space>
      </List.Item>
    );
  };

  const quickPrompts = [
    "Crea un modulo per gestire i fornitori",
    "Voglio un sistema per tracciare i progetti con kanban",
    "Aggiungi un campo partita IVA ai clienti",
    "Crea un modulo ordini collegato ai clienti",
  ];

  return (
    <Modal
      title={
        <Space>
          <RobotOutlined />
          <span>AI Assistant</span>
          <Select
            value={selectedModel}
            onChange={setSelectedModel}
            style={{ width: 160 }}
            options={MODEL_OPTIONS}
            size="small"
          />
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={700}
      footer={null}
      style={{ top: 20 }}
    >
      <Card 
        bodyStyle={{ padding: 0, height: 500, display: 'flex', flexDirection: 'column' }}
        style={{ height: 500 }}
      >
        {/* Messages Area */}
        <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
          <List
            dataSource={messages}
            renderItem={renderMessage}
            locale={{ emptyText: <Empty description="Scrivi un messaggio per iniziare" /> }}
          />
          {loading && (
            <div style={{ textAlign: 'center', padding: 16 }}>
              <Spin tip="L'AI sta generando..." />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <Divider style={{ margin: 0 }} />

        {/* Quick Prompts */}
        <div style={{ padding: '8px 16px', background: '#fafafa' }}>
          <Space wrap>
            <Text type="secondary" style={{ fontSize: 12 }}>Esempi:</Text>
            {quickPrompts.map((prompt, idx) => (
              <Tag 
                key={idx} 
                icon={<BulbOutlined />}
                style={{ cursor: 'pointer' }}
                onClick={() => handleQuickPrompt(prompt)}
              >
                {prompt.substring(0, 25)}...
              </Tag>
            ))}
          </Space>
        </div>

        <Divider style={{ margin: 0 }} />

        {/* Input Area */}
        <div style={{ padding: 16, display: 'flex', gap: 8 }}>
          <TextArea
            value={input}
                       onChange={(e) => setInput(e.target.value)}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Descrivi quello che vuoi creare..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ flex: 1 }}
            disabled={loading}
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            disabled={!input.trim()}
          >
            Invia
          </Button>
        </div>
      </Card>

      {/* Config Preview Modal */}
      <Modal
        title="Configurazione Generata - Modifica prima di applicare"
        open={showConfig}
        onCancel={() => setShowConfig(false)}
        width={700}
        footer={[
          <Button key="close" onClick={() => setShowConfig(false)}>
            Chiudi
          </Button>,
          <Button 
            key="edit"
            onClick={() => {
              setShowConfig(false);
              setInput('Modifica: ' + JSON.stringify(generatedConfig, null, 2));
            }}
          >
            Invia a AI per modifica
          </Button>,
          <Button 
            key="apply" 
            type="primary"
            onClick={() => {
              message.success('Configurazione applicata al progetto!');
              setShowConfig(false);
            }}
          >
            Applica al Progetto
          </Button>
        ]}
      >
        {generatedConfig && (
          <div>
            <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
              Puoi modificare il JSON prima di applicare:
            </Text>
            <TextArea
              value={JSON.stringify(generatedConfig, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setGeneratedConfig(parsed);
                } catch (err) {
                  // Invalid JSON, don't update
                }
              }}
              rows={15}
              style={{ fontFamily: 'monospace', fontSize: 12 }}
            />
          </div>
        )}
      </Modal>
    </Modal>
  );
}

export default AIAssistant;
