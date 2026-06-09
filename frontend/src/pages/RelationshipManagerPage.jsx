import React, { useState, useCallback, useEffect, memo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, Handle, Position, useNodesState, useEdgesState, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, Tabs, Table, Button, Tag, Space, Modal, Form, Select, Tooltip, Spin, message, Drawer, Input } from 'antd';
import { ScanOutlined, PlusOutlined, DeleteOutlined, ReloadOutlined, ApartmentOutlined, DatabaseOutlined, LinkOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';

const COLORS = {
  model: { bg: '#e6f4ff', border: '#1677ff', headerBg: '#1677ff', headerText: '#fff' },
  block: { bg: '#f6ffed', border: '#52c41a', headerBg: '#52c41a', headerText: '#fff' },
};

const ModelNode = memo(({ data, selected }) => {
  const colors = COLORS[data.nodeType] || COLORS.model;
  return (
    <div style={{
      background: colors.bg,
      border: `2px solid ${selected ? colors.border : '#d9d9d9'}`,
      borderRadius: 8,
      minWidth: 220,
      maxWidth: 280,
      boxShadow: selected ? `0 0 0 2px ${colors.border}40` : '0 1px 4px rgba(0,0,0,0.08)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontSize: 12,
    }}>
      <Handle type="target" position={Position.Top} style={{ background: colors.border }} />
      <div style={{
        background: colors.headerBg,
        color: colors.headerText,
        padding: '6px 12px',
        borderRadius: '6px 6px 0 0',
        fontWeight: 600,
        fontSize: 13,
        display: 'flex',
        alignItems: 'center',
        gap: 6,
      }}>
        {data.nodeType === 'block' ? <ApartmentOutlined /> : <DatabaseOutlined />}
        {data.label}
      </div>
      <div style={{ padding: '6px 12px 8px' }}>
        {data.nodeType === 'model' && (
          <div style={{ color: '#888', fontSize: 10, marginBottom: 4 }}>
            {data.table_name}
          </div>
        )}
        {data.fields && data.fields.slice(0, 8).map(f => (
          <div key={f.id} style={{
            display: 'flex',
            justifyContent: 'space-between',
            padding: '2px 0',
            borderBottom: '1px solid #f0f0f0',
            fontSize: 11,
          }}>
            <span style={{ color: f.type === 'many2one' || f.type === 'one2many' || f.type === 'many2many' ? colors.border : '#333', fontWeight: f.type === 'many2one' ? 600 : 400 }}>
              {f.technical_name}
            </span>
            <Tag style={{ fontSize: 9, lineHeight: '16px', padding: '0 4px', margin: 0 }}>{f.type}</Tag>
          </div>
        ))}
        {data.fields && data.fields.length > 8 && (
          <div style={{ color: '#999', fontSize: 10, textAlign: 'center', marginTop: 4 }}>
            +{data.fields.length - 8} more fields
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: colors.border }} />
    </div>
  );
});

const nodeTypes = { model: ModelNode, block: ModelNode };

function applySimpleLayout(nodes, edges) {
  const modelNodes = nodes.filter(n => n.type === 'model');
  const blockNodes = nodes.filter(n => n.type === 'block');
  let idx = 0;
  const cols = 4;
  const xGap = 300;
  const yGap = 80;

  modelNodes.forEach(n => {
    const col = idx % cols;
    const row = Math.floor(idx / cols);
    n.position = { x: col * xGap, y: row * yGap };
    idx++;
  });

  blockNodes.forEach(n => {
    const col = idx % cols;
    const row = Math.floor(idx / cols);
    n.position = { x: col * xGap, y: row * yGap };
    idx++;
  });

  return { layoutedNodes: nodes, layoutedEdges: edges };
}

const RelationshipManagerPage = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [models, setModels] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [relLoading, setRelLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [createForm] = Form.useForm();
  const [selectedNode, setSelectedNode] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await apiFetch('/api/v1/relationship-manager/graph');
      const data = await resp.json();
      const graphNodes = (data.nodes || []).map(n => ({
        id: n.id,
        type: 'model',
        position: { x: 0, y: 0 },
        data: { ...n, nodeType: n.type },
      }));
      const graphEdges = (data.edges || []).map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        type: 'smoothstep',
        animated: e.type === 'block_dependency',
        style: {
          stroke: e.type === 'block_dependency' ? '#52c41a' : '#1677ff',
          strokeWidth: e.type === 'block_dependency' ? 2 : 1.5,
          strokeDasharray: e.type === 'block_dependency' ? '5 5' : undefined,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: e.type === 'block_dependency' ? '#52c41a' : '#1677ff',
        },
        labelStyle: { fontSize: 10, fontWeight: 600 },
        labelBgStyle: { fill: '#fff', fillOpacity: 0.8 },
      }));
      const { layoutedNodes } = applySimpleLayout(graphNodes, graphEdges);
      setNodes(layoutedNodes);
      setEdges(graphEdges);
    } catch (err) {
      message.error('Error loading graph data');
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  const fetchModels = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/v1/relationship-manager/models');
      const data = await resp.json();
      setModels(data.models || []);
    } catch (err) {
      message.error('Error loading models');
    }
  }, []);

  const fetchRelationships = useCallback(async () => {
    setRelLoading(true);
    try {
      const resp = await apiFetch('/api/v1/relationship-manager/relationships');
      const data = await resp.json();
      setRelationships(data.items || []);
    } catch (err) {
      message.error('Error loading relationships');
    } finally {
      setRelLoading(false);
    }
  }, []);

  const handleScan = async () => {
    setScanning(true);
    try {
      const resp = await apiFetch('/api/v1/relationship-manager/scan', { method: 'POST' });
      const result = await resp.json();
      message.success(`Scansione completata: ${result.models_created} modelli, ${result.fields_created} campi, ${result.relations_found} relazioni`);
      fetchGraph();
      fetchRelationships();
    } catch (err) {
      message.error('Error during scan');
    } finally {
      setScanning(false);
    }
  };

  const handleDelete = async (relId) => {
    try {
      await apiFetch(`/api/v1/relationship-manager/relationships/${relId}`, { method: 'DELETE' });
      message.success('Relazione eliminata');
      fetchRelationships();
      fetchGraph();
    } catch (err) {
      message.error('Error deleting relationship');
    }
  };

  const handleCreate = async () => {
    try {
      const values = await createForm.validateFields();
      const payload = {
        source_type: values.source_type,
        source_id: values.source_id,
        source_field_id: values.source_field_id || null,
        target_type: values.target_type,
        target_id: values.target_id,
        rel_type: values.rel_type,
        name: values.name,
        technical_name: values.technical_name,
        title: values.title,
      };
      await apiFetch('/api/v1/relationship-manager/relationships', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      message.success('Relazione creata');
      setCreateModalOpen(false);
      createForm.resetFields();
      fetchRelationships();
      fetchGraph();
    } catch (err) {
      if (err.errorFields) return;
      message.error('Error creating relationship');
    }
  };

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
    setDrawerOpen(true);
  }, []);

  useEffect(() => {
    fetchGraph();
    fetchRelationships();
    fetchModels();
  }, [fetchGraph, fetchRelationships, fetchModels]);

  const relColumns = [
    { title: 'Tipo', dataIndex: 'type', key: 'type', width: 100,
      render: (t) => <Tag color={t === 'block' ? 'green' : 'blue'}>{t === 'block' ? 'Blocco' : 'Campo'}</Tag>
    },
    { title: 'Sorgente', dataIndex: 'source_label', key: 'source', width: 200 },
    { title: 'Campo Sorgente', dataIndex: 'source_field_label', key: 'source_field', width: 150,
      render: (v) => v || '-' },
    { title: 'Tipo Relazione', dataIndex: 'rel_type', key: 'rel_type', width: 130,
      render: (t) => <Tag>{t}</Tag>
    },
    { title: 'Target', dataIndex: 'target_label', key: 'target', width: 200 },
    { title: '', key: 'actions', width: 80,
      render: (_, record) => (
        <Button type="text" danger icon={<DeleteOutlined />}
          onClick={() => handleDelete(record.id)} />
      ),
    },
  ];

  const tabItems = [
    {
      key: 'er-diagram',
      label: <span><ApartmentOutlined /> ER Diagram</span>,
      children: (
        <div style={{ height: 600, border: '1px solid #f0f0f0', borderRadius: 8, position: 'relative' }}>
          {loading && <Spin style={{ position: 'absolute', top: '50%', left: '50%', zIndex: 10 }} />}
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
          >
            <Controls />
            <MiniMap
              nodeStrokeWidth={3}
              nodeColor={(n) => COLORS[n.data?.nodeType]?.border || '#1677ff'}
              style={{ height: 120 }}
            />
            <Background gap={16} size={1} />
          </ReactFlow>
        </div>
      ),
    },
    {
      key: 'relationships',
      label: <span><LinkOutlined /> Relazioni</span>,
      children: (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>
              Nuova Relazione
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => { fetchRelationships(); fetchGraph(); }}>
              Aggiorna
            </Button>
          </div>
          <Table
            dataSource={relationships}
            columns={relColumns}
            rowKey="id"
            loading={relLoading}
            size="small"
            pagination={{ pageSize: 20 }}
          />
        </div>
      ),
    },
  ];

  const modelOptions = models.filter(m => m.type !== 'block').map(m => ({
    label: `${m.title} (${m.table_name || ''})`,
    value: m.id,
  }));

  const blockOptions = models.filter(m => m.type === 'block').map(m => ({
    label: m.title || m.name,
    value: m.id,
  }));

  return (
    <div style={{ padding: 24 }}>
      <Card
        title={
          <Space>
            <ApartmentOutlined />
            <span>Relationship Manager</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ScanOutlined />} onClick={handleScan} loading={scanning}>
              Scansiona Modelli Statici
            </Button>
          </Space>
        }
      >
        <Tabs items={tabItems} />
      </Card>

      <Modal
        title="Nuova Relazione"
        open={createModalOpen}
        onOk={handleCreate}
        onCancel={() => { setCreateModalOpen(false); createForm.resetFields(); }}
        width={500}
      >
        <Form form={createForm} layout="vertical">
          <Form.Item name="source_type" label="Tipo Sorgente" rules={[{ required: true }]}>
            <Select options={[
              { label: 'Modello (SysModel)', value: 'model' },
              { label: 'Blocco (Block)', value: 'block' },
            ]} />
          </Form.Item>
          <Form.Item noStyle shouldUpdate={(prev, cur) => prev.source_type !== cur.source_type}>
            {({ getFieldValue }) => {
              const st = getFieldValue('source_type');
              const opts = st === 'block' ? blockOptions : modelOptions;
              return (
                <Form.Item name="source_id" label="Sorgente" rules={[{ required: true }]}>
                  <Select showSearch optionFilterProp="label" options={opts} />
                </Form.Item>
              );
            }}
          </Form.Item>
          <Form.Item name="source_field_id" label="Campo Sorgente (opzionale)">
            <Select allowClear
              options={(models.find(m => m.id === createForm.getFieldValue('source_id') && m.type !== 'block')?.fields || []).map(f => ({
                label: `${f.technical_name} (${f.type})`,
                value: f.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="rel_type" label="Tipo Relazione" rules={[{ required: true }]}>
            <Select options={[
              { label: 'many2one', value: 'many2one' },
              { label: 'one2many', value: 'one2many' },
              { label: 'many2many', value: 'many2many' },
              { label: 'requires (blocco)', value: 'requires' },
              { label: 'recommends (blocco)', value: 'recommends' },
              { label: 'conflicts (blocco)', value: 'conflicts' },
            ]} />
          </Form.Item>
          <Form.Item name="target_type" label="Tipo Target" rules={[{ required: true }]}>
            <Select options={[
              { label: 'Modello (SysModel)', value: 'model' },
              { label: 'Blocco (Block)', value: 'block' },
            ]} />
          </Form.Item>
          <Form.Item noStyle shouldUpdate={(prev, cur) => prev.target_type !== cur.target_type}>
            {({ getFieldValue }) => {
              const tt = getFieldValue('target_type');
              const opts = tt === 'block' ? blockOptions : modelOptions;
              return (
                <Form.Item name="target_id" label="Target" rules={[{ required: true }]}>
                  <Select showSearch optionFilterProp="label" options={opts} />
                </Form.Item>
              );
            }}
          </Form.Item>
          <Form.Item name="name" label="Nome (opzionale, solo per nuovi campi)">
            <Input placeholder="e.g. categoria_id" />
          </Form.Item>
          <Form.Item name="title" label="Titolo (opzionale)">
            <Input placeholder="e.g. Categoria" />
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title={selectedNode?.data?.label || 'Dettaglio'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={400}
      >
        {selectedNode && (
          <div>
            <p><strong>Tipo:</strong> {selectedNode.data?.nodeType === 'block' ? 'Blocco' : 'Modello'}</p>
            {selectedNode.data?.table_name && (
              <p><strong>Tabella:</strong> {selectedNode.data.table_name}</p>
            )}
            <p><strong>Origine:</strong> {selectedNode.data?.origin === 'scanned' ? 'Scansionato' : 'Dinamico'}</p>
            {selectedNode.data?.fields && (
              <div>
                <h4>Campi ({selectedNode.data.fields.length})</h4>
                {selectedNode.data.fields.map(f => (
                  <div key={f.id} style={{ padding: '4px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <Space>
                      <Tag color={['many2one','one2many','many2many'].includes(f.type) ? 'blue' : 'default'}>{f.type}</Tag>
                      <strong>{f.technical_name}</strong>
                    </Space>
                    {f.relation_model && (
                      <div style={{ fontSize: 11, color: '#888', marginLeft: 4 }}>
                        → {f.relation_model}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default RelationshipManagerPage;
