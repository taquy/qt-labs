export const FETCH_SETTINGS = 'settings/fetchSettings';
export const SAVE_SETTINGS = 'settings/saveSettings';

export const fetchSettings = (type) => ({ type: FETCH_SETTINGS, payload: { type } });
export const saveSettings = (type, setting_value) => ({ type: SAVE_SETTINGS, payload: { type, setting_value } });
