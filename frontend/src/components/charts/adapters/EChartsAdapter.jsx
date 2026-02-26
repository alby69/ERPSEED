import React, { useRef } from 'react';
import ReactECharts from 'echarts-for-react';

const ECHARTS_NAME = 'echarts';

const ECHART_TYPE_MAP = {
  bar: 'bar',
  line: 'line',
  pie: 'pie',
  doughnut: 'pie',
  radar: 'radar',
  scatter: 'scatter',
  heatmap: 'heatmap',
  treemap: 'treemap',
  gauge: 'gauge',
};

const DEFAULT_COLORS = [
  '#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272', '#FC8452', '#9A60B4'
];

export const EChartsAdapter = {
  name: ECHARTS_NAME,
  label: 'ECharts',
  chartTypes: ['bar', 'line', 'pie', 'doughnut', 'radar', 'scatter', 'heatmap', 'treemap', 'gauge'],
  supportsExport: true,

  render(config, data, options = {}) {
    const chartRef = useRef(null);

    if (!data || !data.labels || !data.datasets) {
      return <div className="text-muted p-3">No data available</div>;
    }

    const echartType = ECHART_TYPE_MAP[config.chart_type] || 'bar';
    const isPie = ['pie', 'doughnut'].includes(echartType);
    const isGauge = echartType === 'gauge';

    let series;
    
    if (isPie) {
      series = [{
        name: config.title || 'Data',
        type: 'pie',
        radius: config.chart_type === 'doughnut' ? ['40%', '70%'] : '50%',
        data: data.labels.map((label, i) => ({
          name: label,
          value: data.datasets[0]?.data?.[i] || 0
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }];
    } else if (isGauge) {
      series = [{
        type: 'gauge',
        progress: { show: true, width: 18 },
        axisLine: { lineStyle: { width: 18 } },
        axisTick: { show: false },
        splitLine: { length: 15, lineStyle: { width: 2, color: '#999' } },
        axisLabel: { distance: 25, color: '#999', fontSize: 12 },
        anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
        title: { show: false },
        detail: {
          valueAnimation: true,
          fontSize: 30,
          offsetCenter: [0, '70%']
        },
        data: [{
          value: data.datasets[0]?.data?.[0] || 0,
          name: config.title || ''
        }]
      }];
    } else {
      series = data.datasets.map((ds, idx) => ({
        name: ds.label || `Series ${idx + 1}`,
        type: echartType,
        data: ds.data || [],
        smooth: config.chart_type === 'line',
        emphasis: { focus: 'series' }
      }));
    }

    const chartOptions = {
      color: DEFAULT_COLORS,
      title: config.title ? {
        text: config.title,
        left: 'center'
      } : undefined,
      tooltip: {
        trigger: isPie ? 'item' : 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        bottom: 0,
        data: isPie ? data.labels : data.datasets?.map(ds => ds.label)
      },
      grid: isPie || isGauge ? undefined : {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xaxis: isPie || isGauge ? undefined : {
        type: 'category',
        data: data.labels,
        axisTick: { alignWithLabel: true }
      },
      yaxis: isPie || isGauge ? undefined : {
        type: 'value'
      },
      series,
      ...options
    };

    return (
      <div style={{ width: '100%', height: '100%', minHeight: '200px' }}>
        <ReactECharts
          ref={chartRef}
          option={chartOptions}
          style={{ height: '100%', minHeight: '200px' }}
          opts={{ renderer: 'svg' }}
        />
      </div>
    );
  },

  getChartTypes() {
    return this.chartTypes;
  },
};

export default EChartsAdapter;
