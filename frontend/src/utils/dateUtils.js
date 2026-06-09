import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';

dayjs.extend(customParseFormat);

export const API_DATE_FORMAT = 'YYYY-MM-DD';
export const DISPLAY_DATE_FORMAT = 'DD/MM/YYYY';
export const DISPLAY_DATETIME_FORMAT = 'DD/MM/YYYY HH:mm';

export const parseDateForForm = (dateString) => {
  return dateString ? dayjs(dateString, API_DATE_FORMAT) : null;
};

export const formatDateForApi = (dayjsObject) => {
  return dayjsObject ? dayjsObject.format(API_DATE_FORMAT) : null;
};

export const formatDateForDisplay = (dateString) => {
  return dateString ? dayjs(dateString, API_DATE_FORMAT).format(DISPLAY_DATE_FORMAT) : null;
};

export const formatDateTimeForDisplay = (dateString) => {
  return dateString ? dayjs(dateString).format(DISPLAY_DATETIME_FORMAT) : null;
};

export default dayjs; // Esporta dayjs come default per usi più complessi se necessario