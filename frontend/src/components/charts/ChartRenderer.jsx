import React from 'react';
import { CHART_LIBRARIES } from './types';
import ChartJsAdapter from './adapters/ChartJsAdapter';
import ApexChartsAdapter from './adapters/ApexChartsAdapter';
import EChartsAdapter from './adapters/EChartsAdapter';

const ADAPTERS = {
  [CHART_LIBRARIES.CHARTJS]: ChartJsAdapter,
  [CHART_LIBRARIES.APEXCHARTS]: ApexChartsAdapter,
  [CHART_LIBRARIES.ECHARTS]: EChartsAdapter,
};

export function getAdapter(library) {
  const adapter = ADAPTERS[library];
  if (!adapter) {
    console.warn(`Chart adapter not found for library: ${library}, falling back to chartjs`);
    return ADAPTERS[CHART_LIBRARIES.CHARTJS];
  }
  return adapter;
}

export function getAllAdapters() {
  return Object.values(ADAPTERS);
}

export function getAdapterByName(name) {
  return ADAPTERS[name];
}

function ChartRenderer({ library, config, data, options }) {
  const Adapter = getAdapter(library);

  if (!Adapter) {
    return (
      <div className="alert alert-danger">
        Libreria grafica non supportata: {library}
      </div>
    );
  }

  return Adapter.render(config, data, options);
}

export default ChartRenderer;
