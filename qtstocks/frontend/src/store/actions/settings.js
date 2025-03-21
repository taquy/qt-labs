export const FETCH_SETTINGS = 'settings/fetchSettings';
export const SAVE_SETTINGS = 'settings/saveSettings';

export const fetchSettings = (setting_key) => ({ type: FETCH_SETTINGS, setting_key });
export const saveSettings = (setting_key, setting_value) => ({ type: SAVE_SETTINGS, setting_key, setting_value });
