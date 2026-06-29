import React from 'react';
import { Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { GlobalOutlined } from '@ant-design/icons';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const handleChange = (value) => {
    i18n.changeLanguage(value);
    localStorage.setItem('language', value);
  };

  return (
    <Space>
      <GlobalOutlined style={{ color: 'rgba(255, 255, 255, 0.65)' }} />
      <Select
        defaultValue={i18n.language}
        style={{ width: 100 }}
        onChange={handleChange}
        options={[
          { value: 'it', label: 'Italiano' },
          { value: 'en', label: 'English' },
        ]}
        size="small"
        variant="borderless"
        popupMatchSelectWidth={false}
        className="language-select"
        style={{ color: 'rgba(255, 255, 255, 0.65)' }}
      />
    </Space>
  );
};

export default LanguageSwitcher;
