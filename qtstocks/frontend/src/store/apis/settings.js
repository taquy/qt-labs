import axios from 'axios';
import { API_SETTINGS_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  fetchSettings: async ({ type }) => {
    const response = await axios.get(API_SETTINGS_ENDPOINTS.settings(type), getRequestConfig());
    return response.data;
  },
  saveSettings: async ({ type, setting_value }) => {
    const response = await axios.put(
      API_SETTINGS_ENDPOINTS.updateSetting(type), { setting_value }, getRequestConfig()
    );
    // console.log(response.data)
    return response.data;
  },
};

export default api;