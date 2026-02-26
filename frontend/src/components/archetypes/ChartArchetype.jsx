/**
 * Chart Archetype
 */
import React from 'react';
import ChartWidget from '../ChartWidget';

const ChartArchetype = ({ config = {}, data = null, ...props }) => {
  return <ChartWidget {...config} {...props} />;
};

export default ChartArchetype;
