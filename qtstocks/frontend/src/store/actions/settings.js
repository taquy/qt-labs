export const FETCH_SETTINGS = 'settings/fetchSettings';
export const SAVE_SETTINGS = 'settings/saveSettings';

export const fetchSettings = () => ({ type: FETCH_SETTINGS });
export const saveSettings = (type, settings_value) => ({ type: SAVE_SETTINGS, payload: { type, settings_value } });
