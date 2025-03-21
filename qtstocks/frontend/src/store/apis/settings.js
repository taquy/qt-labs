import axios from 'axios';
import { API_SETTINGS_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  fetchSettings: async () => {
    const response = await axios.get(API_SETTINGS_ENDPOINTS.settings, getRequestConfig());
    return response.data.settings;
  },
  saveSettings: async ({ type, settings_value }) => {
    console.log(type, settings_value)
    const response = await axios.put(
      API_SETTINGS_ENDPOINTS.updateSetting(type), { settings_value }, getRequestConfig()
    );
    console.log(response.data)
    return response.data;
  },
};

export default api;