import * as effects from 'redux-saga/effects';
import {
  setStats,
  setError,
  setStocks,
  setExportedCsv,
  setExportedGraphPdf,
  setLoader,
  setExchanges,
  LoaderActions,
  MessageActions,
  ErrorActions,
  setMessages,
  setPortfolios,
} from '../slices/stocks';

import { handleApiError } from '../utils';

import {
  FETCH_STOCKS,
  FETCH_STATS,
  PULL_STOCK_STATS,
  REMOVE_STATS,
  EXPORT_STOCK_DATA,
  EXPORT_GRAPH_PDF,
  PULL_STOCK_LIST,
  FETCH_EXCHANGES,
  SET_MESSAGE,
  FETCH_PORTFOLIOS,
  CREATE_PORTFOLIO,
} from '../actions/stocks';

import api from '../apis/stocks';
// Sagas
function* createPortfolioSaga(action) {
  try {
    const response = yield effects.call(api.createPortfolio, action.payload);
    yield effects.put(setPortfolios(response));
  } catch (error) {
    yield effects.call(handleApiError, error, 'createPortfolioSaga');
  }
}

function* fetchPortfoliosSaga() {
  try {
    const response = yield effects.call(api.fetchPortfolios);
    yield effects.put(setPortfolios(response));
  } catch (error) {
    yield effects.call(handleApiError, error, 'fetchPortfoliosSaga');
  }
}

function* setMessagesSaga(action) {
  yield effects.put(setMessages(action.payload));
}

function* fetchExchangesSaga() {
  try {
    const response = yield effects.call(api.fetchExchanges);
    yield effects.put(setExchanges(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to fetch exchanges',
    }));
    yield effects.call(handleApiError, error, 'fetchExchangesSaga');
  }
}

function* pullStockListSaga() {
  try {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: '',
    }));
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_LIST, value: true }));
    yield effects.put(setMessages({
      action: MessageActions.PULL_STOCK_LIST,
      message: 'Pulling stock list...',
    }));
    const response = yield effects.call(api.pullStockList);
    yield effects.put(setMessages({
      action: MessageActions.PULL_STOCK_LIST,
      message: response.message,
    }));
    yield effects.call(fetchStocksSaga);
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to pull stock list',
    }));
    yield effects.call(handleApiError, error, 'pullStockListSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_LIST, value: false }));
  }
}

function* exportGraphPdfSaga() {
  try {
    yield effects.put(setError({
      action: ErrorActions.STOCK_GRAPH,
      message: '',
    }));
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_GRAPH_PDF, value: true }));
    const response = yield effects.call(api.exportGraphPdf);
    yield effects.put(setExportedGraphPdf(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_GRAPH,
      message: 'Failed to export graph PDF',
    }));
    yield effects.call(handleApiError, error, 'exportGraphPdfSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_GRAPH_PDF, value: false }));
  }
}

function* removeStatsSaga(action) {
  try {
    yield effects.put(setError({
      action: ErrorActions.STOCK_TABLE,
      message: '',
    } ));
    yield effects.put(setLoader({ action: LoaderActions.REMOVE_STATS, value: true }));
    yield effects.call(api.removeStats, action.payload);
    yield effects.call(fetchStatsSaga);
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_TABLE,
      message: 'Failed to remove available stock',
    }));
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.REMOVE_STATS, value: false }));
  }
}

function* exportCsvSaga() {
  try {
    yield effects.put(setError({
      action: ErrorActions.STOCK_TABLE,
      message: '',
    } ));
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_STOCK_DATA, value: true }));
    const response = yield effects.call(api.exportCsv);
    yield effects.put(setExportedCsv(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_TABLE,
      message: 'Failed to export stock data',
    }));
    yield effects.call(handleApiError, error, 'exportCsvSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.EXPORT_STOCK_DATA, value: false }));
  }
}

function* pullStockStatsSaga(action) {
  try {
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_STATS, value: true }));
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: '',
    }));
    yield effects.call(api.pullStockStats, action.payload);
    yield effects.call(fetchStatsSaga);
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to pull stock stats',
    }));
    yield effects.call(handleApiError, error, 'pullStockStatsSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.PULL_STOCK_STATS, value: false }));
  }
}

function* fetchStocksSaga(action) {
  try {
    const query = action.payload;
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: '',
    }));
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STOCKS, value: true }));
    query["exchanges"] = query["exchanges"].join(',');
    const results = yield effects.call(api.fetchStocks, query);
    yield effects.put(setStocks({...results, refresh: query.refresh}));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to fetch stocks',
    }));
    yield effects.call(handleApiError, error, 'fetchStocksSaga');
  } finally {
    yield effects.delay(1000);
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STOCKS, value: false }));
  }
}

function* fetchStatsSaga() {
  try {
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STATS, value: true }));
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: '',
    } ));
    const stocks = yield effects.call(api.fetchStats);
    yield effects.put(setStats(stocks));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to fetch stats',
    }));
    yield effects.call(handleApiError, error, 'fetchStatsSaga');
  } finally {
    yield effects.put(setLoader({ action: LoaderActions.FETCH_STATS, value: false }));
  }
}

// Root Saga
export function* stocksSaga() {
  yield effects.takeLatest(FETCH_STOCKS, fetchStocksSaga);
  yield effects.takeLatest(FETCH_STATS, fetchStatsSaga);
  yield effects.takeLatest(PULL_STOCK_STATS, pullStockStatsSaga);
  yield effects.takeLatest(REMOVE_STATS, removeStatsSaga);
  yield effects.takeLatest(EXPORT_STOCK_DATA, exportCsvSaga);
  yield effects.takeLatest(EXPORT_GRAPH_PDF, exportGraphPdfSaga);
  yield effects.takeLatest(PULL_STOCK_LIST, pullStockListSaga);
  yield effects.takeLatest(FETCH_EXCHANGES, fetchExchangesSaga);
  yield effects.takeLatest(SET_MESSAGE, setMessagesSaga);
  yield effects.takeLatest(FETCH_PORTFOLIOS, fetchPortfoliosSaga);
  yield effects.takeLatest(CREATE_PORTFOLIO, createPortfolioSaga);
}
