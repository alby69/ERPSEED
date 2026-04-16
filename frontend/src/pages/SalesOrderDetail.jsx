import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { Layout, FormLines } from '../components';
import { apiFetch, formatCurrency } from '../utils';

function SalesOrderDetail() {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const isNew = orderId === 'new';
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dynamicOptions, setDynamicOptions] = useState({});

    const lineColumns = [
        { accessor: 'product.name', header: 'Product' },
        { accessor: 'quantity', header: 'Quantity' },
        { accessor: 'unit_price', header: 'Unit Price', render: (row) => formatCurrency(row.unit_price) },
        { accessor: 'line_total', header: 'Total', render: (row) => formatCurrency(row.line_total) },
    ];

    const lineFields = [
        { name: 'product_id', label: 'Product', type: 'select', apiUrl: '/products', valueKey: 'id', labelKey: 'name', colClass: 'col-md-5' },
        { name: 'quantity', label: 'Qty', type: 'number', colClass: 'col-md-2' },
        { name: 'unit_price', label: 'Price', type: 'currency', colClass: 'col-md-2' },
        { name: 'line_total', label: 'Total', type: 'currency', readOnly: true, colClass: 'col-md-3' },
    ];

    const computeTotals = (lines = []) => {
        let grandTotal = 0;
        const updatedLines = lines.map(line => {
            const quantity = parseFloat(line.quantity) || 0;
            const price = parseFloat(line.unit_price) || 0;
            const lineTotal = quantity * price;
            grandTotal += lineTotal;
            return { ...line, line_total: lineTotal.toFixed(2) };
        });
        return { updatedLines, grandTotal };
    };

    const fetchOrder = useCallback(async () => {
        if (isNew) {
            setOrder({
                party_id: '',
                order_date: new Date().toISOString().substring(0, 10),
                lines: [],
                total_amount: '0.00',
                status: 'draft'
            });
            setLoading(false);
            return;
        }
        try {
            setLoading(true);
            const data = await apiFetch(`/sales-orders/${orderId}`).then(res => res.json());
            const { updatedLines, grandTotal } = computeTotals(data.lines || []);
            setOrder({ ...data, lines: updatedLines, total_amount: grandTotal.toFixed(2) });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [orderId, isNew]);

    useEffect(() => {
        fetchOrder();
        apiFetch('/parties?per_page=1000').then(r => r.json()).then(d => setDynamicOptions(p => ({...p, parties: d.items || d})));
    }, [fetchOrder]);

    const handleHeaderChange = (e) => {
        const { name, value } = e.target;
        setOrder(prev => ({ ...prev, [name]: value }));
    };

    const handleLinesChange = ({ name, value }) => { // Destruttura l'oggetto evento
        const { updatedLines, grandTotal } = computeTotals(value);
        setOrder(prev => ({ ...prev, [name]: updatedLines, total_amount: grandTotal.toFixed(2) }));
    };

    const handleSave = async () => {
        try {
            const payload = {
                ...order,
                lines_attributes: order.lines.map(({ id, product_id, quantity, unit_price, _destroy }) => ({
                    id, product_id, quantity, unit_price, _destroy
                }))
            };
            delete payload.lines;
            delete payload.party;

            const url = isNew ? '/sales-orders' : `/sales-orders/${orderId}`;
            const method = isNew ? 'POST' : 'PUT';

            await apiFetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            message.success('Order saved successfully!');
            navigate('/sales');
        } catch (err) {
            message.error(`Error saving: ${err.message}`);
        }
    };

    const handleDownloadPDF = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`/api/v1/pdf/sales-order/${orderId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Errore download PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ordine_${orderId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            alert(`Errore PDF: ${err.message}`);
        }
    };

    if (loading) return <Layout><div>Loading order...</div></Layout>;
    if (error) return <Layout><div className="alert alert-danger m-4">{error}</div></Layout>;
    if (!order) return <Layout><div>Order not found.</div></Layout>;

    return (
        <Layout>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2>{isNew ? 'New Sales Order' : `Sales Order #${order.id}`}</h2>
                <div>
                    <Link to="/sales" className="btn btn-secondary me-2">Back</Link>
                    {!isNew && (
                        <button onClick={handleDownloadPDF} className="btn btn-danger me-2">
                            Download PDF
                        </button>
                    )}
                    <button onClick={handleSave} className="btn btn-primary">Save Order</button>
                </div>
            </div>

            <div className="card">
                <div className="card-header">Order Details</div>
                <div className="card-body">
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Customer</label>
                            <select name="party_id" value={order.party_id} onChange={handleHeaderChange} className="form-select">
                                <option value="">Select Customer</option>
                                {(dynamicOptions.parties || []).map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                            </select>
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Order Date</label>
                            <input type="date" name="order_date" value={(order.order_date || '').substring(0, 10)} onChange={handleHeaderChange} className="form-control" />
                        </div>
                    </div>
                    <hr />
                    <h5>Order Lines</h5>
                    <FormLines name="lines" value={order.lines} onChange={handleLinesChange} columns={lineColumns} fields={lineFields} />
                    <div className="text-end mt-3"><h4>Totale: {formatCurrency(order.total_amount)}</h4></div>
                </div>
            </div>
        </Layout>
    );
}

export default SalesOrderDetail;