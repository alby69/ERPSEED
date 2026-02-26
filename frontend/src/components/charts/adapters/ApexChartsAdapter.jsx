import React from 'react';
import ReactApexChart from 'react-apexcharts';

const APEXCHARTS_NAME = 'apexcharts';

const APEX_TYPE_MAP = {
  bar: 'bar',
  line: 'line',
  area: 'area',
  pie: 'pie',
  donut: 'donut',
  radar: 'radar',
  scatter: 'scatter',
  heatmap: 'heatmap',
  treemap: 'treemap',
};

const DEFAULT_COLORS = [
  '#008FFB', '#FF4560', '#00E396', '#FEB019', '#775DD0', '#FF6F61'
];

export const ApexChartsAdapter = {
  name: APEXCHARTS_NAME,
  label: 'ApexCharts',
  chartTypes: ['bar', 'line', 'area', 'pie', 'donut', 'radar', 'scatter', 'heatmap', 'treemap'],
  supportsExport: true,

  render(config, data, options = {}) {
    if (!data || !data.labels || !data.datasets) {
      return <div className="text-muted p-3">No data available</div>;
    }

    const apexType = APEX_TYPE_MAP[config.chart_type] || 'bar';
    
    const isPieOrDonut = ['pie', 'donut'].includes(apexType);
    
    const series = isPieOrDonut 
      ? data.datasets[0]?.data || []
      : data.datasets.map(ds => ({
          name: ds.label || 'Series',
          data: ds.data || []
        }));

    const labels = data.labels || [];

    const chartOptions = {
      chart: {
        type: apexType,
        height: '100%',
        toolbar: {
          show: true,
          tools: { download: true },
        },
        zoom: { enabled: true },
        fontFamily: 'inherit',
        ...options.chart,
      },
      colors: data.datasets?.map((_, i) => DEFAULT_COLORS[i % DEFAULT_COLORS.length]) || DEFAULT_COLORS,
      labels: isPieOrDonut ? labels : undefined,
      xaxis: !isPieOrDonut ? { categories: labels } : undefined,
      legend: {
        position: 'bottom',
        ...options.legend,
      },
      dataLabels: {
        enabled: false,
        ...options.dataLabels,
      },
      plotOptions: {
        bar: { borderRadius: 4 },
        ...options.plotOptions,
      },
      title: config.title ? { text: config.title } : undefined,
      subtitle: config.subtitle ? { text: config.subtitle } : undefined,
      ...options,
    };

    return (
      <div style={{ width: '100%', height: '100%', minHeight: '200px' }}>
        <ReactApexChart
          type={apexType}
          options={chartOptions}
          series={series}
          height="100%"
        />
      </div>
    );
  },

  getChartTypes() {
    return this.chartTypes;
  },
};

export default ApexChartsAdapter;
