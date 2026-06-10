import React from 'react';
import { Button } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import ColumnSettingsDrawer from './ColumnSettingsDrawer';

export default function ColumnSettingsButton({ manager }) {
  return (
    <>
      <Button icon={<SettingOutlined />} onClick={manager.openDrawer}>
        Colonne
      </Button>
      <ColumnSettingsDrawer
        open={manager.drawerOpen}
        onClose={manager.closeDrawer}
        columns={manager.allColumns}
        onToggle={manager.toggleColumn}
        onMoveUp={(key) => manager.moveColumn(key, -1)}
        onMoveDown={(key) => manager.moveColumn(key, 1)}
        onReset={manager.resetColumns}
        hasChanges={manager.hasChanges}
      />
    </>
  );
}
