import axios from 'axios';
import { API_STOCK_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

// API calls
const api = {
  fetchStocks: async (page = 1, per_page = 20) => {
    const endpoint = API_STOCK_ENDPOINTS.stocks + `?page=${page}&per_page=${per_page}`;
    const response = await axios.get(endpoint, getRequestConfig());
    return response.data;
  },
  fetchExchanges: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.exchanges, getRequestConfig());
    return response.data;
  },
  fetchAvailableStocks: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.stocksWithStats, getRequestConfig());
    return response.data.stocks;
  },
  fetchStockData: async (payload) => {
    const response = await axios.post(API_STOCK_ENDPOINTS.fetchStockData, {
      symbols: payload.selectedStocks,
      loadLatestData: payload.loadLatestData
    }, getRequestConfig());
    return response.data.data;
  },
  removeAvailableStock: async (symbols) => {
    const response = await axios.post(API_STOCK_ENDPOINTS.removeAvailableStock, {
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
