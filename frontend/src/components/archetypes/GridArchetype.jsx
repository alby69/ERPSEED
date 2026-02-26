/**
 * Grid Layout Archetype
 * 
 * Grid layout container for other components
 */
import React from 'react';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { ComponentRenderer } from '../core/ComponentRenderer';

const GRID_COLS = 12;
const ROW_HEIGHT = 80;

const GridArchetype = ({ 
  config = {}, 
  data = null,
  onChange,
  ...props 
}) => {
  const { 
    cols = GRID_COLS, 
    rowHeight = ROW_HEIGHT, 
    margin = [16, 16],
    draggable = true,
    resizable = true,
    components = [],
  } = config;

  const [layout, setLayout] = React.useState(
    config.layout || components.map((comp, index) => ({
      i: String(comp.id || index),
      x: (index % cols) * 2,
      y: Math.floor(index / cols) * 4,
      w: 2,
      h: 4,
      minW: 1,
      minH: 2,
    }))
  );

  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
    if (onChange) {
      onChange({ ...config, layout: newLayout });
    }
  };

  return (
    <GridLayout
      className="layout"
      layout={layout}
      cols={cols}
      rowHeight={rowHeight}
      width={1100}
      margin={margin}
      isDraggable={draggable}
      isResizable={resizable}
      onLayoutChange={handleLayoutChange}
      {...props}
    >
      {components.map((comp, index) => (
        <div key={String(comp.id || index)}>
          <ComponentRenderer
            type={comp.type}
            config={comp.config}
            data={comp.data}
          />
        </div>
      ))}
    </GridLayout>
  );
};

export default GridArchetype;
