import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, message, Spin, Alert, Tabs, Space, Badge, Divider, Typography } from 'antd';
import { PlayCircleOutlined, PlusOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, WarningOutlined, HistoryOutlined, ExportOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components';
import { apiFetch } from '../utils';

const { Title, Text } = Typography;
const { Option } = Select;

function TestRunnerPage() {
    const [suites, setSuites] = useState([]);
    const [executions, setExecutions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [runningSuite, setRunningSuite] = useState(null);
    const [suiteModalOpen, setSuiteModalOpen] = useState(false);
    const [caseModalOpen, setCaseModalOpen] = useState(false);
    const [selectedSuite, setSelectedSuite] = useState(null);
    const [generateModalOpen, setGenerateModalOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('suites');
    const [form] = Form.useForm();
    const [caseForm] = Form.useForm();
    const [generateForm] = Form.useForm();
    const navigate = useNavigate();
    
    // Run All state
    const [runningAll, setRunningAll] = useState(false);
    const [runAllProgress, setRunAllProgress] = useState({ current: 0, total: 0, suiteName: '', status: '' });
    
    // Delete All state
    const [deleteAllModalVisible, setDeleteAllModalVisible] = useState(false);
    const [deletingAll, setDeletingAll] = useState(false);

    const statoColors = {
        bozza: 'default',
        in_test: 'processing',
        testato: 'warning',
        pubblicato: 'success',
        obsoleto: 'error'
    };

    const esitoColors = {
        successo: 'success',
        fallito: 'error',
        errore: 'warning',
        in_corso: 'processing'
    };

    useEffect(() => {
        fetchSuites();
        fetchExecutions();
    }, []);

    const fetchSuites = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await apiFetch('/api/v1/tests/suites', {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await response.json();
            setSuites(data.test_suites || []);
        } catch (error) {
            message.error('Errore nel caricamento test suites');
        } finally {
            setLoading(false);
        }
    };

    const fetchExecutions = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await apiFetch('/api/v1/tests/executions', {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await response.json();
            setExecutions(data.executions || []);
        } catch (error) {
            console.error('Errore nel caricamento executions');
        }
    };

    const handleCreateSuite = async (values) => {
        try {
            const token = localStorage.getItem('token');
            await apiFetch('/api/v1/tests/suites', {
                method: 'POST',
                body: JSON.stringify(values),
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
            });
            message.success('TestSuite creata!');
            setSuiteModalOpen(false);
            form.resetFields();
            fetchSuites();
        } catch (error) {
            message.error('Errore nella creazione');
        }
    };

    const handleGenerateSuite = async (values) => {
        try {
            const token = localStorage.getItem('token');
            await apiFetch('/api/v1/tests/generate', {
                method: 'POST',
                body: JSON.stringify(values),
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
            });
            message.success('TestSuite generata automaticamente!');
            setGenerateModalOpen(false);
            generateForm.resetFields();
            fetchSuites();
        } catch (error) {
            message.error('Errore nella generazione');
        }
    };

    const handleRunSuite = async (suite) => {
        setRunningSuite(suite.id);
        try {
            const token = localStorage.getItem('token');
            await apiFetch(`/api/v1/tests/suites/${suite.id}/run`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });
            message.success('Test eseguito!');
            fetchSuites();
            fetchExecutions();
        } catch (error) {
            message.error('Errore nell\'esecuzione test');
        } finally {
            setRunningSuite(null);
        }
    };

    const handleRunAll = async () => {
        const MAX_RETRIES = 3;
        const activeSuites = suites.filter(s => s.is_active !== false);
        
        if (activeSuites.length === 0) {
            message.warning('Nessuna test suite attiva da eseguire');
            return;
        }

        setRunningAll(true);
        setRunAllProgress({ current: 0, total: activeSuites.length, suiteName: '', status: 'Iniziale...' });
        
        let passed = 0;
        let failed = 0;
        
        for (let i = 0; i < activeSuites.length; i++) {
            const suite = activeSuites[i];
            setRunAllProgress({ 
                current: i + 1, 
                total: activeSuites.length, 
                suiteName: suite.nome, 
                status: 'In esecuzione...' 
            });
            
            let success = false;
            let lastError = null;
            
            for (let retry = 0; retry < MAX_RETRIES; retry++) {
                try {
                    const token = localStorage.getItem('token');
                    const response = await apiFetch(`/api/v1/tests/suites/${suite.id}/run`, {
                        method: 'POST',
                        headers: { Authorization: `Bearer ${token}` }
                    });
                    const result = await response.json();
                    
                    if (result.esito === 'successo') {
                        success = true;
                        break;
                    } else {
                        lastError = result;
                        if (retry < MAX_RETRIES - 1) {
                            setRunAllProgress(p => ({ ...p, status: `Riprova ${retry + 1}/${MAX_RETRIES}...` }));
                            await new Promise(r => setTimeout(r, 1000));
                        }
                    }
                } catch (error) {
                    lastError = error;
                    if (retry < MAX_RETRIES - 1) {
                        setRunAllProgress(p => ({ ...p, status: `Riprova ${retry + 1}/${MAX_RETRIES}...` }));
                        await new Promise(r => setTimeout(r, 1000));
                    }
                }
            }
            
            if (success) {
                passed++;
                setRunAllProgress(p => ({ ...p, status: '✓ Passato' }));
            } else {
                failed++;
                setRunAllProgress(p => ({ ...p, status: '✗ Fallito' }));
            }
            
            await new Promise(r => setTimeout(r, 500));
        }
        
        setRunningAll(false);
        setRunAllProgress({ current: 0, total: 0, suiteName: '', status: '' });
        
        fetchSuites();
        fetchExecutions();
        
        if (failed === 0) {
            message.success(`Completato! Tutte le ${passed} suite sono passate!`);
        } else {
            message.warning(`Completato: ${passed} passate, ${failed} fallite`);
        }
    };

    const [deleteModalVisible, setDeleteModalVisible] = useState(false);
    const [itemToDelete, setItemToDelete] = useState(null);
    const [deleteType, setDeleteType] = useState(null);

    const confirmDelete = (id, type) => {
        setItemToDelete(id);
        setDeleteType(type);
        setDeleteModalVisible(true);
    };

    const executeDelete = async () => {
        if (deleteType === 'suite') {
            console.log('Executing delete for suite:', itemToDelete);
            try {
                const token = localStorage.getItem('token');
                const response = await apiFetch(`/api/v1/tests/suites/${itemToDelete}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` }
                });
                console.log('Delete response status:', response.status);
                if (!response.ok) {
                    const err = await response.json();
                    message.error(err.error || 'Errore nell\'eliminazione');
                    return;
                }
                message.success('TestSuite eliminata');
                fetchSuites();
            } catch (error) {
                console.error('Delete suite error:', error);
                message.error('Errore nell\'eliminazione');
            }
        } else if (deleteType === 'execution') {
            console.log('Executing delete for execution:', itemToDelete);
            try {
                const token = localStorage.getItem('token');
                const response = await apiFetch(`/api/v1/tests/executions/${itemToDelete}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (!response.ok) {
                    const err = await response.json();
                    message.error(err.error || 'Errore nell\'eliminazione');
                    return;
                }
                message.success('Esecuzione eliminata');
                fetchExecutions();
            } catch (error) {
                console.error('Delete execution error:', error);
                message.error('Errore nell\'eliminazione');
            }
        }
        setDeleteModalVisible(false);
        setItemToDelete(null);
        setDeleteType(null);
    };

    const handleDeleteSuite = (suiteId) => {
        console.log('Opening delete modal for suite:', suiteId);
        confirmDelete(suiteId, 'suite');
    };

    const handleDeleteExecution = (execId) => {
        console.log('Opening delete modal for execution:', execId);
        confirmDelete(execId, 'execution');
    };

    const handleDeleteAllExecutions = async () => {
        setDeletingAll(true);
        try {
            const token = localStorage.getItem('token');
            for (const exec of executions) {
                await apiFetch(`/api/v1/tests/executions/${exec.id}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            message.success('Tutte le esecuzioni eliminate');
            fetchExecutions();
        } catch (error) {
            message.error('Errore nell\'eliminazione');
        } finally {
            setDeletingAll(false);
            setDeleteAllModalVisible(false);
        }
    };

    const handleAddCase = async (values) => {
        try {
            const token = localStorage.getItem('token');
            await apiFetch(`/api/v1/tests/suites/${selectedSuite.id}/cases`, {
                method: 'POST',
                body: JSON.stringify(values),
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
            });
            message.success('TestCase aggiunto!');
            setCaseModalOpen(false);
            caseForm.resetFields();
            fetchSuites();
        } catch (error) {
            message.error('Errore nell\'aggiunta del test case');
        }
    };

    const handleChangeStatus = async (moduloNome, nuovoStato) => {
        try {
            const token = localStorage.getItem('token');
            await apiFetch('/api/v1/tests/module/status', {
                method: 'POST',
                body: JSON.stringify({ modulo_nome: moduloNome, nuovo_stato: nuovoStato }),
                headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
            });
            message.success(`Stato cambiato a ${nuovoStato}`);
            fetchSuites();
        } catch (error) {
            message.error('Errore nel cambio stato');
        }
    };

    const exportReport = (execution) => {
        const report = `
TEST REPORT - FlaskERP
======================
Suite: ${execution.test_suite_id}
Data: ${execution.created_at}
Esito: ${execution.esito}
Totale Test: ${execution.totale_test}
Passati: ${execution.test_passati}
Falliti: ${execution.test_falliti}
Errori: ${execution.test_errori}
Durata: ${execution.durata_secondi}s

${execution.errori?.length > 0 ? 'ERRORI:\n' + JSON.stringify(execution.errori, null, 2) : ''}
        `;
        
        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test_report_${execution.id}_${new Date().toISOString().slice(0,10)}.txt`;
        a.click();
    };

    const suiteColumns = [
        {
            title: 'Nome',
            dataIndex: 'nome',
            key: 'nome',
            render: (text, record) => (
                <Space>
                    <strong>{text}</strong>
                    <Tag color={statoColors[record.stato]}>{record.stato}</Tag>
                </Space>
            )
        },
        {
            title: 'Modulo',
            dataIndex: 'modulo_target',
            key: 'modulo_target'
        },
        {
            title: 'Tipo',
            dataIndex: 'test_type',
            key: 'test_type'
        },
        {
            title: 'Test Cases',
            key: 'test_cases',
            render: (_, record) => record.test_cases?.length || 0
        },
        {
            title: 'Ultimo Esito',
            key: 'ultimo_esito',
            render: (_, record) => (
                record.ultimo_esito ? 
                <Badge status={esitoColors[record.ultimo_esito] === 'success' ? 'success' : esitoColors[record.ultimo_esito] === 'error' ? 'error' : 'warning'} text={record.ultimo_esito} /> 
                : <Text type="secondary">Mai eseguito</Text>
            )
        },
        {
            title: 'Azioni',
            key: 'azioni',
            render: (_, record) => (
                <Space>
                    <Button 
                        type="primary" 
                        icon={<PlayCircleOutlined />} 
                        loading={runningSuite === record.id}
                        onClick={() => handleRunSuite(record)}
                    >
                        Esegui
                    </Button>
                    <Button onClick={() => { setSelectedSuite(record); setCaseModalOpen(true); }}>
                        + Test
                    </Button>
                    <Select
                        value={record.stato}
                        onChange={(val) => handleChangeStatus(record.modulo_target, val)}
                        style={{ width: 120 }}
                    >
                        <Option value="bozza">Bozza</Option>
                        <Option value="in_test">In Test</Option>
                        <Option value="testato">Testato</Option>
                        <Option value="pubblicato">Pubblicato</Option>
                        <Option value="obsoleto">Obsoleto</Option>
                    </Select>
                    <Button 
                        danger 
                        icon={<DeleteOutlined />} 
                        onClick={() => handleDeleteSuite(record.id)}
                    />
                </Space>
            )
        }
    ];

    const executionColumns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id'
        },
        {
            title: 'Suite',
            dataIndex: 'test_suite_id',
            key: 'test_suite_id'
        },
        {
            title: 'Esito',
            dataIndex: 'esito',
            key: 'esito',
            render: (esito) => (
                <Badge 
                    status={esitoColors[esito] === 'success' ? 'success' : esitoColors[esito] === 'error' ? 'error' : esitoColors[esito] === 'warning' ? 'warning' : 'processing'} 
                    text={esito} 
                />
            )
        },
        {
            title: 'Progresso',
            key: 'progresso',
            render: (_, record) => (
                <span>
                    {record.test_passati}/{record.totale_test} 
                    ({record.percentuale_successo}%)
                </span>
            )
        },
        {
            title: 'Durata',
            dataIndex: 'durata_secondi',
            key: 'durata_secondi',
            render: (s) => `${s}s`
        },
        {
            title: 'Data',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (d) => new Date(d).toLocaleString()
        },
        {
            title: 'Azioni',
            key: 'azioni',
            render: (_, record) => (
                <Space>
                    <Button 
                        icon={<ExportOutlined />} 
                        onClick={() => exportReport(record)}
                    >
                        Report
                    </Button>
                    <Button 
                        danger 
                        icon={<DeleteOutlined />} 
                        onClick={() => handleDeleteExecution(record.id)}
                    />
                </Space>
            )
        }
    ];

    if (loading) return <Spin size="large" />;

    return (
        <Layout>
            <Modal
                title={deleteType === 'suite' ? 'Eliminare TestSuite?' : 'Eliminare Esecuzione Test?'}
                open={deleteModalVisible}
                onOk={executeDelete}
                onCancel={() => { setDeleteModalVisible(false); setItemToDelete(null); setDeleteType(null); }}
                okText="Elimina"
                okType="danger"
                cancelText="Annulla"
            >
                <p>Questa azione non è reversibile.</p>
            </Modal>
            <Modal
                title="Eliminare Tutte le Esecuzioni?"
                open={deleteAllModalVisible}
                onOk={handleDeleteAllExecutions}
                onCancel={() => setDeleteAllModalVisible(false)}
                okText="Elimina Tutti"
                okType="danger"
                cancelText="Annulla"
                confirmLoading={deletingAll}
            >
                <p>Sei sicuro di voler eliminare tutte le {executions.length} esecuzioni?</p>
                <p style={{ color: 'red' }}>Questa azione non è reversibile.</p>
            </Modal>
            <div style={{ padding: '24px' }}>
                <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Title level={2}>Test Runner</Title>
                    <Space>
                        <Button 
                            type="primary" 
                            icon={<PlusOutlined />} 
                            onClick={() => setSuiteModalOpen(true)}
                        >
                            Nuova Suite
                        </Button>
                        <Button 
                            icon={<PlayCircleOutlined />} 
                            onClick={() => setGenerateModalOpen(true)}
                        >
                            Genera Suite
                        </Button>
                        <Button 
                            type="primary" 
                            danger={runningAll}
                            icon={<CheckCircleOutlined />} 
                            onClick={handleRunAll}
                            loading={runningAll}
                        >
                            {runningAll ? `Esecuzione... ${runAllProgress.current}/${runAllProgress.total}` : 'Esegui Tutti'}
                        </Button>
                    </Space>
                </div>

                {runningAll && (
                    <Alert 
                        message={`Esecuzione Test Suite: ${runAllProgress.suiteName}`}
                        description={`Suite ${runAllProgress.current} di ${runAllProgress.total} - ${runAllProgress.status}`}
                        type="info"
                        showIcon
                        style={{ marginBottom: 16 }}
                    />
                )}

                <Alert 
                    message="Guida agli Stati dei Moduli" 
                    description={
                        <div>
                            <p><Tag color="default">BOZZA</Tag> - Modulo appena creato, non testato</p>
                            <p><Tag color="processing">IN_TEST</Tag> - Test in corso, in fase di validazione</p>
                            <p><Tag color="warning">TESTATO</Tag> - Test completati, pronto per pubblicazione</p>
                            <p><Tag color="success">PUBBLICATO</Tag> - Operativo in produzione</p>
                            <p><Tag color="error">OBSOLETO</Tag> - Non più utilizzabile</p>
                        </div>
                    }
                    type="info"
                    style={{ marginBottom: 16 }}
                />

                <Tabs 
                    activeKey={activeTab} 
                    onChange={setActiveTab}
                    items={[
                        {
                            key: 'suites',
                            label: 'Test Suites',
                            children: (
                                <Table 
                                    dataSource={suites} 
                                    columns={suiteColumns} 
                                    rowKey="id"
                                    pagination={{ pageSize: 10 }}
                                />
                            )
                        },
                        {
                            key: 'executions',
                            label: 'Storico Esecuzioni',
                            children: (
                                <div>
                                    <div style={{ marginBottom: 16, textAlign: 'right' }}>
                                        <Button 
                                            danger 
                                            icon={<DeleteOutlined />}
                                            onClick={() => setDeleteAllModalVisible(true)}
                                            disabled={executions.length === 0}
                                        >
                                            Elimina Tutti
                                        </Button>
                                    </div>
                                    <Table 
                                        dataSource={executions} 
                                        columns={executionColumns} 
                                        rowKey="id"
                                        pagination={{ pageSize: 10 }}
                                    />
                                </div>
                            )
                        }
                    ]}
                />

                <Modal
                    title="Crea TestSuite"
                    open={suiteModalOpen}
                    onCancel={() => setSuiteModalOpen(false)}
                    footer={null}
                >
                    <Form form={form} onFinish={handleCreateSuite} layout="vertical">
                        <Form.Item name="nome" label="Nome" rules={[{ required: true }]}>
                            <Input />
                        </Form.Item>
                        <Form.Item name="descrizione" label="Descrizione">
                            <Input.TextArea />
                        </Form.Item>
                        <Form.Item name="modulo_target" label="Modulo Target" rules={[{ required: true }]}>
                            <Input placeholder="es: anagrafiche, soggetti, ruoli" />
                        </Form.Item>
                        <Form.Item name="test_type" label="Tipo Test" initialValue="crud">
                            <Select>
                                <Option value="crud">CRUD</Option>
                                <Option value="validation">Validazione</Option>
                                <Option value="api">API</Option>
                                <Option value="full">Completo</Option>
                            </Select>
                        </Form.Item>
                        <Button type="primary" htmlType="submit">Crea</Button>
                    </Form>
                </Modal>

                <Modal
                    title="Genera TestSuite Automatica"
                    open={generateModalOpen}
                    onCancel={() => setGenerateModalOpen(false)}
                    footer={null}
                >
                    <Form form={generateForm} onFinish={handleGenerateSuite} layout="vertical">
                        <Form.Item name="modulo_nome" label="Nome Modulo" rules={[{ required: true }]}>
                            <Input placeholder="es: anagrafiche" />
                        </Form.Item>
                        <Form.Item name="endpoint_base" label="Endpoint Base" rules={[{ required: true }]}>
                            <Input placeholder="es: /soggetti" />
                        </Form.Item>
                        <Form.Item name="tipo" label="Tipo" initialValue="crud">
                            <Select>
                                <Option value="crud">CRUD</Option>
                                <Option value="validation">Validazione</Option>
                            </Select>
                        </Form.Item>
                        <Button type="primary" htmlType="submit">Genera</Button>
                    </Form>
                </Modal>

                <Modal
                    title={`Aggiungi Test a ${selectedSuite?.nome}`}
                    open={caseModalOpen}
                    onCancel={() => setCaseModalOpen(false)}
                    footer={null}
                    width={600}
                >
                    <Form form={caseForm} onFinish={handleAddCase} layout="vertical">
                        <Form.Item name="nome" label="Nome Test" rules={[{ required: true }]}>
                            <Input />
                        </Form.Item>
                        <Form.Item name="descrizione" label="Descrizione">
                            <Input.TextArea />
                        </Form.Item>
                        <Space>
                            <Form.Item name="test_type" label="Tipo" initialValue="create">
                                <Select style={{ width: 100 }}>
                                    <Option value="create">Create</Option>
                                    <Option value="read">Read</Option>
                                    <Option value="update">Update</Option>
                                    <Option value="delete">Delete</Option>
                                    <Option value="validation">Validation</Option>
                                    <Option value="api">API</Option>
                                </Select>
                            </Form.Item>
                            <Form.Item name="metodo" label="Metodo" initialValue="GET">
                                <Select style={{ width: 100 }}>
                                    <Option value="GET">GET</Option>
                                    <Option value="POST">POST</Option>
                                    <Option value="PUT">PUT</Option>
                                    <Option value="DELETE">DELETE</Option>
                                </Select>
                            </Form.Item>
                        </Space>
                        <Form.Item name="endpoint" label="Endpoint" rules={[{ required: true }]}>
                            <Input placeholder="/api/v1/soggetti" />
                        </Form.Item>
                        <Form.Item name="payload" label="Payload (JSON)">
                            <Input.TextArea rows={3} placeholder='{"nome": "Test"}' />
                        </Form.Item>
                        <Form.Item name="expected_status" label="Status Atteso" initialValue={200}>
                            <Input type="number" />
                        </Form.Item>
                        <Form.Item name="ordine" label="Ordine" initialValue={0}>
                            <Input type="number" />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">Aggiungi</Button>
                    </Form>
                </Modal>
            </div>
        </Layout>
    );
}

export default TestRunnerPage;
