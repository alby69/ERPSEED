/**
 * Metric Archetype
 */
import React from 'react';
import { Card, Statistic } from 'antd';

const MetricArchetype = ({ config = {}, data = null, ...props }) => {
  const { valueType = 'number', format = 'number', title = 'Metric' } = config;
  const value = data?.value || 0;

  return (
    <Card>
      <Statistic 
        title={title} 
        value={value} 
        formatter={(val) => format === 'currency' ? `€${val.toLocaleString()}` : val.toLocaleString()} 
      />
    </Card>
  );
};

export default MetricArchetype;
