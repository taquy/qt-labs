import * as effects from 'redux-saga/effects';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config';
import {
  setAvailableStocks,
  setChartData,
  setError,
  setLoading,
  setSettings,
  clearError,
  clearChartData
} from '../slices/stockGraphSlice';

// Action Types
export const FETCH_AVAILABLE_STOCKS = 'stockGraph/fetchAvailableStocks';
export const FETCH_SETTINGS = 'stockGraph/fetchSettings';
export const UPDATE_GRAPH = 'stockGraph/updateGraph';
export const SAVE_SETTINGS = 'stockGraph/saveSettings';

// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchSettings = () => ({ type: FETCH_SETTINGS });
export const updateGraph = (symbols, metric) => ({ type: UPDATE_GRAPH, payload: { symbols, metric } });
export const saveSettings = (stocks, metric) => ({ type: SAVE_SETTINGS, payload: { stocks, metric } });

// Helper function to get auth token
const getAuthToken = () => localStorage.getItem('token');

// Helper function to handle API errors
const handleApiError = (error, saga) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('isLoggedIn');
    window.location.href = '/login';
  }
  return saga;
}

// API calls
const api = {
  fetchAvailableStocks: async (token) => {
    const response = await axios.get(API_ENDPOINTS.stocksWithStats, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.data.stocks;
  },

  fetchSettings: async (token) => {
    const response = await axios.get(API_ENDPOINTS.settings, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.data.settings;
  },

  updateGraph: async (token, symbols, metric) => {
    const response = await axios.post(API_ENDPOINTS.updateGraph, {
      stocks: symbols,
      metric: metric
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.data;
  },

  saveSettings: async (token, stocks, metric) => {
    await axios.put(
      API_ENDPOINTS.updateSetting('stockGraph'),
      {
        value: {
          selectedSymbols: stocks.map(stock => stock.symbol),
          selectedMetric: metric
        }
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
  }
};

// Sagas
function* fetchAvailableStocksSaga() {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const stocks = yield effects.call(api.fetchAvailableStocks, token);
    yield effects.put(setAvailableStocks(stocks));
  } catch (error) {
    yield effects.put(setError('Failed to fetch available stocks'));
    yield effects.call(handleApiError, error, 'fetchAvailableStocksSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* fetchSettingsSaga() {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const settings = yield effects.call(api.fetchSettings, token);
    yield effects.put(setSettings(settings));
  } catch (error) {
    yield effects.put(setError('Failed to fetch settings'));
    yield effects.call(handleApiError, error, 'fetchSettingsSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* updateGraphSaga(action) {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const { symbols, metric } = action.payload;
    const response = yield effects.call(api.updateGraph, token, symbols, metric);
    
    // Generate colors for each bar
    const colors = response.data.map((_, index) => 
      `hsl(${(index * 360/response.data.length)}, 70%, 50%)`
    );

    const chartConfig = {
      labels: response.data.map(item => item.symbol),
      datasets: [{
        label: response.metric,
        data: response.data.map(item => item.value),
        backgroundColor: colors,
        borderColor: colors.map(color => color.replace('50%', '40%')),
        borderWidth: 1,
        borderRadius: 5,
        hoverBackgroundColor: colors.map(color => color.replace('50%', '60%')),
      }]
    };

    // Store only serializable data in Redux
    yield effects.put(setChartData({ 
      data: chartConfig,
      metric: response.metric
    }));
  } catch (error) {
    yield effects.put(setError('Failed to update graph'));
    yield effects.put(clearChartData());
    yield effects.call(handleApiError, error, 'updateGraphSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* saveSettingsSaga(action) {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');
    
    const { stocks, metric } = action.payload;
    yield effects.call(api.saveSettings, token, stocks, metric);
  } catch (error) {
    yield effects.put(setError('Failed to save settings'));
    yield effects.call(handleApiError, error, 'saveSettingsSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

// Root Saga
export function* stockGraphSaga() {
  yield effects.takeLatest(FETCH_AVAILABLE_STOCKS, fetchAvailableStocksSaga);
  yield effects.takeLatest(FETCH_SETTINGS, fetchSettingsSaga);
  yield effects.takeLatest(UPDATE_GRAPH, updateGraphSaga);
  yield effects.takeLatest(SAVE_SETTINGS, saveSettingsSaga);
} 