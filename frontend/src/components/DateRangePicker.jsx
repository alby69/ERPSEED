import React from 'react';
import { DatePicker } from 'antd';
import { parseDateForForm, formatDateForApi, DISPLAY_DATE_FORMAT } from '@/utils/dateUtils';

const { RangePicker } = DatePicker;

/**
 * Componente riutilizzabile per la selezione di un intervallo di date.
 * Utilizza dayjs e le utility di dateUtils per la formattazione.
 *
 * @param {Array<string>} value - Array di due stringhe data (es. ['2023-01-01', '2023-01-31'])
 * @param {Function} onChange - Callback chiamato al cambio, riceve un array di due stringhe data API.
 * @param {Object} rest - Tutte le altre props passate ad Ant Design RangePicker.
 */
const DateRangePicker = ({ value, onChange, ...rest }) => {
  // Converte il valore in ingresso (array di stringhe data) in un array di oggetti dayjs per Ant Design DatePicker
  const parsedValue = value && value.length === 2 && value[0] && value[1]
    ? [parseDateForForm(value[0]), parseDateForForm(value[1])]
    : [null, null];

  // Gestisce l'evento di cambio dal DatePicker di Ant Design
  const handleChange = (dates) => {
    // dates: array di oggetti dayjs
    const apiFormattedDates = dates && dates.length === 2 ? [formatDateForApi(dates[0]), formatDateForApi(dates[1])] : [null, null];
    onChange(apiFormattedDates);
  };

  return (
    <RangePicker
      value={parsedValue}
      onChange={handleChange}
      format={DISPLAY_DATE_FORMAT} // Utilizza il formato di visualizzazione centralizzato
      style={{ width: '100%' }} // Assicura che occupi lo spazio disponibile
      {...rest}
    />
  );
};

export default DateRangePicker;