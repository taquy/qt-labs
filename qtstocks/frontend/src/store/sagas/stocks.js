import * as effects from 'redux-saga/effects';
import {
  setAvailableStocks,
  setError,
  setLoading,
  clearError,
  setStocks,
  setFetchingStockStats,
  setExportedCsv,
  setExportedGraphPdf,
  setLoader,
  setExchanges,
  LoaderActions,
  MessageActions,
  setMessages
} from '../slices/stocks';

import { handleApiError } from '../utils';

import {
  FETCH_STOCKS,
  FETCH_AVAILABLE_STOCKS,
  FETCH_STOCK_DATA,
  REMOVE_AVAILABLE_STOCK,
  EXPORT_STOCK_DATA,
  EXPORT_GRAPH_PDF,
  PULL_STOCK_LIST,
  FETCH_EXCHANGES
} from '../actions/stocks';

import api from '../apis/stocks';
// Sagas
function* fetchExchangesSaga() {
  try {
    const response = yield effects.call(api.fetchExchanges);
    yield effects.put(setExchanges(response));
  } catch (error) {
    yield effects.put(setError('Failed to fetch exchanges'));
    yield effects.call(handleApiError, error, 'fetchExchangesSaga');
  }
}

function* pullStockListSaga() {
  try {
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_LIST, value: true }));
    setMessages({
      action: MessageActions.PULL_STOCK_LIST,
      message: 'Pulling stock list...',
    });
    const response = yield effects.call(api.pullStockList);
    yield effects.put(setMessages({
      action: MessageActions.PULL_STOCK_LIST,
      message: response,
    }));
    yield effects.call(fetchStocksSaga);
  } catch (error) {
    yield effects.put(setError('Failed to pull stock list'));
    yield effects.call(handleApiError, error, 'pullStockListSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_LIST, value: false }));
  }
}

function* exportGraphPdfSaga() {
  try {
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_GRAPH_PDF, value: true }));
    const response = yield effects.call(api.exportGraphPdf);
    yield effects.put(setExportedGraphPdf(response));
  } catch (error) {
    yield effects.put(setError('Failed to export graph PDF'));
    yield effects.call(handleApiError, error, 'exportGraphPdfSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_GRAPH_PDF, value: false }));
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

function* exportCsvSaga() {
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

function* fetchStocksSaga(action) {
  try {
    yield effects.put(clearError());
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STOCKS, value: true }));
    const stocks = yield effects.call(api.fetchStocks, action.payload.page, action.payload.per_page);
    yield effects.put(setStocks(stocks));
    yield effects.call(fetchExchangesSaga);
  } catch (error) {
    yield effects.put(setError('Failed to fetch stocks'));
    yield effects.call(handleApiError, error, 'fetchStocksSaga');
  } finally {
    yield effects.delay(1000);
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STOCKS, value: false }));
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
export function* stocksSaga() {
  yield effects.takeLatest(FETCH_STOCKS, fetchStocksSaga);
  yield effects.takeLatest(FETCH_AVAILABLE_STOCKS, fetchAvailableStocksSaga);
  yield effects.takeLatest(FETCH_STOCK_DATA, fetchStockDataSaga);
  yield effects.takeLatest(REMOVE_AVAILABLE_STOCK, removeAvailableStockSaga);
  yield effects.takeLatest(EXPORT_STOCK_DATA, exportCsvSaga);
  yield effects.takeLatest(EXPORT_GRAPH_PDF, exportGraphPdfSaga);
  yield effects.takeLatest(PULL_STOCK_LIST, pullStockListSaga);
  yield effects.takeLatest(FETCH_EXCHANGES, fetchExchangesSaga);
}
