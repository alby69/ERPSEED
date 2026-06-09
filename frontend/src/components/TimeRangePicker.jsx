import React from 'react';
import { DatePicker } from 'antd';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

/**
 * Componente riutilizzabile per la selezione di un intervallo di tempo.
 * Utilizza dayjs per la formattazione HH:mm.
 *
 * @param {Array<string>} value - Array di due stringhe ora (es. ['09:00', '17:00'])
 * @param {Function} onChange - Callback chiamato al cambio, riceve un array di due stringhe ora (HH:mm).
 * @param {Object} rest - Tutte le altre props passate ad Ant Design RangePicker.
 */
const TimeRangePicker = ({ value, onChange, ...rest }) => {
  // Converte il valore in ingresso (array di stringhe ora) in un array di oggetti dayjs per Ant Design DatePicker
  const parsedValue = value && value.length === 2 && value[0] && value[1]
    ? [dayjs(value[0], 'HH:mm'), dayjs(value[1], 'HH:mm')]
    : [null, null];

  // Gestisce l'evento di cambio dal RangePicker di Ant Design
  const handleChange = (dates) => {
    // dates: array di oggetti dayjs
    const apiFormattedTimes = dates && dates.length === 2 ? [dates[0]?.format('HH:mm') || null, dates[1]?.format('HH:mm') || null] : [null, null];
    onChange(apiFormattedTimes);
  };

  return (
    <RangePicker
      picker="time" // Specifica che è un time picker
      format="HH:mm" // Formato di visualizzazione e input
      value={parsedValue}
      onChange={handleChange}
      style={{ width: '100%' }} // Assicura che occupi lo spazio disponibile
      {...rest}
    />
  );
};

export default TimeRangePicker;