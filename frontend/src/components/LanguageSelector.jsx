import React from 'react';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
];

function LanguageSelector() {
  const { i18n } = useTranslation();

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <select
      className="form-select form-select-sm"
      value={i18n.language}
      onChange={handleLanguageChange}
      style={{ width: 'auto', cursor: 'pointer' }}
      aria-label="Select language"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  );
}

export default LanguageSelector;
