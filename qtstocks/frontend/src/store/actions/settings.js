export const FETCH_SETTINGS = 'settings/fetchSettings';
export const SAVE_SETTINGS = 'settings/saveSettings';

export const fetchSettings = () => ({ type: FETCH_SETTINGS });
export const saveSettings = (stocks, metric) => ({ type: SAVE_SETTINGS, payload: { stocks, metric } });
