import * as effects from 'redux-saga/effects';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config';
import {
  setAvailableStocks,
  setError,
  setLoading,
  setSettings,
  clearError,
} from '../slices/stockGraphSlice';

// Action Types
export const FETCH_AVAILABLE_STOCKS = 'stockGraph/fetchAvailableStocks';
export const FETCH_SETTINGS = 'stockGraph/fetchSettings';
export const SAVE_SETTINGS = 'stockGraph/saveSettings';

// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchSettings = () => ({ type: FETCH_SETTINGS });
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

  saveSettings: async (token, stocks, metric) => {
    await axios.put(
      API_ENDPOINTS.updateSetting('stockGraph'),
      {
        value: {
          selectedSymbols: stocks.map(stock => stock.symbol),
          selectedMetric: metric
        }
      },
      { headers: { 'Authorization': `Bearer ${token}` } }
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
  yield effects.takeLatest(SAVE_SETTINGS, saveSettingsSaga);
}
