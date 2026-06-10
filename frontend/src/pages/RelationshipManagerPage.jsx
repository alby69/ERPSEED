import React, { useState, useCallback, useEffect, useMemo, memo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, Handle, Position, useNodesState, useEdgesState, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, Tabs, Table, Button, Tag, Space, Modal, Form, Select, Tooltip, Spin, message, Drawer, Input, Empty, Badge } from 'antd';
import { ScanOutlined, PlusOutlined, DeleteOutlined, ReloadOutlined, ApartmentOutlined, DatabaseOutlined, LinkOutlined, SearchOutlined, ClearOutlined } from '@ant-design/icons';
import { apiFetch } from '@/utils';
import { useTheme } from '@/context';
import { useColumnManagerWithDrawer } from '@/hooks/useColumnManager';
import ColumnSettingsButton from '@/components/ColumnSettingsButton';

const BASE_COLORS = {
  model: { bg: '#e6f4ff', border: '#1677ff', headerBg: '#1677ff', headerText: '#fff' },
  block: { bg: '#f6ffed', border: '#52c41a', headerBg: '#52c41a', headerText: '#fff' },
};

const ModelNode = memo(({ data, selected }) => {
  const colors = data._colors || BASE_COLORS[data.nodeType] || BASE_COLORS.model;
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

  const COLS = 5;
  const X_GAP = 320;
  const Y_GAP = 100;
  const SECTION_GAP = 120;

  modelNodes.forEach((n, idx) => {
    const col = idx % COLS;
    const row = Math.floor(idx / COLS);
    n.position = { x: col * X_GAP, y: row * Y_GAP };
  });

  blockNodes.forEach((n, idx) => {
    const col = idx % COLS;
    const row = Math.floor(idx / COLS);
    n.position = { x: col * X_GAP, y: row * Y_GAP + SECTION_GAP };
  });

  return { layoutedNodes: nodes, layoutedEdges: edges };
}

const RelationshipManagerPage = () => {
  const { themeConfig } = useTheme();
  const primaryColor = themeConfig?.primaryColor || '#1677ff';

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
  const [searchFilter, setSearchFilter] = useState('');

  const COLORS = useMemo(() => ({
    model: { bg: `${primaryColor}15`, border: primaryColor, headerBg: primaryColor, headerText: '#fff' },
    block: { bg: '#f6ffed', border: '#52c41a', headerBg: '#52c41a', headerText: '#fff' },
  }), [primaryColor]);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await apiFetch('/api/v1/relationship-manager/graph');
      const data = await resp.json();
      const graphNodes = (data.nodes || []).map(n => ({
        id: n.id,
        type: 'model',
        position: { x: 0, y: 0 },
        data: { ...n, nodeType: n.type, _colors: n.type === 'block' ? COLORS.block : COLORS.model },
      }));
      const graphEdges = (data.edges || []).map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        type: 'smoothstep',
        animated: e.type === 'block_dependency',
        style: {
          stroke: e.type === 'block_dependency' ? '#52c41a' : primaryColor,
          strokeWidth: e.type === 'block_dependency' ? 2 : 1.5,
          strokeDasharray: e.type === 'block_dependency' ? '5 5' : undefined,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: e.type === 'block_dependency' ? '#52c41a' : primaryColor,
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
  }, [setNodes, setEdges, COLORS, primaryColor]);

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

  const filteredNodes = useMemo(() => {
    if (!searchFilter) return nodes;
    const q = searchFilter.toLowerCase();
    return nodes.filter(n =>
      n.data?.label?.toLowerCase().includes(q) ||
      n.data?.table_name?.toLowerCase().includes(q) ||
      n.data?.fields?.some(f => f.technical_name?.toLowerCase().includes(q))
    );
  }, [nodes, searchFilter]);

  const nodeRelationships = useMemo(() => {
    if (!selectedNode) return { incoming: [], outgoing: [] };
    const nodeId = selectedNode.id;
    return {
      outgoing: edges.filter(e => e.source === nodeId),
      incoming: edges.filter(e => e.target === nodeId),
    };
  }, [selectedNode, edges]);

  useEffect(() => {
    fetchGraph();
    fetchRelationships();
    fetchModels();
  }, [fetchGraph, fetchRelationships, fetchModels]);

  const rawRelColumns = [
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
  const colManager = useColumnManagerWithDrawer('relationship_manager', rawRelColumns);

  const tabItems = [
    {
      key: 'er-diagram',
      label: <span><ApartmentOutlined /> ER Diagram</span>,
      children: (
        <div>
          <div style={{ marginBottom: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
            <Input.Search
              placeholder="Cerca modello o campo..."
              allowClear
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
              onSearch={setSearchFilter}
              style={{ width: 320 }}
              prefix={<SearchOutlined style={{ color: '#999' }} />}
            />
            <div style={{ flex: 1 }} />
            <Space size={4}>
              <Badge color={COLORS.model.border} text={<span style={{ fontSize: 12 }}>Modello</span>} />
              <Badge color={COLORS.block.border} text={<span style={{ fontSize: 12 }}>Blocco</span>} />
            </Space>
          </div>
          <div style={{ height: 560, border: '1px solid #f0f0f0', borderRadius: 8, position: 'relative' }}>
            {loading && <Spin style={{ position: 'absolute', top: '50%', left: '50%', zIndex: 10 }} />}
            {!loading && filteredNodes.length === 0 && (
              <Empty description="Nessun nodo trovato" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
            )}
            <ReactFlow
              nodes={filteredNodes}
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
                nodeColor={(n) => COLORS[n.data?.nodeType]?.border || primaryColor}
                style={{ height: 120 }}
              />
              <Background gap={16} size={1} />
            </ReactFlow>
          </div>
        </div>
      ),
    },
    {
      key: 'relationships',
      label: <span><LinkOutlined /> Relazioni</span>,
      children: (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <ColumnSettingsButton manager={colManager} />
            <Button type="primary" icon={<PlusOutlined />} style={{ background: primaryColor, borderColor: primaryColor }} onClick={() => setCreateModalOpen(true)}>
              Nuova Relazione
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => { fetchRelationships(); fetchGraph(); }}>
              Aggiorna
            </Button>
          </div>
          <Table
            dataSource={relationships}
            columns={colManager.processedColumns}
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
    <div style={{ padding: 24, minHeight: '100%' }}>
      <Card
        title={
          <Space>
            <ApartmentOutlined style={{ color: primaryColor }} />
            <span style={{ fontWeight: 600 }}>Relationship Manager</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ScanOutlined />} onClick={handleScan} loading={scanning}>
              Scansiona Modelli Statici
            </Button>
          </Space>
        }
        styles={{ body: { padding: 16 } }}
      >
        <Tabs items={tabItems} />
      </Card>

      <Modal
        title={<span><PlusOutlined style={{ color: primaryColor }} /> Nuova Relazione</span>}
        open={createModalOpen}
        onOk={handleCreate}
        onCancel={() => { setCreateModalOpen(false); createForm.resetFields(); }}
        width={500}
        okButtonProps={{ style: { background: primaryColor, borderColor: primaryColor } }}
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
        title={<span style={{ color: primaryColor }}>{selectedNode?.data?.label || 'Dettaglio'}</span>}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={420}
      >
        {selectedNode && (
          <div>
            <Space direction="vertical" style={{ width: '100%' }} size={12}>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Tag color={selectedNode.data?.nodeType === 'block' ? 'green' : 'blue'} style={{ fontSize: 12, padding: '2px 8px' }}>
                  {selectedNode.data?.nodeType === 'block' ? 'Blocco' : 'Modello'}
                </Tag>
                {selectedNode.data?.origin && (
                  <Tag>{selectedNode.data?.origin === 'scanned' ? 'Scansionato' : 'Dinamico'}</Tag>
                )}
              </div>

              {selectedNode.data?.table_name && (
                <div>
                  <div style={{ fontSize: 11, color: '#999', marginBottom: 2 }}>TABELLA</div>
                  <code style={{ fontSize: 13 }}>{selectedNode.data.table_name}</code>
                </div>
              )}

              {selectedNode.data?.fields && (
                <div>
                  <div style={{ fontSize: 11, color: '#999', marginBottom: 6 }}>
                    CAMPI ({selectedNode.data.fields.length})
                  </div>
                  <div style={{ maxHeight: 260, overflow: 'auto' }}>
                    {selectedNode.data.fields.map(f => (
                      <div key={f.id} style={{ padding: '5px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Space>
                          <Tag color={['many2one','one2many','many2many'].includes(f.type) ? 'blue' : 'default'} style={{ margin: 0 }}>{f.type}</Tag>
                          <strong style={{ fontSize: 12 }}>{f.technical_name}</strong>
                        </Space>
                        {f.relation_model && (
                          <div style={{ fontSize: 11, color: '#888', marginLeft: 4, marginTop: 2 }}>
                            → {f.relation_model}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(nodeRelationships.incoming.length > 0 || nodeRelationships.outgoing.length > 0) && (
                <div>
                  <div style={{ fontSize: 11, color: '#999', marginBottom: 6 }}>RELAZIONI</div>
                  {nodeRelationships.outgoing.length > 0 && (
                    <div style={{ marginBottom: 8 }}>
                      <div style={{ fontSize: 11, color: '#52c41a', marginBottom: 4 }}>In uscita ({nodeRelationships.outgoing.length})</div>
                      {nodeRelationships.outgoing.map(e => (
                        <div key={e.id} style={{ fontSize: 12, padding: '2px 0', display: 'flex', gap: 4 }}>
                          <span>→</span>
                          <Tag style={{ fontSize: 10 }}>{e.label || e.id}</Tag>
                          <span style={{ color: '#888' }}>{e.target}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {nodeRelationships.incoming.length > 0 && (
                    <div>
                      <div style={{ fontSize: 11, color: primaryColor, marginBottom: 4 }}>In entrata ({nodeRelationships.incoming.length})</div>
                      {nodeRelationships.incoming.map(e => (
                        <div key={e.id} style={{ fontSize: 12, padding: '2px 0', display: 'flex', gap: 4 }}>
                          <span>←</span>
                          <Tag style={{ fontSize: 10 }}>{e.label || e.id}</Tag>
                          <span style={{ color: '#888' }}>{e.source}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Space>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default RelationshipManagerPage;
