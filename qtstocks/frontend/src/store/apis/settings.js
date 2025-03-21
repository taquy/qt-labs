import axios from 'axios';
import { API_SETTINGS_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  fetchSettings: async (setting_key) => {
    const response = await axios.get(API_SETTINGS_ENDPOINTS.settings(setting_key), getRequestConfig());
    return response.data;
  },
  saveSettings: async ({ setting_key, setting_value }) => {
    const response = await axios.put(
      API_SETTINGS_ENDPOINTS.updateSetting(setting_key), { setting_value }, getRequestConfig()
    );
    return response.data;
  },
};

export default api;