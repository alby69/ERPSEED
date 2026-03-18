/**
 * Archetype Registry
 * 
 * This module provides a registry for all component archetypes.
 * Each archetype defines how a component type should be rendered and configured.
 */

import React from 'react';

// Import archetype implementations
import TableArchetype from '../archetypes/TableArchetype';
import FormArchetype from '../archetypes/FormArchetype';
import ChartArchetype from '../archetypes/ChartArchetype';
import KanbanArchetype from '../archetypes/KanbanArchetype';
import MetricArchetype from '../archetypes/MetricArchetype';
import GridArchetype from '../archetypes/GridArchetype';

// Default archetype configurations (fallback when API is unavailable)
const DEFAULT_ARCHETYPES = {
  table: {
    name: 'data_table',
    component_type: 'table',
    description: 'Data table with sorting, filtering, pagination',
    icon: 'TableOutlined',
    defaultConfig: {
      columns: [],
      sortable: true,
      filterable: true,
      paginated: true,
      pageSize: 10,
    },
    Schema: {
      list: { method: 'GET', path: '/data' },
      create: { method: 'POST', path: '/data' },
      update: { method: 'PUT', path: '/data/{id}' },
      delete: { method: 'DELETE', path: '/data/{id}' },
    },
    Component: TableArchetype,
  },
  form: {
    name: 'form',
    component_type: 'form',
    description: 'Data entry form with validation',
    icon: 'FormOutlined',
    defaultConfig: {
      fields: [],
      layout: 'vertical',
      validateOn: 'blur',
    },
    Schema: {
      submit: { method: 'POST', path: '/submit' },
    },
    Component: FormArchetype,
  },
  chart: {
    name: 'chart',
    component_type: 'chart',
    description: 'Data visualization chart',
    icon: 'LineChartOutlined',
    defaultConfig: {
      chartType: 'bar',
      library: 'chartjs',
      aggregation: 'sum',
    },
    Schema: {
      data: { method: 'GET', path: '/chart-data' },
    },
    Component: ChartArchetype,
  },
  kanban: {
    name: 'kanban',
    component_type: 'kanban',
    description: 'Kanban board with drag & drop',
    icon: 'ColumnsOutlined',
    defaultConfig: {
      columns: [],
      draggable: true,
    },
    Schema: {
      move: { method: 'PUT', path: '/move' },
    },
    Component: KanbanArchetype,
  },
  metric: {
    name: 'metric',
    component_type: 'metric',
    description: 'KPI metric card',
    icon: 'NumberOutlined',
    defaultConfig: {
      valueType: 'number',
      format: 'number',
      comparison: null,
    },
    Schema: {
      value: { method: 'GET', path: '/value' },
    },
    Component: MetricArchetype,
  },
  grid: {
    name: 'grid_layout',
    component_type: 'grid',
    description: 'Grid layout container for other components',
    icon: 'AppstoreOutlined',
    defaultConfig: {
      cols: 12,
      rowHeight: 80,
      margin: [16, 16],
      draggable: true,
      resizable: true,
    },
    Schema: {},
    Component: GridArchetype,
  },
};

class ArchetypeRegistry {
  constructor() {
    this.archetypes = { ...DEFAULT_ARCHETYPES };
    this.listeners = [];
  }

  /**
   * Register a new archetype
   * @param {string} type - Component type identifier
   * @param {Object} config - Archetype configuration
   */
  register(type, config) {
    this.archetypes[type] = {
      ...DEFAULT_ARCHETYPES[type],
      ...config,
    };
    this.notifyListeners();
  }

  /**
   * Get archetype by type
   * @param {string} type - Component type identifier
   * @returns {Object|null} Archetype configuration
   */
  get(type) {
    return this.archetypes[type] || null;
  }

  /**
   * Get all registered archetypes
   * @returns {Object} All archetypes
   */
  getAll() {
    return { ...this.archetypes };
  }

  /**
   * Check if archetype exists
   * @param {string} type - Component type identifier
   * @returns {boolean}
   */
  has(type) {
    return !!this.archetypes[type];
  }

  /**
   * Get available archetype types
   * @returns {string[]} List of type identifiers
   */
  getTypes() {
    return Object.keys(this.archetypes);
  }

  /**
   * Load archetypes from API
   * @param {Array} archetypes - Array of archetype configurations from API
   */
  loadFromAPI(archetypes) {
    if (!archetypes || !Array.isArray(archetypes)) return;

    archetypes.forEach(arch => {
      const type = arch.component_type;
      this.archetypes[type] = {
        ...this.archetypes[type],
        ...arch,
        // Merge default config with API config
        defaultConfig: {
          ...(this.archetypes[type]?.defaultConfig || {}),
          ...(arch.default_config || {}),
        },
      };
    });

    this.notifyListeners();
  }

  /**
   * Subscribe to registry changes
   * @param {Function} listener - Callback function
   * @returns {Function} Unsubscribe function
   */
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * Notify all listeners of changes
   */
  notifyListeners() {
    this.listeners.forEach(listener => listener(this.archetypes));
  }
}

// Singleton instance
const registry = new ArchetypeRegistry();

export { registry, DEFAULT_ARCHETYPES };
export default registry;
