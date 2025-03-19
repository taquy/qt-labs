import * as effects from 'redux-saga/effects';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config';
import {
  setAvailableStocks,
  setError,
  setLoading,
  clearError,
  setStocks,
  setFetchingStockStats,
} from '../slices/stockGraphSlice';
import { handleApiError, getRequestConfig } from '../utils';

// Action Types
export const FETCH_STOCKS = 'stockGraph/fetchStocks';
export const FETCH_AVAILABLE_STOCKS = 'stockGraph/fetchAvailableStocks';
export const FETCH_STOCK_DATA = 'stockGraph/fetchStockData';
export const REMOVE_AVAILABLE_STOCK = 'stockGraph/removeAvailableStock';

// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchStocks = () => ({ type: FETCH_STOCKS });
export const removeAvailableStock = (payload) => ({ type: REMOVE_AVAILABLE_STOCK, payload });
export const fetchStockData = (payload) => ({ type: FETCH_STOCK_DATA, payload });

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
  fetchStockData: async (payload) => {
    const response = await axios.post(API_ENDPOINTS.fetchStockData, {
      symbols: payload.selectedStocks,
      loadLatestData: payload.loadLatestData
    }, getRequestConfig());
    return response.data.data;
  },
  removeAvailableStock: async (symbols) => {
    const response = await axios.post(API_ENDPOINTS.removeAvailableStock, {
      symbols: symbols
    }, getRequestConfig());
    return response.data;
  }
};

// Sagas
function* removeAvailableStockSaga(action) {
  try {
    yield effects.call(api.removeAvailableStock, action.payload);
    yield effects.call(fetchAvailableStocksSaga);
  } catch (error) {
    yield effects.put(setError('Failed to remove available stock'));
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

// Root Saga
export function* stockGraphSaga() {
  yield effects.takeLatest(FETCH_STOCKS, fetchStocksSaga);
  yield effects.takeLatest(FETCH_AVAILABLE_STOCKS, fetchAvailableStocksSaga);
  yield effects.takeLatest(FETCH_STOCK_DATA, fetchStockDataSaga);
  yield effects.takeLatest(REMOVE_AVAILABLE_STOCK, removeAvailableStockSaga);
}
