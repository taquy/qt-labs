import axios from 'axios';
import { API_SETTINGS_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  fetchSettings: async () => {
    const response = await axios.get(API_SETTINGS_ENDPOINTS.settings, getRequestConfig());
    return response.data.settings;
  },
  saveSettings: async (stocks, settings) => {
    const payload = {
      value: {
        selectedSymbols: stocks.map(stock => stock.symbol),
        ...settings
      }
    };
    await axios.put(
      API_SETTINGS_ENDPOINTS.updateSetting('stocks'), payload, getRequestConfig()
    );
  },
};

export default api;