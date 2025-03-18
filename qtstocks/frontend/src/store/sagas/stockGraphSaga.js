import * as effects from 'redux-saga/effects';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config';
import {
  setAvailableStocks,
  setError,
  setLoading,
  setSettings,
  clearError,
  setIsLoggedIn,
  setAuthToken,
  setStocks,
  setFetchingStockStats
} from '../slices/stockGraphSlice';

// Action Types
export const FETCH_STOCKS = 'stockGraph/fetchStocks';
export const FETCH_AVAILABLE_STOCKS = 'stockGraph/fetchAvailableStocks';
export const FETCH_SETTINGS = 'stockGraph/fetchSettings';
export const SAVE_SETTINGS = 'stockGraph/saveSettings';
export const FETCH_STOCK_DATA = 'stockGraph/fetchStockData';
export const LOGOUT = 'stockGraph/logout';
export const LOGIN = 'stockGraph/login';
export const GOOGLE_LOGIN = 'stockGraph/googleLogin';
export const REMOVE_AVAILABLE_STOCK = 'stockGraph/removeAvailableStock';
export const CHECK_IS_LOGGED_IN = 'stockGraph/checkIsLoggedIn';
// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchSettings = () => ({ type: FETCH_SETTINGS });
export const saveSettings = (stocks, metric) => ({ type: SAVE_SETTINGS, payload: { stocks, metric } });
export const login = (username, password) => ({ type: LOGIN, payload: { username, password } });
export const logout = () => ({ type: LOGOUT });
export const fetchStocks = () => ({ type: FETCH_STOCKS });
export const googleLogin = (token) => ({ type: GOOGLE_LOGIN, payload: { token } });
export const removeAvailableStock = (payload) => ({ type: REMOVE_AVAILABLE_STOCK, payload });
export const fetchStockData = (payload) => ({ type: FETCH_STOCK_DATA, payload });
export const checkIsLoggedIn = () => ({ type: CHECK_IS_LOGGED_IN });
// Helper function to handle API errors
const handleApiError = (error, saga) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('authToken');
    localStorage.removeItem('isLoggedIn');
    window.location.href = '/login';
  }
  return saga;
}

const getRequestConfig = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` },
  withCredentials: true
});

// API calls
const api = {
  fetchStocks: async () => {
    const response = await axios.get(API_ENDPOINTS.stocks, getRequestConfig());
    return response.data.stocks;
  },

  fetchAvailableStocks: async () => {
    const response = await axios.get(API_ENDPOINTS.stocksWithStats, getRequestConfig());
    return response.data.stocks;
  },
  fetchSettings: async () => {
    const response = await axios.get(API_ENDPOINTS.settings, getRequestConfig());
    return response.data.settings;
  },
  saveSettings: async (stocks, metric) => {
    const payload = {
      value: {
        selectedSymbols: stocks.map(stock => stock.symbol),
        selectedMetric: metric
      }
    };
    await axios.put(
      API_ENDPOINTS.updateSetting('stockGraph'), payload, getRequestConfig()
    );
  },
  fetchStockData: async (symbols) => {
    const response = await axios.post(API_ENDPOINTS.fetchStockData, {
      symbols: symbols
    }, getRequestConfig());
    return response.data.data;
  },
  logout: async () => {
    const response = await axios.post(API_ENDPOINTS.logout, {}, getRequestConfig());
    return response.data;
  },
  login: async (payload) => {
    const response = await axios.post(API_ENDPOINTS.login, payload);
    return response.data;
  },
  googleLogin: async (token) => {
    const response = await fetch(API_ENDPOINTS.googleLogin, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ token: token }),
    });
    return response.data;
  },
  removeAvailableStock: async (symbols) => {
    const response = await axios.post(API_ENDPOINTS.removeAvailableStock, {
      symbols: symbols
    }, getRequestConfig());
    return response.data;
  }
};


// Sagas
function* checkIsLoggedInSaga() {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const authToken = localStorage.getItem('authToken');
  if (isLoggedIn && authToken) {
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(authToken));
  } else {
    yield effects.put(setIsLoggedIn(false));
  }
}

function* removeAvailableStockSaga(action) {
  try {
    yield effects.call(api.removeAvailableStock, action.payload);
    yield effects.call(fetchAvailableStocksSaga);
  } catch (error) {
    yield effects.put(setError('Failed to remove available stock'));
  }
}

function* googleLoginSaga(action) {
  try {
    const response = yield effects.call(api.googleLogin, action.payload);
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(response.token));
  } catch (error) {
    yield effects.put(setError('Failed to login'));
  }
}

function* loginSaga(action) {
  try {
    const response = yield effects.call(api.login, action.payload);
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(response.token));
  } catch (error) {
    yield effects.put(setError('Failed to login'));
  }
}

function* logoutSaga() {
  try {
    yield effects.call(api.logout);
    localStorage.removeItem('authToken');
    localStorage.removeItem('isLoggedIn');
    delete axios.defaults.headers.common['Authorization'];
    yield effects.put(setIsLoggedIn(false));
  } catch (error) {
    yield effects.put(setError('Failed to logout'));
    yield effects.call(handleApiError, error, 'logoutSaga');
  }
}

function* fetchStockDataSaga(action) {
  try {
    yield effects.put(setFetchingStockStats(true));
    yield effects.put(clearError());
    yield effects.call(api.fetchStockData, action.payload);
    yield effects.call(fetchAvailableStocksSaga);
  } catch (error) {
    yield effects.put(setError('Failed to fetch stocks'));
    yield effects.call(handleApiError, error, 'fetchStockDataSaga');
  } finally {
    yield effects.put(setFetchingStockStats(false));
  }
}

function* fetchStocksSaga() {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const stocks = yield effects.call(api.fetchStocks);
    yield effects.put(setStocks(stocks));
  } catch (error) {
    yield effects.put(setError('Failed to fetch stocks'));
    yield effects.call(handleApiError, error, 'fetchStocksSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* fetchAvailableStocksSaga() {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const stocks = yield effects.call(api.fetchAvailableStocks);
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
    const settings = yield effects.call(api.fetchSettings);
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
    const { stocks, metric } = action.payload;
    yield effects.call(api.saveSettings, stocks, metric);
    yield effects.call(fetchSettingsSaga);
  } catch (error) {
    yield effects.put(setError('Failed to save settings'));
    yield effects.call(handleApiError, error, 'saveSettingsSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

// Root Saga
export function* stockGraphSaga() {
  yield effects.takeLatest(FETCH_STOCKS, fetchStocksSaga);
  yield effects.takeLatest(FETCH_AVAILABLE_STOCKS, fetchAvailableStocksSaga);
  yield effects.takeLatest(FETCH_SETTINGS, fetchSettingsSaga);
  yield effects.takeLatest(SAVE_SETTINGS, saveSettingsSaga);
  yield effects.takeLatest(FETCH_STOCK_DATA, fetchStockDataSaga);
  yield effects.takeLatest(LOGOUT, logoutSaga);
  yield effects.takeLatest(LOGIN, loginSaga);
  yield effects.takeLatest(GOOGLE_LOGIN, googleLoginSaga);
  yield effects.takeLatest(REMOVE_AVAILABLE_STOCK, removeAvailableStockSaga);
  yield effects.takeLatest(CHECK_IS_LOGGED_IN, checkIsLoggedInSaga);
}
