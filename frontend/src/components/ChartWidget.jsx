import React, { useEffect, useState, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
import { apiFetch } from '../utils';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function ChartWidget({ chartId, dateFilters, onFilterChange }) {
  const [chartConfig, setChartConfig] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [widgetFilters, setWidgetFilters] = useState({});
  const chartRef = useRef(null);
  const widgetRef = useRef(null);

  useEffect(() => {
    const loadChart = async () => {
      try {
        setLoading(true);
        const configRes = await apiFetch(`/sys-charts/${chartId}`);
        if (!configRes.ok) throw new Error("Failed to load chart config");
        const config = await configRes.json();
        setChartConfig(config);

        if (config.type !== 'text') {
          let url = `/analytics/chart-data/${chartId}`;
          const params = new URLSearchParams();
          if (dateFilters?.from) params.append('date_from', dateFilters.from);
          if (dateFilters?.to) params.append('date_to', dateFilters.to);

          Object.entries(widgetFilters).forEach(([key, value]) => {
            if (value) params.append(`filter_${key}`, value);
          });

          if (params.toString()) url += `?${params.toString()}`;

          const dataRes = await apiFetch(url);
          if (!dataRes.ok) throw new Error("Failed to load chart data");
          const data = await dataRes.json();
          setChartData(data);
        }
      } catch (e) {
        console.error("Chart widget error:", e);
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    if (chartId) {
      loadChart();
    }
  }, [chartId, dateFilters, widgetFilters]);

  const handleFilterChange = (field, value) => {
    const newFilters = { ...widgetFilters, [field]: value };
    setWidgetFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  const exportToPNG = async () => {
    if (!widgetRef.current) return;
    try {
      const canvas = await html2canvas(widgetRef.current, { scale: 2 });
      const link = document.createElement('a');
      link.download = `${chartConfig?.title || 'chart'}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (e) {
      console.error("Export PNG error:", e);
    }
  };

  const exportToPDF = async () => {
    if (!widgetRef.current) return;
    try {
      const canvas = await html2canvas(widgetRef.current, { scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
        unit: 'px',
        format: [canvas.width, canvas.height]
      });
      pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
      pdf.save(`${chartConfig?.title || 'chart'}.pdf`);
    } catch (e) {
      console.error("Export PDF error:", e);
    }
  };

  if (loading) return <div className="text-center p-3">Loading chart...</div>;
  if (error) return <div className="alert alert-danger">Error: {error}</div>;
  if (!chartConfig) return null;

  const renderFilters = () => {
    if (!chartConfig.filters_config || chartConfig.filters_config.length === 0) return null;

    return (
      <div className="mb-2 p-2 bg-light rounded" style={{ fontSize: '12px' }}>
        <div className="d-flex flex-wrap gap-2">
          {chartConfig.filters_config.map((filter, idx) => (
            <div key={idx} className="d-flex align-items-center">
              <label className="me-1 text-muted small">{filter.label}:</label>
              {filter.type === 'date_range' ? (
                <input
                  type="date"
                  className="form-control form-control-sm"
                  style={{ width: '130px' }}
                  value={widgetFilters[filter.field] || ''}
                  onChange={(e) => handleFilterChange(filter.field, e.target.value)}
                />
              ) : filter.type === 'select' || filter.type === 'multiselect' ? (
                <select
                  className="form-select form-select-sm"
                  style={{ width: 'auto', minWidth: '100px' }}
                  value={widgetFilters[filter.field] || ''}
                  onChange={(e) => handleFilterChange(filter.field, e.target.value)}
                >
                  <option value="">All</option>
                  {(filter.options || []).map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : filter.type === 'text' ? (
                <input
                  type="text"
                  className="form-control form-control-sm"
                  style={{ width: '100px' }}
                  placeholder="Search..."
                  value={widgetFilters[filter.field] || ''}
                  onChange={(e) => handleFilterChange(filter.field, e.target.value)}
                />
              ) : filter.type === 'number_range' ? (
                <input
                  type="number"
                  className="form-control form-control-sm"
                  style={{ width: '80px' }}
                  value={widgetFilters[filter.field] || ''}
                  onChange={(e) => handleFilterChange(filter.field, e.target.value)}
                />
              ) : null}
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (chartConfig.type === 'text') {
    return (
      <div className="card shadow-sm h-100" ref={widgetRef}>
        <div className="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
          {chartConfig.title}
          <div className="btn-group btn-group-sm">
            <button className="btn btn-outline-secondary" onClick={exportToPNG} title="Export PNG">📷</button>
            <button className="btn btn-outline-secondary" onClick={exportToPDF} title="Export PDF">📄</button>
          </div>
        </div>
        <div className="card-body" dangerouslySetInnerHTML={{ __html: chartConfig.content }} />
      </div>
    );
  }

  if (chartConfig.type === 'table') {
    const columns = chartData?.columns || [];
    const rows = chartData?.data || [];
    const displayColumns = columns.slice(0, 4);

    return (
      <div className="card shadow-sm h-100" ref={widgetRef}>
        <div className="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
          {chartConfig.title}
          <span className="badge bg-secondary">{rows.length}</span>
        </div>
        {renderFilters()}
        <div className="card-body p-0 table-responsive">
          <table className="table table-sm table-striped mb-0 small">
            <thead>
              <tr>{displayColumns.map(c => <th key={c}>{c}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((r, i) => <tr key={i}>{displayColumns.map(c => <td key={c}>{r[c]}</td>)}</tr>)}
              {rows.length === 0 && <tr><td colSpan={displayColumns.length} className="text-center text-muted">No data</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="card-footer bg-white border-top-0">
          <div className="btn-group btn-group-sm">
            <button className="btn btn-outline-secondary" onClick={exportToPNG} title="Export PNG">📷 PNG</button>
            <button className="btn btn-outline-secondary" onClick={exportToPDF} title="Export PDF">📄 PDF</button>
          </div>
        </div>
      </div>
    );
  }

  if (!chartData) return null;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: chartConfig.title },
    },
  };

  const data = {
    labels: chartData.labels,
    datasets: chartData.datasets.map(ds => ({
      ...ds,
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', 'rgba(255, 206, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)', 'rgba(153, 102, 255, 0.5)', 'rgba(255, 159, 64, 0.5)',
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)',
      ],
      borderWidth: 1,
      ...(chartConfig.type === 'area' ? { fill: true } : {}),
      ...(chartConfig.type === 'scatter' ? { showLine: false, pointRadius: 6 } : {}),
    })),
  };

  const ChartComponent = {
    bar: Bar,
    line: Line,
    pie: Pie,
    doughnut: Doughnut,
    area: Line,
    scatter: Line,
  }[chartConfig.type] || Bar;

  return (
    <div className="card shadow-sm h-100" ref={widgetRef}>
      <div className="card-header bg-white border-bottom-0 pt-2 pb-0">
        <div className="d-flex justify-content-between align-items-center">
          <h6 className="mb-0">{chartConfig.title}</h6>
          <div className="btn-group btn-group-sm">
            <button className="btn btn-outline-secondary" onClick={exportToPNG} title="Export PNG">📷</button>
            <button className="btn btn-outline-secondary" onClick={exportToPDF} title="Export PDF">📄</button>
          </div>
        </div>
      </div>
      {renderFilters()}
      <div className="card-body" style={{ height: '200px' }}>
        <ChartComponent ref={chartRef} options={options} data={data} />
      </div>
    </div>
  );
}

export default ChartWidget;
