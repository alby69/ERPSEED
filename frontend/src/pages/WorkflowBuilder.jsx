import React, { useState, useCallback, useEffect } from 'react';
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Card, Button, Input, Select, Space, message,
  Drawer, List, Tag, Modal, Spin, Divider
} from 'antd';
import {
  SaveOutlined, PlayCircleOutlined, PlusOutlined,
  FunctionOutlined, ApiOutlined, BellOutlined,
  ClockCircleOutlined, ArrowLeftOutlined, UnorderedListOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { apiFetch } from '../utils';
import { useWorkflowBuilderStore } from '../stores/workflowBuilderStore';
import { nodeTypes } from '../components/workflow/WorkflowNodes';
import WorkflowPropertiesPanel from '../components/workflow/WorkflowPropertiesPanel';
import ImportExportToolbar from '../components/ui/ImportExportToolbar';
import ImportExportContextMenu from '../components/ui/ImportExportContextMenu';
import { useTheme } from '../context';

const { Option } = Select;

const triggerOptions = [
  { value: 'order.created', label: 'Ordine creato' },
  { value: 'order.updated', label: 'Ordine aggiornato' },
  { value: 'order.deleted', label: 'Ordine eliminato' },
  { value: 'invoice.created', label: 'Fattura creata' },
  { value: 'invoice.updated', label: 'Fattura aggiornata' },
  { value: 'product.created', label: 'Prodotto creato' },
  { value: 'product.updated', label: 'Prodotto aggiornato' },
  { value: 'user.created', label: 'Utente creato' },
  { value: 'entity.created', label: 'Qualsiasi entità creata' },
  { value: 'entity.updated', label: 'Qualsiasi entità aggiornata' },
  { value: '*', label: 'Qualsiasi evento' },
];

const toolboxItems = [
  { type: 'condition', label: 'Condizione', icon: <FunctionOutlined />, color: '#722ed1' },
  { type: 'action', label: 'Azione', icon: <ApiOutlined />, color: '#52c41a' },
  { type: 'notification', label: 'Notifica', icon: <BellOutlined />, color: '#fa8c16' },
  { type: 'delay', label: 'Ritardo', icon: <ClockCircleOutlined />, color: '#eb2f96' },
  { type: 'webhook', label: 'Webhook', icon: <ApiOutlined />, color: '#13c2c2' },
];

const WorkflowBuilder = () => {
  const { themeConfig } = useTheme();
  const { projectId, workflowId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showList, setShowList] = useState(false);
  const [workflows, setWorkflows] = useState([]);

  const {
    nodes,
    edges,
    triggerEvent,
    workflowName,
    workflowDescription,
    workflowId: currentWorkflowId,
    setWorkflowMeta,
    setTriggerEvent,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    selectNode,
    clearSelection,
    setNodes,
    setEdges,
    reset,
  } = useWorkflowBuilderStore();

  const fetchWorkflows = useCallback(async () => {
    try {
      const response = await apiFetch(`/workflows?projectId=${projectId || ''}`);
      const data = await response.json();
      setWorkflows(data);
    } catch {
      console.error('Error loading workflows');
    }
  }, [projectId]);

  const loadWorkflow = useCallback(async (id) => {
    setLoading(true);
    try {
      const [workflowResponse, canvasResponse] = await Promise.all([
        apiFetch(`/workflows/${id}`),
        apiFetch(`/workflows/${id}/canvas`),
      ]);
      const data = await workflowResponse.json();
      const canvas = await canvasResponse.json();

      setWorkflowMeta({
        id: data.id,
        name: data.name,
        description: data.description,
        triggerEvent: data.trigger_event,
      });

      setNodes(canvas.nodes || []);
      setEdges(canvas.edges || []);
    } catch {
      message.error('Error loading workflow');
    } finally {
      setLoading(false);
    }
  }, [setEdges, setNodes, setWorkflowMeta]);

  useEffect(() => {
    if (workflowId) {
      loadWorkflow(workflowId);
    } else {
      reset();
    }
    fetchWorkflows();
  }, [workflowId, fetchWorkflows, loadWorkflow, reset]);

  const handleSave = async () => {
    if (!workflowName) {
      message.error('Inserisci un nome per il workflow');
      return;
    }

    setSaving(true);
    try {
      const workflowPayload = {
        name: workflowName,
        description: workflowDescription,
        trigger_event: triggerEvent,
        projectId: projectId ? parseInt(projectId, 10) : null,
      };

      let savedWorkflowId = currentWorkflowId;
      if (savedWorkflowId) {
        await apiFetch(`/workflows/${savedWorkflowId}`, {
          method: 'PUT',
          body: JSON.stringify(workflowPayload),
        });
      } else {
        const response = await apiFetch('/workflows', {
          method: 'POST',
          body: JSON.stringify(workflowPayload),
        });

        const result = await response.json();
        savedWorkflowId = result.id;
        setWorkflowMeta({
          id: result.id,
          name: result.name,
          description: result.description,
          triggerEvent: result.trigger_event,
        });
      }

      await apiFetch(`/workflows/${savedWorkflowId}/canvas`, {
        method: 'PUT',
        body: JSON.stringify({
          nodes,
          edges,
        }),
      });

      message.success('Workflow salvato!');
      fetchWorkflows();
    } catch {
      message.error('Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    if (!currentWorkflowId) {
      message.warning('Salva prima il workflow');
      return;
    }

    try {
      const response = await apiFetch(`/workflows/${currentWorkflowId}/test`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.status === 'completed') {
        message.success('Workflow eseguito con successo!');
      } else {
        message.error(`Esecuzione fallita: ${data.error}`);
      }
    } catch {
      message.error('Errore nel test');
    }
  };

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    const reactFlowBounds = document.querySelector('.react-flow').getBoundingClientRect();
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    };

    addNode(type, position);
  }, [addNode]);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onNodeClick = useCallback((event, node) => {
    selectNode(node);
  }, [selectNode]);

  const onPaneClick = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  const openWorkflow = (id) => {
    navigate(`/projects/${projectId}/workflow-builder/${id}`);
    setShowList(false);
  };

  return (
    <Spin spinning={loading}>
    <div style={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <Card size="small" style={{ borderRadius: 0 }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/projects/${projectId}/workflows`)}
          >
            Indietro
          </Button>
          <Button
            icon={<UnorderedListOutlined />}
            onClick={() => setShowList(true)}
          >
            Lista Workflow
          </Button>
          <Divider type="vertical" />
          <Input
            placeholder="Nome workflow"
            value={workflowName}
            onChange={(e) => setWorkflowMeta({ name: e.target.value })}
            style={{ width: 200 }}
          />
          <Select
            value={triggerEvent}
            onChange={setTriggerEvent}
            style={{ width: 200 }}
          >
            {triggerOptions.map(o => (
              <Option key={o.value} value={o.value}>{o.label}</Option>
            ))}
          </Select>
          <Divider type="vertical" />
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
          >
            Salva
          </Button>
          <Button
            icon={<PlayCircleOutlined />}
            onClick={handleTest}
          >
            Test
          </Button>
          <Divider type="vertical" />
          <ImportExportToolbar
            type="workflow"
            projectId={projectId || localStorage.getItem('currentProjectId') || 1}
            showExport={false}
            showImport={true}
            importConfigLabel="Importa Workflow"
          />
        </Space>
      </Card>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ width: 80, background: themeConfig.mode === 'dark' ? '#1f1f1f' : '#fafafa', borderRight: themeConfig.mode === 'dark' ? '1px solid #303030' : '1px solid #f0f0f0', padding: 8 }}>
          <div style={{ textAlign: 'center', fontSize: 11, marginBottom: 8, color: themeConfig.mode === 'dark' ? 'rgba(255,255,255,0.45)' : '#666' }}>
            Toolbox
          </div>
          {toolboxItems.map(item => (
            <div
              key={item.type}
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData('application/reactflow', item.type);
                e.dataTransfer.effectAllowed = 'move';
              }}
              style={{
                padding: '8px 4px',
                marginBottom: 8,
                background: item.color,
                color: '#fff',
                borderRadius: 6,
                textAlign: 'center',
                cursor: 'grab',
                fontSize: 10,
              }}
            >
              <div style={{ fontSize: 16 }}>{item.icon}</div>
              <div>{item.label}</div>
            </div>
          ))}
        </div>

        <div style={{ flex: 1 }} onDrop={handleDrop} onDragOver={handleDragOver}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            snapToGrid
            snapGrid={[15, 15]}
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>

        <div style={{ width: 280, borderLeft: '1px solid #f0f0f0', overflow: 'auto' }}>
          <WorkflowPropertiesPanel />
        </div>
      </div>

      <Drawer
        title="Lista Workflow"
        placement="left"
        onClose={() => setShowList(false)}
        open={showList}
        width={400}
      >
        <List
          dataSource={workflows}
          renderItem={item => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => openWorkflow(item.id)}>
                  Apri
                </Button>
              ]}
            >
              <ImportExportContextMenu
                type="workflow"
                entityId={item.id}
                entityName={item.name}
                projectId={projectId || localStorage.getItem('currentProjectId') || 1}
                showExportConfig={true}
                showExportData={false}
              >
                <div style={{ cursor: 'context-menu', width: '100%' }}>
                  <List.Item.Meta
                    title={item.name}
                    description={
                      <Space>
                        <Tag color="blue">{item.trigger_event}</Tag>
                        <span>{item.steps_count} step</span>
                      </Space>
                    }
                  />
                </div>
              </ImportExportContextMenu>
            </List.Item>
          )}
        />
      </Drawer>
    </div>
    </Spin>
  );
};

export default WorkflowBuilder;
