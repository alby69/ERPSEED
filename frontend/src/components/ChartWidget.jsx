import React, { useEffect, useState } from 'react';
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
import { Bar, Line, Pie, Doughnut, Scatter } from 'react-chartjs-2';
import { apiFetch } from '../utils';

// Registrazione componenti Chart.js
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

function ChartWidget({ chartId, dateFilters }) {
  const [chartConfig, setChartConfig] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadChart = async () => {
      try {
        setLoading(true);
        // 1. Recupera configurazione grafico
        const configRes = await apiFetch(`/sys-charts/${chartId}`);
        if (!configRes.ok) throw new Error("Failed to load chart config");
        const config = await configRes.json();
        setChartConfig(config);

        // 2. Recupera dati aggregati (solo se non è un widget di testo)
        if (config.type !== 'text' || config.type === 'table') {
          let url = `/analytics/chart-data/${chartId}`;
          const params = new URLSearchParams();
          if (dateFilters?.from) params.append('date_from', dateFilters.from);
          if (dateFilters?.to) params.append('date_to', dateFilters.to);
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
  }, [chartId, dateFilters]);

  if (loading) return <div className="text-center p-3">Loading chart...</div>;
  if (error) return <div className="alert alert-danger">Error loading chart: {error}</div>;
  if (!chartConfig) return null;

  if (chartConfig.type === 'text') {
    return (
      <div className="card shadow-sm h-100">
        <div className="card-header bg-white fw-bold">{chartConfig.title}</div>
        <div className="card-body" dangerouslySetInnerHTML={{ __html: chartConfig.content }} />
      </div>
    );
  }

  if (chartConfig.type === 'table') {
    const columns = chartData.columns || [];
    const rows = chartData.data || [];
    // Mostra solo le prime 4 colonne per evitare overflow nel widget, o tutte se poche
    const displayColumns = columns.slice(0, 4); 

    return (
      <div className="card shadow-sm h-100">
        <div className="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
            {chartConfig.title}
            <span className="badge bg-secondary">{rows.length}</span>
        </div>
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
      </div>
    );
  }

  if (!chartData) return null;

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: chartConfig.title,
      },
    },
  };

  // Mappatura dati per Chart.js
  const data = {
    labels: chartData.labels,
    datasets: chartData.datasets.map(ds => {
      const baseConfig = {
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
      };

      if (chartConfig.type === 'area') {
        baseConfig.fill = true;
      } else if (chartConfig.type === 'scatter') {
        baseConfig.showLine = false;
        baseConfig.pointRadius = 6;
      }
      return baseConfig;
    }),
  };

  const ChartComponent = {
    bar: Bar,
    line: Line,
    pie: Pie,
    doughnut: Doughnut,
    area: Line, // Area is just a filled Line
    scatter: Line, // Scatter on categorical axis is a Line without lines
  }[chartConfig.type] || Bar;

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body">
        <ChartComponent options={options} data={data} />
      </div>
    </div>
  );
}

export default ChartWidget;