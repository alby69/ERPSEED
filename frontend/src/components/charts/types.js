export const CHART_LIBRARIES = {
  CHARTJS: 'chartjs',
  APEXCHARTS: 'apexcharts',
  ECHARTS: 'echarts',
};

export const CHART_LIBRARY_LABELS = {
  [CHART_LIBRARIES.CHARTJS]: 'Chart.js',
  [CHART_LIBRARIES.APEXCHARTS]: 'ApexCharts',
  [CHART_LIBRARIES.ECHARTS]: 'ECharts',
};

export const CHART_TYPES = {
  BAR: 'bar',
  LINE: 'line',
  PIE: 'pie',
  DOUGHNUT: 'doughnut',
  AREA: 'area',
  RADAR: 'radar',
  SCATTER: 'scatter',
  POLAR_AREA: 'polarArea',
  BUBBLE: 'bubble',
  HEATMAP: 'heatmap',
  TREEMAP: 'treemap',
};

export const AGGREGATION_TYPES = {
  SUM: 'sum',
  AVG: 'avg',
  COUNT: 'count',
  MIN: 'min',
  MAX: 'max',
};

export const CHART_TYPES_BY_LIBRARY = {
  [CHART_LIBRARIES.CHARTJS]: ['bar', 'line', 'pie', 'doughnut', 'radar', 'scatter', 'bubble', 'polarArea'],
  [CHART_LIBRARIES.APEXCHARTS]: ['bar', 'line', 'area', 'pie', 'donut', 'radar', 'scatter', 'heatmap', 'treemap'],
  [CHART_LIBRARIES.ECHARTS]: ['bar', 'line', 'pie', 'doughnut', 'radar', 'scatter', 'heatmap', 'treemap', 'gauge'],
};

export const DEFAULT_CHART_OPTIONS = {
  [CHART_LIBRARIES.CHARTJS]: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
    },
  },
  [CHART_LIBRARIES.APEXCHARTS]: {
    chart: {
      toolbar: { show: true, tools: { download: true } },
      zoom: { enabled: true },
    },
    legend: { position: 'bottom' },
    dataLabels: { enabled: false },
  },
  [CHART_LIBRARIES.ECHARTS]: {
    responsive: true,
    maintainAspectRatio: false,
    legend: { position: 'bottom' },
    tooltip: {},
  },
};
