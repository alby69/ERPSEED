import React from 'react';
import { Select, Space } from 'antd';
import { useTranslation } from 'react-i18next';
import { GlobalOutlined } from '@ant-design/icons';
import { useTheme } from '../context';

const languages = [
  { value: 'en', label: '🇬🇧 English' },
  { value: 'it', label: '🇮🇹 Italiano' },
];

function LanguageSelector() {
  const { i18n } = useTranslation();
  const { themeConfig } = useTheme();

  const handleLanguageChange = (value) => {
    i18n.changeLanguage(value);
    localStorage.setItem('language', value);
  };

  const isDark = themeConfig.mode === 'dark';

  return (
    <Space size={4}>
      <GlobalOutlined style={{ color: isDark ? 'rgba(255,255,255,0.65)' : 'rgba(0,0,0,0.45)' }} />
      <Select
        size="small"
        value={i18n.language.split('-')[0]} // Handle locales like en-US
        onChange={handleLanguageChange}
        options={languages}
        variant="borderless"
        popupMatchSelectWidth={false}
        style={{ width: 'auto' }}
        dropdownStyle={{ minWidth: 120 }}
      />
    </Space>
  );
}

export default LanguageSelector;
