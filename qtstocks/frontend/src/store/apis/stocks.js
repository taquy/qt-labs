import axios from 'axios';
import { API_STOCK_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

// API calls
const api = {
  fetchStocks: async (payload) => {
    const query = new URLSearchParams(payload);
    const endpoint = API_STOCK_ENDPOINTS.stocks + `?${query.toString()}`;
    const response = await axios.get(endpoint, getRequestConfig());
    return response.data;
  },
  fetchExchanges: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.exchanges, getRequestConfig());
    return response.data;
  },
  fetchStats: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.stats, getRequestConfig());
    return response.data;
  },
  pullStockStats: async (payload) => {
    const response = await axios.post(API_STOCK_ENDPOINTS.pullStockStats, payload, getRequestConfig());
    return response.data.data;
  },
  removeStats: async (symbols) => {
    const response = await axios.post(API_STOCK_ENDPOINTS.removeStats, {
      symbols: symbols
    }, getRequestConfig());
    return response.data;
  },
  exportCsv: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.exportCsv, getRequestConfig());
    return response.data;
  },
  exportGraphPdf: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.exportGraphPdf, getRequestConfig());
    return response.data;
  },
  pullStockList: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.pullStockList, getRequestConfig());
    return response.data;
  },
};

export default api;
