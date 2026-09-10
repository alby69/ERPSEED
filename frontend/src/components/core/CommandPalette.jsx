import React, { useState, useEffect, useMemo } from 'react';
import { Modal, Input, List, Tag, Typography, Space } from 'antd';
import {
    SearchOutlined,
    DashboardOutlined,
    ShoppingCartOutlined,
    UserOutlined,
    AppstoreOutlined,
    InboxOutlined,
    DollarOutlined,
    ProjectOutlined,
    PlusCircleOutlined,
    FileTextOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Text } = Typography;

const defaultCommands = [
    {
        id: 'nav-dashboard',
        title: 'Dashboard',
        category: 'Pagine',
        icon: <DashboardOutlined />,
        path: '/dashboard'
    },
    {
        id: 'nav-sales',
        title: 'Ordini Vendita',
        category: 'Pagine',
        icon: <ShoppingCartOutlined />,
        path: '/sales'
    },
    {
        id: 'nav-purchases',
        title: 'Ordini Acquisto',
        category: 'Pagine',
        icon: <ShoppingCartOutlined />,
        path: '/purchase-orders'
    },
    {
        id: 'nav-anagrafiche',
        title: 'Anagrafiche (Soggetti)',
        category: 'Pagine',
        icon: <UserOutlined />,
        path: '/anagrafiche'
    },
    {
        id: 'nav-products',
        title: 'Catalogo Prodotti',
        category: 'Pagine',
        icon: <AppstoreOutlined />,
        path: '/products'
    },
    {
        id: 'nav-inventory',
        title: 'Giacenze Magazzino',
        category: 'Pagine',
        icon: <InboxOutlined />,
        path: '/stock-levels'
    },
    {
        id: 'nav-accounting',
        title: 'Prima Nota Contabile',
        category: 'Pagine',
        icon: <DollarOutlined />,
        path: '/journal'
    },
    {
        id: 'nav-projects',
        title: 'Progetti',
        category: 'Pagine',
        icon: <ProjectOutlined />,
        path: '/projects'
    },
    {
        id: 'act-new-sales',
        title: 'Nuovo Ordine Vendita',
        category: 'Azioni Rapide',
        icon: <PlusCircleOutlined style={{ color: '#52c41a' }} />,
        path: '/sales/new'
    },
    {
        id: 'act-new-product',
        title: 'Nuovo Prodotto',
        category: 'Azioni Rapide',
        icon: <PlusCircleOutlined style={{ color: '#1890ff' }} />,
        path: '/products/new'
    },
    {
        id: 'act-new-invoice',
        title: 'Nuova Fattura',
        category: 'Azioni Rapide',
        icon: <FileTextOutlined style={{ color: '#fa8c16' }} />,
        path: '/invoices'
    }
];

/**
 * CommandPalette Component
 *
 * Global quick command palette triggered by Ctrl+K / Cmd+K.
 */
const CommandPalette = ({ isOpen, onClose, extraCommands = [] }) => {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const navigate = useNavigate();

    const allCommands = useMemo(() => {
        return [...defaultCommands, ...extraCommands];
    }, [extraCommands]);

    const filteredCommands = useMemo(() => {
        if (!query.trim()) return allCommands;
        const q = query.toLowerCase();
        return allCommands.filter(c =>
            c.title.toLowerCase().includes(q) ||
            c.category.toLowerCase().includes(q)
        );
    }, [allCommands, query]);

    useEffect(() => {
        setSelectedIndex(0);
    }, [query]);

    const handleSelect = (cmd) => {
        if (!cmd) return;
        if (cmd.action) {
            cmd.action();
        } else if (cmd.path) {
            navigate(cmd.path);
        }
        setQuery('');
        if (onClose) onClose();
    };

    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => (prev + 1) % (filteredCommands.length || 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % (filteredCommands.length || 1));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filteredCommands[selectedIndex]) {
                handleSelect(filteredCommands[selectedIndex]);
            }
        }
    };

    return (
        <Modal
            open={isOpen}
            onCancel={onClose}
            footer={null}
            title={null}
            width={600}
            style={{ top: 80 }}
            destroyOnClose
        >
            <div style={{ padding: '8px 0' }}>
                <Input
                    prefix={<SearchOutlined style={{ color: '#bfbfbf', fontSize: 18 }} />}
                    placeholder="Cerca pagina o azione rapida... (es. Ordini, Nuovo Prodotto)"
                    size="large"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    autoFocus
                    variant="borderless"
                    style={{ fontSize: 16, borderBottom: '1px solid #f0f0f0', borderRadius: 0, paddingBottom: 12 }}
                />

                <List
                    size="small"
                    style={{ maxHeight: 350, overflowY: 'auto', marginTop: 8 }}
                    dataSource={filteredCommands}
                    locale={{ emptyText: 'Nessun comando trovato' }}
                    renderItem={(item, index) => {
                        const isSelected = index === selectedIndex;
                        return (
                            <List.Item
                                onClick={() => handleSelect(item)}
                                onMouseEnter={() => setSelectedIndex(index)}
                                style={{
                                    cursor: 'pointer',
                                    backgroundColor: isSelected ? '#e6f7ff' : 'transparent',
                                    borderRadius: 6,
                                    padding: '10px 12px',
                                    border: 'none',
                                    transition: 'background-color 0.15s'
                                }}
                            >
                                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                                    <Space size="middle">
                                        <span style={{ fontSize: 18 }}>{item.icon}</span>
                                        <Text strong={isSelected}>{item.title}</Text>
                                    </Space>
                                    <Tag color={item.category === 'Azioni Rapide' ? 'green' : 'blue'}>
                                        {item.category}
                                    </Tag>
                                </Space>
                            </List.Item>
                        );
                    }}
                />

                <div style={{ marginTop: 12, paddingTop: 8, borderTop: '1px solid #f0f0f0', textAlign: 'right' }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                        Usa <Tag size="small">↑</Tag> <Tag size="small">↓</Tag> per navigare, <Tag size="small">Enter</Tag> per selezionare, <Tag size="small">Esc</Tag> per uscire
                    </Text>
                </div>
            </div>
        </Modal>
    );
};

export default CommandPalette;
