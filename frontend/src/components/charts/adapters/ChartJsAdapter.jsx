import React from 'react';
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
import { Bar, Line, Pie, Doughnut, Scatter, Radar, PolarArea, Bubble } from 'react-chartjs-2';

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

const CHART_TYPE_MAP = {
  bar: Bar,
  line: Line,
  pie: Pie,
  doughnut: Doughnut,
  radar: Radar,
  scatter: Scatter,
  polarArea: PolarArea,
  bubble: Bubble,
};

const CHARTJS_NAME = 'chartjs';

export const ChartJsAdapter = {
  name: CHARTJS_NAME,
  label: 'Chart.js',
  chartTypes: ['bar', 'line', 'pie', 'doughnut', 'radar', 'scatter', 'polarArea', 'bubble'],
  supportsExport: true,

  render(config, data, options = {}) {
    const ChartComponent = CHART_TYPE_MAP[config.chart_type];
    
    if (!ChartComponent) {
      return <div className="text-danger">Chart type not supported: {config.chart_type}</div>;
    }

    if (!data || !data.labels || !data.datasets) {
      return <div className="text-muted">No data available</div>;
    }

    const chartData = {
      labels: data.labels,
      datasets: data.datasets.map((ds, idx) => ({
        ...ds,
        backgroundColor: ds.backgroundColor || getDefaultColors(idx),
        borderColor: ds.borderColor || getDefaultColors(idx),
      })),
    };

    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        title: { display: !!config.title, text: config.title },
      },
      ...options,
    };

    return (
      <div style={{ width: '100%', height: '100%', minHeight: '200px' }}>
        <ChartComponent data={chartData} options={defaultOptions} />
      </div>
    );
  },

  getChartTypes() {
    return this.chartTypes;
  },
};

function getDefaultColors(index) {
  const colors = [
    'rgba(54, 162, 235, 0.6)',
    'rgba(255, 99, 132, 0.6)',
    'rgba(75, 192, 192, 0.6)',
    'rgba(255, 206, 86, 0.6)',
    'rgba(153, 102, 255, 0.6)',
    'rgba(255, 159, 64, 0.6)',
    'rgba(199, 199, 199, 0.6)',
    'rgba(83, 102, 255, 0.6)',
  ];
  return colors[index % colors.length];
}

export default ChartJsAdapter;
