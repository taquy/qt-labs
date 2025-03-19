import * as effects from 'redux-saga/effects';
import axios from 'axios';
import { API_STOCK_ENDPOINTS } from '../../config';
import {
  setAvailableStocks,
  setError,
  setLoading,
  clearError,
  setStocks,
  setFetchingStockStats,
  setExportedCsv,
  setExportedGraphPdf,
  setLoadingDownloadPdf,
} from '../slices/stockGraphSlice';
import { handleApiError, getRequestConfig } from '../utils';

// Action Types
export const FETCH_STOCKS = 'stockGraph/fetchStocks';
export const FETCH_AVAILABLE_STOCKS = 'stockGraph/fetchAvailableStocks';
export const FETCH_STOCK_DATA = 'stockGraph/fetchStockData';
export const REMOVE_AVAILABLE_STOCK = 'stockGraph/removeAvailableStock';
export const EXPORT_STOCK_DATA = 'stockGraph/exportStockData';
export const EXPORT_GRAPH_PDF = 'stockGraph/exportGraphPdf';

// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchStocks = () => ({ type: FETCH_STOCKS });
export const removeAvailableStock = (payload) => ({ type: REMOVE_AVAILABLE_STOCK, payload });
export const fetchStockData = (payload) => ({ type: FETCH_STOCK_DATA, payload });
export const exportCsv = () => ({ type: EXPORT_STOCK_DATA });
export const exportGraphPdf = () => ({ type: EXPORT_GRAPH_PDF });
// API calls
const api = {
  fetchStocks: async () => {
    const response = await axios.get(API_STOCK_ENDPOINTS.stocks, getRequestConfig());
    return response.data.stocks;
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
  }
};

// Sagas
function* exportGraphPdfSaga(action) {
  try {
    yield effects.put(setLoadingDownloadPdf(true));
    const response = yield effects.call(api.exportGraphPdf);
    yield effects.put(setExportedGraphPdf(response));
  } catch (error) {
    yield effects.put(setError('Failed to export graph PDF'));
    yield effects.call(handleApiError, error, 'exportGraphPdfSaga');
  } finally {
    yield effects.put(setLoadingDownloadPdf(false));
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

function* exportCsvSaga(action) {
  try {
    const response = yield effects.call(api.exportCsv);
    yield effects.put(setExportedCsv(response));
  } catch (error) {
    yield effects.put(setError('Failed to export stock data'));
    yield effects.call(handleApiError, error, 'exportCsvSaga');
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
  yield effects.takeLatest(EXPORT_STOCK_DATA, exportCsvSaga);
  yield effects.takeLatest(EXPORT_GRAPH_PDF, exportGraphPdfSaga);
}
